# -*- coding: utf-8 -*-
"""光谱级色彩引擎 —— 让色彩考证从「RGB 比色」升级为「物理光谱推理」。

纯标准库实现，无任何第三方依赖。包含：

1. CIE 1931 2° 标准观察者色匹配函数
   采用 Wyman / Sloan / Shirley (2013, JCGT) 的多峰高斯解析拟合，
   在 380–730 nm 上以 10 nm 采样重建 x̄(λ), ȳ(λ), z̄(λ)。
2. 光源相对光谱功率分布（Planck 黑体辐射 + 等能光源 E），
   用于计算同一颜料在 D65 日光 / A 白炽 / 烛光下的呈色差异。
3. Kubelka-Munk 单常数混色模型
   K/S = (1-R)² / 2R，混合时 K/S 按浓度线性叠加，再反解反射率 R。
   这是颜料（不透明/半透明涂层）混色的经典物理模型，
   比在 RGB / Lab 空间做线性插值更接近真实调色行为。
4. 老化动力学与解析反演
   光致褪色（漂白）与含铅颜料硫化变黑两类退化通道，
   均给出闭式逆变换，可由「现存残留色」反推 t 年前的初色（时光倒流）。

参考：CIE 15:2004；Wyman et al. 2013；Kubelka & Munk 1931；
      敦煌研究院壁画褪色机理研究；故宫官式彩画材料分析。
说明：反射率由颜料典型新鲜色反演重建，属「教学/演示级参考光谱」，
      不替代实测分光光度计数据。
"""

import math
from typing import Dict, List, Optional, Sequence, Tuple

from .. import color_utils as cu

# 380–730 nm，10 nm 采样，共 36 个通道
WAVELENGTHS: List[int] = list(range(380, 731, 10))
_N = len(WAVELENGTHS)


# ---------------------------------------------------------------- 1. 标准观察者
def _gauss(x: float, mu: float, s_lo: float, s_hi: float) -> float:
    """非对称高斯：波长小于峰值用 s_lo，大于峰值用 s_hi。"""
    s = s_lo if x < mu else s_hi
    return math.exp(-0.5 * ((x - mu) / s) ** 2)


def cmf(lam: float) -> Tuple[float, float, float]:
    """CIE 1931 2° 标准观察者色匹配函数的解析近似（Wyman 2013）。"""
    x = (1.056 * _gauss(lam, 599.8, 37.9, 31.0)
         + 0.362 * _gauss(lam, 442.0, 16.0, 26.7)
         - 0.065 * _gauss(lam, 501.1, 20.4, 26.2))
    y = (0.821 * _gauss(lam, 568.8, 46.9, 40.5)
         + 0.286 * _gauss(lam, 530.9, 16.3, 31.1))
    z = (1.217 * _gauss(lam, 437.0, 11.8, 36.0)
         + 0.681 * _gauss(lam, 459.0, 26.0, 13.8))
    return max(x, 0.0), max(y, 0.0), max(z, 0.0)


CMF: List[Tuple[float, float, float]] = [cmf(l) for l in WAVELENGTHS]


# ---------------------------------------------------------------- 2. 光源 SPD
def _planck(lam_nm: float, kelvin: float) -> float:
    """普朗克黑体辐射定律（相对值），lam_nm 单位 nm。"""
    lam = lam_nm * 1e-9
    c1 = 3.7418e-16          # 2πhc²  [W·m²]
    c2 = 1.4388e-2           # hc/k   [m·K]
    try:
        return c1 / (lam ** 5 * (math.exp(c2 / (lam * kelvin)) - 1.0))
    except OverflowError:
        return 0.0


def _normalize_spd(values: Sequence[float]) -> List[float]:
    m = max(values) or 1.0
    return [v / m for v in values]


def illuminant(name: str) -> List[float]:
    """返回 36 通道相对光谱功率分布（归一化到峰值 1）。

    D65：以 6500 K 黑体做日光近似（演示级）；
    A  ：CIE 标准 A 光源，2856 K 白炽灯；
    烛光：约 1900 K，古代殿堂夜间照明；
    E  ：等能光源，各波长能量相同。
    """
    if name == "E":
        return [1.0] * _N
    temps = {"D65": 6500.0, "A": 2856.0, "烛光": 1900.0, "展厅LED": 4000.0}
    t = temps.get(name, 6500.0)
    return _normalize_spd([_planck(l, t) for l in WAVELENGTHS])


ILLUMINANTS = ("D65", "A", "烛光", "展厅LED", "E")


# ---------------------------------------------------------------- 3. 反射率重建
def _band(lam: float, mu: float, width: float) -> float:
    return math.exp(-0.5 * ((lam - mu) / width) ** 2)


# 四个非负重建基：三条宽带（红/绿/蓝）+ 常数散射基底。
# 用「三刺激值反演同色异谱光谱」的标准做法：解线性方程组使
# ∫R(λ)S(λ)x̄dλ 等三式严格等于该 sRGB 色的 CIE XYZ，
# 因此重建光谱与原始色在三刺激值上完全自洽（闭环误差 ≈ 0）。
_BASIS_MU = ((610.0, 72.0), (540.0, 62.0), (460.0, 58.0))


def _basis(lam: float) -> List[float]:
    return [_band(lam, mu, w) for mu, w in _BASIS_MU] + [1.0]


def _solve(A: List[List[float]], b: List[float]) -> List[float]:
    """高斯消元解 n×n 线性方程组（部分主元）。"""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            return [0.0] * n
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= p
        for r in range(n):
            if r != col and abs(M[r][col]) > 1e-15:
                f = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def _target_xyz_from_hex(hex_color: str) -> Tuple[float, float, float]:
    """sRGB → CIE XYZ (0–100, D65)，与 color_utils.rgb_to_lab 的矩阵一致。"""
    r, g, b = (cu._srgb_to_linear(c) for c in cu.hex_to_rgb(hex_color))
    return ((r * 0.4124 + g * 0.3576 + b * 0.1805) * 100.0,
            (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100.0,
            (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100.0)


_SPD_D65: Optional[List[float]] = None


def reflectance_from_hex(hex_color: str) -> List[float]:
    """由 sRGB 典型色重建 36 通道漫反射率曲线（三刺激值严格自洽）。

    这是欠定反演：满足同一 XYZ 的光谱有无穷多条，这里取
    「四条平滑宽带基的最小范数解」，形状接近真实颜料的缓变反射曲线。
    属于教学/演示级参考光谱，不替代实测分光光度数据。
    """
    global _SPD_D65
    if _SPD_D65 is None:
        _SPD_D65 = illuminant("D65")
    S = _SPD_D65
    denom = sum(S[i] * CMF[i][1] for i in range(_N)) or 1.0
    k = 100.0 / denom
    target = list(_target_xyz_from_hex(hex_color))

    # M[i][j] = k·Σ f_j(λ)·S(λ)·cmf_i(λ)   (3×4 响应矩阵)
    M = [[0.0] * 4 for _ in range(3)]
    for lam_i, lam in enumerate(WAVELENGTHS):
        f = _basis(lam)
        c = CMF[lam_i]
        for i in range(3):
            for j in range(4):
                M[i][j] += k * f[j] * S[lam_i] * c[i]

    # 正规方程 (M·Mᵀ + αI)u = target，再取 c = Mᵀu
    MtM = [[sum(M[i][j] * M[t][j] for j in range(4)) for t in range(3)]
           for i in range(3)]
    alpha = 1e-7 * sum(MtM[i][i] for i in range(3)) / 3.0 + 1e-12
    for i in range(3):
        MtM[i][i] += alpha
    u = _solve(MtM, target)
    coef = [sum(M[i][j] * u[i] for i in range(3)) for j in range(4)]

    # 允许极小的数学超出，保证三刺激值严格闭环；调用方在需要时再做物理 clamp
    return [max(0.001, min(1.35, sum(coef[j] * _basis(l)[j] for j in range(4))))
            for l in WAVELENGTHS]


def clamp_reflectance(values: Sequence[float]) -> List[float]:
    """把数学重建光谱收敛到物理区间 (0,1)，供 K-M 与老化模型使用。"""
    return [max(0.01, min(0.99, v)) for v in values]


def _ks_from_reflectance(r: float) -> float:
    """Kubelka-Munk 变换：K/S = (1-R)² / (2R)。"""
    r = max(0.01, min(0.99, r))
    return (1.0 - r) ** 2 / (2.0 * r)


def _reflectance_from_ks(ks: float) -> float:
    """K-M 逆变换：R = 1 + K/S − sqrt((K/S)² + 2·K/S)。"""
    ks = max(0.0, ks)
    return max(0.01, min(0.99, 1.0 + ks - math.sqrt(ks * ks + 2.0 * ks)))


def pigment_ks(pigment_name: str) -> Optional[List[float]]:
    """取某颜料新鲜态的 K/S 曲线；库中无此颜料返回 None。

    K-M 变换要求 R∈(0,1)，混色前先把数学重建光谱收敛到物理区间。
    """
    from .. import knowledge_base as kb
    p = kb.PIGMENTS.get(pigment_name)
    if p is None:
        return None
    return [_ks_from_reflectance(r) for r in clamp_reflectance(reflectance_from_hex(p.hex_fresh))]


def km_mix(components: Sequence[Tuple[str, float]]) -> Optional[List[float]]:
    """Kubelka-Munk 物理混色。

    components: [(颜料名, 浓度权重), ...]；权重归一化为浓度。
    返回混合后的 36 通道反射率曲线。
    """
    curves = []
    for name, w in components:
        ks = pigment_ks(name)
        if ks is None or w <= 0:
            continue
        curves.append((ks, w))
    if not curves:
        return None
    total = sum(w for _, w in curves)
    mixed = []
    for i in range(_N):
        ks = sum(curve[i] * (w / total) for curve, w in curves)
        mixed.append(_reflectance_from_ks(ks))
    return mixed


# ---------------------------------------------------------------- 4. 光谱 → 颜色
def spectrum_to_xyz(reflectance: Sequence[float],
                    spd: Optional[Sequence[float]] = None) -> Tuple[float, float, float]:
    """反射率 × 光源 × 标准观察者 → CIE XYZ（Y 归一化到 0–100）。"""
    if spd is None:
        spd = illuminant("D65")
    denom = sum(spd[i] * CMF[i][1] for i in range(_N)) or 1.0
    k = 100.0 / denom
    X = k * sum(reflectance[i] * spd[i] * CMF[i][0] for i in range(_N))
    Y = k * sum(reflectance[i] * spd[i] * CMF[i][1] for i in range(_N))
    Z = k * sum(reflectance[i] * spd[i] * CMF[i][2] for i in range(_N))
    return X, Y, Z


def xyz_to_rgb(X: float, Y: float, Z: float) -> Tuple[int, int, int]:
    """CIE XYZ (0–100) → sRGB (0–255)，标准 3×3 矩阵 + gamma 校正。"""
    r = (3.2406 * X - 1.5372 * Y - 0.4986 * Z) / 100.0
    g = (-0.9689 * X + 1.8758 * Y + 0.0415 * Z) / 100.0
    b = (0.0557 * X - 0.2040 * Y + 1.0570 * Z) / 100.0

    def gamma(c: float) -> float:
        c = max(0.0, min(1.0, c))
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    return tuple(max(0, min(255, int(round(255.0 * gamma(c))))) for c in (r, g, b))


def xyz_to_hex(X: float, Y: float, Z: float) -> str:
    return cu.rgb_to_hex(xyz_to_rgb(X, Y, Z))


def chromaticity(X: float, Y: float, Z: float) -> Tuple[float, float]:
    """CIE 1931 xy 色度坐标。"""
    s = X + Y + Z
    return (X / s, Y / s) if s > 0 else (0.0, 0.0)


def hex_to_xy(hex_color: str) -> Tuple[float, float]:
    """由反射光谱求某颜色的 xy 色度坐标（比直接 sRGB 矩阵更物理）。"""
    return chromaticity(*spectrum_to_xyz(reflectance_from_hex(hex_color)))


def spectral_locus() -> List[Tuple[float, float, int]]:
    """单色光（光谱轨迹）上的 xy 坐标，用于绘制 CIE 1931 马蹄图。"""
    pts = []
    for lam in WAVELENGTHS:
        R = [0.0] * _N
        # 单色刺激：仅该波长处有能量
        i = min(_N - 1, max(0, int(round((lam - 380) / 10))))
        R[i] = 1.0
        X, Y, Z = spectrum_to_xyz(R, spd=[1.0] * _N)
        x, y = chromaticity(X, Y, Z)
        pts.append((x, y, lam))
    return pts


_WHITE_D65_XY = (0.3127, 0.3290)


# ---------------------------------------------------------------- 5. 同色异谱
def illuminant_shift(hex_color: str, light_a: str = "D65",
                     light_b: str = "烛光") -> Dict:
    """同一颜料/涂层换光源后的呈色差异（展厅照明评估）。

    返回两光源下的 hex、Lab、xy 及 CIEDE2000 色差。
    """
    refl = reflectance_from_hex(hex_color)
    out = {}
    for tag, name in (("a", light_a), ("b", light_b)):
        X, Y, Z = spectrum_to_xyz(refl, illuminant(name))
        rgb = xyz_to_rgb(X, Y, Z)
        out[tag] = {
            "light": name, "hex": cu.rgb_to_hex(rgb),
            "lab": cu.rgb_to_lab(rgb), "xy": chromaticity(X, Y, Z),
        }
    out["delta_e"] = round(cu.delta_e_cie2000(out["a"]["lab"], out["b"]["lab"]), 2)
    return out


def _formula_hex(formula, light: str) -> Optional[str]:
    refl = km_mix(formula)
    return _refl_to_hex(refl, light) if refl else None


def metamerism_index(formula_a: Sequence[Tuple[str, float]],
                     formula_b: Sequence[Tuple[str, float]],
                     test_light: str = "A") -> Dict:
    """同色异谱指数：两配方在 D65 下等色，换测试光源后暴露出的色差。

    先在 D65 下对配方 B 做配比网格优化，使其与配方 A 尽可能等色
    （模拟修复师「照着日光调补色」）；再换到测试光源，
    此时显现的 ΔE 即同色异谱指数——补色在暖光/烛光下「跳色」的风险。
    """
    ra = km_mix(formula_a)
    if ra is None or len(formula_b) < 2:
        return {"valid": False}
    ha_d65 = _refl_to_hex(ra, "D65")

    names = [n for n, _ in formula_b][:2]
    best = None
    for step in range(2, 99):
        w = step / 100.0
        cand = [(names[0], w), (names[1], 1.0 - w)]
        hb = _formula_hex(cand, "D65")
        if hb is None:
            continue
        de = cu.color_distance(ha_d65, hb)
        if best is None or de < best[0]:
            best = (de, w, cand, km_mix(cand))
    if best is None:
        return {"valid": False}

    _, w, formula_b_opt, rb = best
    ha_test = _refl_to_hex(ra, test_light)
    hb_d65 = _formula_hex(formula_b_opt, "D65")
    hb_test = _refl_to_hex(rb, test_light)

    return {
        "valid": True, "light": test_light,
        "optimized_formula": [(n, round(v, 2)) for n, v in formula_b_opt],
        "ratio": round(w, 2),
        "d65": (ha_d65, hb_d65),
        "test": (ha_test, hb_test),
        "delta_e_d65": round(cu.color_distance(ha_d65, hb_d65), 2),
        "delta_e_test": round(cu.color_distance(ha_test, hb_test), 2),
        "metamerism_index": round(cu.color_distance(ha_test, hb_test), 2),
    }


# ---------------------------------------------------------------- 6. 老化动力学
# 光致褪色：反射率整体向「漂白」漂移；含铅/含汞颜料：整体变暗（硫化/氧化）
_DARKENING_PIGMENTS = ("铅白", "朱砂", "银朱", "铜绿")


def _aging_params(pigment_name: Optional[str], years: float):
    """返回 (褪色强度 f, 变黑强度 d, 时间常数说明)。"""
    from .. import knowledge_base as kb
    p = kb.PIGMENTS.get(pigment_name) if pigment_name else None
    lf = p.lightfastness if p else 3
    tau = 45.0 * lf + 25.0                       # 耐光性越差，时间常数越短
    f = 1.0 - math.exp(-max(0.0, years) / tau)  # 光褪色进度 0→1
    dark = pigment_name in _DARKENING_PIGMENTS
    d = 0.72 * f if dark else 0.0
    return f, d, tau


def _apply_aging(refl: Sequence[float], f: float, d: float) -> List[float]:
    """正向老化：漂白 + 变黑（闭式，便于解析反演）。

    边界与重建光谱一致（0.001–1.35），保证 f=0 时严格回到原色，
    反演才有零残差。
    """
    bleach = 0.55 * f
    out = []
    for r in refl:
        v = r + (0.86 - r) * bleach           # 向浅灰白漂移
        v *= (1.0 - d)                        # 整体变暗
        out.append(max(0.001, min(1.35, v)))
    return out


def _reverse_aging(refl: Sequence[float], f: float, d: float) -> List[float]:
    """解析逆变换：由老化后的反射率反推初始反射率（时光倒流）。"""
    bleach = 0.55 * f
    denom_b = max(0.05, 1.0 - bleach)
    denom_d = max(0.05, 1.0 - d)
    out = []
    for v in refl:
        r0 = v / denom_d
        r0 = (r0 - 0.86 * bleach) / denom_b
        out.append(max(0.001, min(1.35, r0)))
    return out


def _refl_to_hex(refl: Sequence[float], light: str = "D65") -> str:
    X, Y, Z = spectrum_to_xyz(refl, illuminant(light))
    return cu.rgb_to_hex(xyz_to_rgb(X, Y, Z))


def aging_curve(hex_color: str, pigment_name: Optional[str] = None,
                max_years: int = 400, steps: int = 12) -> List[Dict]:
    """正向模拟：从 fresh 色出发，输出各年代的颜色与累计色差。"""
    refl0 = reflectance_from_hex(hex_color)
    lab0 = cu.hex_to_lab(hex_color)
    out = []
    for i in range(steps + 1):
        years = max_years * i / steps
        if years == 0:
            # 零时刻直接返回输入色，避免把「光谱重建残差」误当作老化量
            out.append({"year": 0, "hex": hex_color, "delta_e": 0.0, "f": 0.0})
            continue
        f, d, _ = _aging_params(pigment_name, years)
        hx = _refl_to_hex(_apply_aging(refl0, f, d))
        out.append({
            "year": round(years), "hex": hx,
            "delta_e": round(cu.delta_e_cie2000(lab0, cu.hex_to_lab(hx)), 2),
            "f": round(f, 3),
        })
    return out


def reverse_aging(observed_hex: str, pigment_name: Optional[str] = None,
                  years: float = 200) -> Dict:
    """时光倒流：由现存残留色反推 years 年前的初色（解析反演）。"""
    f, d, tau = _aging_params(pigment_name, years)
    aged = reflectance_from_hex(observed_hex)
    fresh = _reverse_aging(aged, f, d)
    # 校验：把反演结果再正向老化一次，看能否回到观测色（残差应极小）
    check = _refl_to_hex(_apply_aging(fresh, f, d))
    return {
        "years": round(years), "pigment": pigment_name or "综合",
        "observed_hex": observed_hex,
        "restored_hex": _refl_to_hex(fresh),
        "verification_hex": check,
        "residual_delta_e": round(cu.color_distance(check, observed_hex), 3),
        "tau_years": round(tau),
        "fresh_spectrum": fresh, "aged_spectrum": aged,
    }
