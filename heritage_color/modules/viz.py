# -*- coding: utf-8 -*-
"""科技可视化组件 —— 纯 SVG 字符串，零依赖，可直接嵌入 Streamlit。

深色「数智中枢」视觉语言：墨青底 + 鎏金网格 + 朱砂/青蓝数据色，
与主站古风外壳形成「外古朴、内精密」的反差。

包含：
- chromaticity_diagram : CIE 1931 xy 色度图（真实光谱轨迹 + 色域扇区 + 点云 + 置信椭圆）
- spectrum_chart       : 380–730 nm 反射率 / 光源光谱曲线
- aging_timeline       : 老化时光轴（颜色条 + ΔE 曲线）
- convergence_chart    : 蒙特卡洛收敛曲线
- posterior_bars       : 贝叶斯后验概率水平条
- gauge                : 环形指标仪表
- flow_diagram         : 算法链路流程图
"""

import math
from typing import Dict, List, Optional, Sequence, Tuple

from . import spectral as sp
from .. import color_utils as cu

# ---------------------------------------------------------------- 配色
INK = "#0C1418"
PANEL = "#101C21"
GRID = "rgba(212,175,55,0.14)"
GOLD = "#D4AF37"
GOLD_SOFT = "#F3D98A"
CINNABAR = "#E0574A"
CYAN = "#57CFC3"
TEXT = "#DCE7DF"
MUTED = "#8FA8A2"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _frame(w: int, h: int, title: str = "", subtitle: str = "") -> Tuple[List[str], int]:
    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'style="width:100%;height:auto;display:block;background:{INK};'
        f'border:1px solid rgba(212,175,55,.35);border-radius:6px;">',
        f'<defs>'
        f'<radialGradient id="gvGlow"><stop offset="0%" stop-color="{GOLD}" stop-opacity=".55"/>'
        f'<stop offset="100%" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="gvFade" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{CYAN}" stop-opacity=".28"/>'
        f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>'
        f'</defs>',
        f'<rect width="{w}" height="{h}" fill="{PANEL}"/>',
    ]
    y = 0
    if title:
        head += [
            f'<text x="18" y="28" fill="{GOLD_SOFT}" font-size="15" '
            f'font-family="Georgia,serif" letter-spacing="1.5">{_esc(title)}</text>',
            f'<line x1="18" y1="38" x2="{w - 18}" y2="38" stroke="{GRID}" stroke-width="1"/>',
        ]
        y = 38
    if subtitle:
        head.append(f'<text x="18" y="{y + 18}" fill="{MUTED}" font-size="11" '
                    f'font-family="sans-serif">{_esc(subtitle)}</text>')
    return head, y


def _wavelength_rgb(wl: float) -> str:
    """单色光波长 → 近似 sRGB（Dan Bruton 经典分段近似），用于色度图填色。"""
    if wl < 440:
        r, g, b = -(wl - 440) / 60.0, 0.0, 1.0
    elif wl < 490:
        r, g, b = 0.0, (wl - 440) / 50.0, 1.0
    elif wl < 510:
        r, g, b = 0.0, 1.0, -(wl - 510) / 20.0
    elif wl < 580:
        r, g, b = (wl - 510) / 70.0, 1.0, 0.0
    elif wl < 645:
        r, g, b = 1.0, -(wl - 645) / 65.0, 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0
    # 两端视见函数衰减
    if wl < 420:
        f = 0.35 + 0.65 * (wl - 380) / 40.0
    elif wl > 700:
        f = 0.35 + 0.65 * (780 - wl) / 80.0
    else:
        f = 1.0
    f = max(0.0, min(1.0, f))
    return cu.rgb_to_hex(tuple(int(255 * max(0.0, min(1.0, c * f))) for c in (r, g, b)))


# ---------------------------------------------------------------- 1. CIE 色度图
def chromaticity_diagram(observed_hex: Optional[str] = None,
                         target_hex: Optional[str] = None,
                         cloud_hexes: Optional[Sequence[str]] = None,
                         ellipse: Optional[Dict] = None,
                         extra_points: Optional[Sequence[Tuple[str, str, str]]] = None,
                         width: int = 680, height: int = 452) -> str:
    """CIE 1931 xy 色度图：光谱轨迹 + 色域扇区 + 数据点 + 置信椭圆。"""
    pad_l, pad_r, pad_t, pad_b = 52, 20, 62, 44
    pw, ph = width - pad_l - pad_r, height - pad_t - pad_b
    xmin, xmax, ymin, ymax = 0.0, 0.76, 0.0, 0.86

    def PX(x): return pad_l + (x - xmin) / (xmax - xmin) * pw
    def PY(y): return pad_t + (ymax - y) / (ymax - ymin) * ph

    out, _ = _frame(width, height, "CIE 1931 · 色度坐标图",
                    "2° Standard Observer · 光谱轨迹 / 色域 / 观测点 / 后验点云")
    locus = sp.spectral_locus()
    white = sp._WHITE_D65_XY

    # 网格与刻度
    for gx in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        out.append(f'<line x1="{PX(gx):.1f}" y1="{PY(0):.1f}" x2="{PX(gx):.1f}" '
                   f'y2="{PY(ymax):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{PX(gx):.1f}" y="{PY(0) + 16}" fill="{MUTED}" '
                   f'font-size="10" text-anchor="middle" font-family="sans-serif">{gx:.1f}</text>')
    for gy in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
        out.append(f'<line x1="{PX(0):.1f}" y1="{PY(gy):.1f}" x2="{PX(xmax):.1f}" '
                   f'y2="{PY(gy):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{PX(0) - 9}" y="{PY(gy) + 3:.1f}" fill="{MUTED}" '
                   f'font-size="10" text-anchor="end" font-family="sans-serif">{gy:.1f}</text>')

    # 色域扇区：白点与光谱轨迹相邻点组成的三角形，按波长着色
    for i in range(len(locus) - 1):
        x1, y1, l1 = locus[i]
        x2, y2, l2 = locus[i + 1]
        col = _wavelength_rgb((l1 + l2) / 2.0)
        out.append(f'<polygon points="{PX(white[0]):.1f},{PY(white[1]):.1f} '
                   f'{PX(x1):.1f},{PY(y1):.1f} {PX(x2):.1f},{PY(y2):.1f}" '
                   f'fill="{col}" fill-opacity="0.42"/>')
    # 紫红边界（连接 380 与 730 两端）
    x1, y1, _ = locus[0]
    x2, y2, _ = locus[-1]
    out.append(f'<polygon points="{PX(white[0]):.1f},{PY(white[1]):.1f} '
               f'{PX(x1):.1f},{PY(y1):.1f} {PX(x2):.1f},{PY(y2):.1f}" '
               f'fill="#8B4A8F" fill-opacity="0.30"/>')

    # 光谱轨迹轮廓 + 波长标注
    pts = " ".join(f"{PX(x):.1f},{PY(y):.1f}" for x, y, _ in locus)
    out.append(f'<polyline points="{pts} {PX(x1):.1f},{PY(y1):.1f}" fill="none" '
               f'stroke="{GOLD}" stroke-width="1.6" stroke-opacity="0.85"/>')
    for x, y, lam in locus:
        if lam % 50 == 0 or lam in (380, 730):
            out.append(f'<circle cx="{PX(x):.1f}" cy="{PY(y):.1f}" r="2" fill="{GOLD_SOFT}"/>')
            out.append(f'<text x="{PX(x) + 5:.1f}" y="{PY(y) - 4:.1f}" fill="{GOLD_SOFT}" '
                       f'font-size="9" font-family="sans-serif">{lam}</text>')

    # 后验点云
    if cloud_hexes:
        for hx in cloud_hexes:
            try:
                cx, cy = sp.hex_to_xy(hx)
                out.append(f'<circle cx="{PX(cx):.1f}" cy="{PY(cy):.1f}" r="1.5" '
                           f'fill="{CYAN}" fill-opacity="0.30"/>')
            except Exception:
                continue

    # 置信椭圆（a*b* 平面投影的示意，映射到 xy 邻近区域）
    if ellipse and target_hex:
        tx, ty = sp.hex_to_xy(target_hex)
        rx = min(0.055, ellipse.get("rx", 3.0) * 0.0032)
        ry = min(0.045, ellipse.get("ry", 3.0) * 0.0026)
        out.append(f'<ellipse cx="{PX(tx):.1f}" cy="{PY(ty):.1f}" '
                   f'rx="{rx * pw / (xmax - xmin):.1f}" ry="{ry * ph / (ymax - ymin):.1f}" '
                   f'fill="none" stroke="{CYAN}" stroke-width="1.3" '
                   f'stroke-dasharray="4 3" stroke-opacity="0.85"/>')

    # 观测点 → 初色点 的推理连线
    if observed_hex and target_hex:
        ox, oy = sp.hex_to_xy(observed_hex)
        tx, ty = sp.hex_to_xy(target_hex)
        out.append(f'<line x1="{PX(ox):.1f}" y1="{PY(oy):.1f}" x2="{PX(tx):.1f}" '
                   f'y2="{PY(ty):.1f}" stroke="{GOLD_SOFT}" stroke-width="1.4" '
                   f'stroke-dasharray="5 4" stroke-opacity="0.8"/>')

    # 额外标注点
    for label, hx, color in (extra_points or []):
        try:
            x, y = sp.hex_to_xy(hx)
            out.append(f'<circle cx="{PX(x):.1f}" cy="{PY(y):.1f}" r="5" fill="{color}" '
                       f'stroke="{INK}" stroke-width="1.5"/>')
            out.append(f'<text x="{PX(x) + 9:.1f}" y="{PY(y) + 4:.1f}" fill="{TEXT}" '
                       f'font-size="10" font-family="sans-serif">{_esc(label)}</text>')
        except Exception:
            continue

    # 主点：观测色 / 考证初色
    for label, hx, color in (("观测", observed_hex, CINNABAR), ("初色", target_hex, GOLD_SOFT)):
        if not hx:
            continue
        x, y = sp.hex_to_xy(hx)
        out.append(f'<circle cx="{PX(x):.1f}" cy="{PY(y):.1f}" r="16" fill="url(#gvGlow)"/>')
        out.append(f'<circle cx="{PX(x):.1f}" cy="{PY(y):.1f}" r="6" fill="{color}" '
                   f'stroke="{INK}" stroke-width="2"/>')
        out.append(f'<text x="{PX(x) + 10:.1f}" y="{PY(y) - 8:.1f}" fill="{color}" '
                   f'font-size="11" font-family="sans-serif">{label} {hx}</text>')

    # D65 白点
    out.append(f'<path d="M {PX(white[0]) - 5:.1f} {PY(white[1]):.1f} h 10 '
               f'M {PX(white[0]):.1f} {PY(white[1]) - 5:.1f} v 10" '
               f'stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.9"/>')
    out.append(f'<text x="{PX(white[0]) + 9:.1f}" y="{PY(white[1]) + 4:.1f}" '
               f'fill="#FFFFFF" font-size="9" font-family="sans-serif">D65</text>')

    # 轴标题与图例
    out.append(f'<text x="{pad_l + pw / 2:.1f}" y="{height - 8}" fill="{MUTED}" '
               f'font-size="10" text-anchor="middle" font-family="sans-serif">x 色度坐标</text>')
    out.append(f'<text x="14" y="{pad_t + ph / 2:.1f}" fill="{MUTED}" font-size="10" '
               f'text-anchor="middle" font-family="sans-serif" '
               f'transform="rotate(-90 14 {pad_t + ph / 2:.1f})">y 色度坐标</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 2. 光谱曲线
def spectrum_chart(curves: Sequence[Tuple[str, Sequence[float], str]],
                   title: str = "光谱反射率 · 380–730 nm",
                   subtitle: str = "36 通道 · Kubelka-Munk 重建 / 光源相对功率",
                   width: int = 680, height: int = 286,
                   y_max: float = 1.0) -> str:
    pad_l, pad_r, pad_t, pad_b = 46, 18, 62, 40
    pw, ph = width - pad_l - pad_r, height - pad_t - pad_b
    out, _ = _frame(width, height, title, subtitle)

    def PX(i): return pad_l + i / (sp._N - 1) * pw
    def PY(v): return pad_t + ph - max(0.0, min(y_max, v)) / y_max * ph

    for gy in (0.0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<line x1="{pad_l}" y1="{PY(gy):.1f}" x2="{pad_l + pw}" '
                   f'y2="{PY(gy):.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l - 8}" y="{PY(gy) + 3:.1f}" fill="{MUTED}" '
                   f'font-size="9" text-anchor="end" font-family="sans-serif">{gy:.2f}</text>')
    for wl in range(400, 731, 50):
        i = int((wl - 380) / 10)
        if 0 <= i < sp._N:
            out.append(f'<line x1="{PX(i):.1f}" y1="{pad_t}" x2="{PX(i):.1f}" '
                       f'y2="{pad_t + ph}" stroke="{GRID}" stroke-width="1"/>')
            out.append(f'<text x="{PX(i):.1f}" y="{pad_t + ph + 15}" fill="{MUTED}" '
                       f'font-size="9" text-anchor="middle" font-family="sans-serif">{wl}</text>')

    for idx, (label, values, color) in enumerate(curves):
        pts = " ".join(f"{PX(i):.1f},{PY(v):.1f}" for i, v in enumerate(values))
        if idx == 0:
            out.append(f'<polygon points="{pad_l},{pad_t + ph} {pts} {pad_l + pw},{pad_t + ph}" '
                       f'fill="url(#gvFade)"/>')
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                   f'stroke-width="2.2" stroke-linejoin="round"/>')
        # 图例：置于标题行右侧，自右向左排布，避免与副标题/曲线重叠
        lx = width - 20 - (len(curves) - idx) * 138
        out.append(f'<rect x="{lx}" y="21" width="12" height="3" fill="{color}"/>')
        out.append(f'<text x="{lx + 17}" y="25" fill="{TEXT}" font-size="10" '
                   f'font-family="sans-serif">{_esc(label)}</text>')

    out.append(f'<text x="{pad_l + pw / 2:.1f}" y="{height - 6}" fill="{MUTED}" '
               f'font-size="10" text-anchor="middle" font-family="sans-serif">波长 λ / nm</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 3. 老化时光轴
def aging_timeline(curve: Sequence[Dict], width: int = 680,
                   height: int = 236) -> str:
    pad_l, pad_r, pad_t = 28, 28, 62
    pw = width - pad_l - pad_r
    out, _ = _frame(width, height, "老化动力学 · 时光倒流反演",
                    "光致褪色 / 硫化变黑双通道 · 解析逆变换重建初色")
    if not curve:
        return "".join(out + ['</svg>'])

    years = [c["year"] for c in curve]
    ymax = max(years) or 1
    bar_y, bar_h = pad_t + 8, 40
    # 颜色条
    for i, c in enumerate(curve):
        x0 = pad_l + (years[i] / ymax) * pw
        x1 = pad_l + ((years[i + 1] if i + 1 < len(curve) else years[i] + ymax / len(curve)) / ymax) * pw
        out.append(f'<rect x="{x0:.1f}" y="{bar_y}" width="{max(2, x1 - x0):.1f}" '
                   f'height="{bar_h}" fill="{c["hex"]}"/>')
    out.append(f'<rect x="{pad_l}" y="{bar_y}" width="{pw}" height="{bar_h}" '
               f'fill="none" stroke="{GOLD}" stroke-width="1" stroke-opacity="0.6"/>')

    # ΔE 曲线
    chart_y, chart_h = bar_y + bar_h + 26, 74
    demax = max(c["delta_e"] for c in curve) or 1.0
    def PY(v): return chart_y + chart_h - (v / demax) * chart_h
    pts = " ".join(f"{pad_l + (years[i] / ymax) * pw:.1f},{PY(c['delta_e']):.1f}"
                   for i, c in enumerate(curve))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{CYAN}" stroke-width="2"/>')
    for i, c in enumerate(curve):
        x = pad_l + (years[i] / ymax) * pw
        out.append(f'<circle cx="{x:.1f}" cy="{PY(c["delta_e"]):.1f}" r="2.6" fill="{CYAN}"/>')
        out.append(f'<line x1="{x:.1f}" y1="{chart_y + chart_h}" x2="{x:.1f}" '
                   f'y2="{chart_y + chart_h + 5}" stroke="{MUTED}"/>')
        out.append(f'<text x="{x:.1f}" y="{chart_y + chart_h + 18}" fill="{MUTED}" '
                   f'font-size="9" text-anchor="middle" font-family="sans-serif">{c["year"]}a</text>')
    out.append(f'<text x="{pad_l}" y="{chart_y - 6}" fill="{MUTED}" font-size="10" '
               f'font-family="sans-serif">累计色差 ΔE00</text>')
    out.append(f'<text x="{pad_l}" y="{bar_y - 6}" fill="{MUTED}" font-size="10" '
               f'font-family="sans-serif">初色 → 现存</text>')
    out.append(f'<text x="{pad_l + pw}" y="{bar_y - 6}" fill="{GOLD_SOFT}" font-size="10" '
               f'text-anchor="end" font-family="sans-serif">现存 {curve[-1]["hex"]}</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 4. 收敛曲线
def convergence_chart(points: Sequence[Dict], width: int = 330,
                      height: int = 168) -> str:
    out, _ = _frame(width, height, "蒙特卡洛收敛", "后验稳定度 · 每 100 次采样")
    if len(points) < 2:
        return "".join(out + ['</svg>'])
    pad_l, pad_t, pw, ph = 38, 72, width - 56, height - 98
    xs = [p["n"] for p in points]
    xmax = max(xs) or 1
    vals = [p["top_probability"] for p in points]
    lo, hi = min(vals + [0.0]), max(vals + [1.0])
    span = max(0.05, hi - lo)
    pts = " ".join(f"{pad_l + (x / xmax) * pw:.1f},{pad_t + ph - (v - lo) / span * ph:.1f}"
                   for x, v in zip(xs, vals))
    for gy in (lo, (lo + hi) / 2, hi):
        y = pad_t + ph - (gy - lo) / span * ph
        out.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + pw}" y2="{y:.1f}" '
                   f'stroke="{GRID}"/>')
        out.append(f'<text x="{pad_l - 6}" y="{y + 3:.1f}" fill="{MUTED}" font-size="9" '
                   f'text-anchor="end" font-family="sans-serif">{gy:.2f}</text>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="{CYAN}" stroke-width="2"/>')
    out.append(f'<text x="{pad_l}" y="{height - 10}" fill="{MUTED}" font-size="9" '
               f'font-family="sans-serif">0</text>')
    out.append(f'<text x="{pad_l + pw}" y="{height - 10}" fill="{MUTED}" font-size="9" '
               f'text-anchor="end" font-family="sans-serif">N={xmax}</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 5. 后验条形
def posterior_bars(rows: Sequence[Dict], width: int = 330,
                   height: int = 190) -> str:
    out, _ = _frame(width, height, "贝叶斯后验分布", "P(候选 | 色差 · 朝代先验 · 文献证据)")
    if not rows:
        return "".join(out + ['</svg>'])
    top = 58
    for i, r in enumerate(rows[:5]):
        y = top + i * 25
        p = float(r.get("posterior", 0))
        label = str(r.get("name", ""))[:8]
        out.append(f'<text x="14" y="{y + 10}" fill="{TEXT}" font-size="10" '
                   f'font-family="sans-serif">{_esc(label)}</text>')
        out.append(f'<rect x="86" y="{y}" width="{width - 130}" height="12" '
                   f'fill="rgba(212,175,55,.10)" rx="2"/>')
        out.append(f'<rect x="86" y="{y}" width="{max(2, (width - 130) * p):.1f}" '
                   f'height="12" fill="{GOLD if i == 0 else CYAN}" rx="2" opacity="{0.95 if i == 0 else 0.65}"/>')
        out.append(f'<text x="{width - 16}" y="{y + 10}" fill="{GOLD_SOFT}" font-size="10" '
                   f'text-anchor="end" font-family="sans-serif">{p * 100:.1f}%</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 6. 环形仪表
def gauge(value: float, label: str, sub: str = "", size: int = 168,
          color: str = GOLD) -> str:
    r, cx, cy = size * 0.36, size / 2, size / 2
    circ = 2 * math.pi * r
    v = max(0.0, min(1.0, value))
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'style="width:100%;max-width:{size}px;height:auto;display:block;">',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="rgba(212,175,55,.14)" stroke-width="9"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
        f'stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{circ * v:.1f} {circ:.1f}" '
        f'transform="rotate(-90 {cx} {cy})"/>',
        f'<text x="{cx}" y="{cy + 2}" fill="{GOLD_SOFT}" font-size="23" '
        f'text-anchor="middle" font-family="Georgia,serif">{v * 100:.0f}%</text>',
        f'<text x="{cx}" y="{cy + 22}" fill="{MUTED}" font-size="10" '
        f'text-anchor="middle" font-family="sans-serif">{_esc(label)}</text>',
    ]
    if sub:
        out.append(f'<text x="{cx}" y="{size - 6}" fill="{MUTED}" font-size="9" '
                   f'text-anchor="middle" font-family="sans-serif">{_esc(sub)}</text>')
    out.append('</svg>')
    return "".join(out)


# ---------------------------------------------------------------- 7. 算法链路
def flow_diagram(steps: Sequence[Tuple[str, str]], width: int = 680,
                 height: int = 150) -> str:
    out, _ = _frame(width, height, "推理链路 · 从光子到决策", "6 阶段可解释流水线")
    n = len(steps)
    pad, gap = 18, 12
    bw = (width - pad * 2 - gap * (n - 1)) / n
    for i, (title, desc) in enumerate(steps):
        x = pad + i * (bw + gap)
        y = 62
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="58" rx="4" '
                   f'fill="rgba(87,207,195,.07)" stroke="rgba(212,175,55,.38)"/>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{y + 22}" fill="{GOLD_SOFT}" '
                   f'font-size="11" text-anchor="middle" font-family="sans-serif">{_esc(title)}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{y + 40}" fill="{MUTED}" '
                   f'font-size="9" text-anchor="middle" font-family="sans-serif">{_esc(desc)}</text>')
        if i < n - 1:
            ax = x + bw + 1
            out.append(f'<path d="M {ax:.1f} {y + 29} l {gap - 3} 0 m -4 -3 l 4 3 l -4 3" '
                       f'fill="none" stroke="{GOLD}" stroke-width="1.2" opacity="0.8"/>')
    out.append('</svg>')
    return "".join(out)
