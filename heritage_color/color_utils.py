"""色彩工具：sRGB / LAB 色空间转换与 CIEDE2000 色差计算。

仅依赖 Python 标准库，无需 numpy / opencv。
"""

import math

# D65 标准光源白点
_WHITE = (95.047, 100.0, 108.883)


def hex_to_rgb(hex_color: str):
    """#RRGGBB 或 RRGGBB -> (r, g, b) 0-255。"""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"非法颜色值: {hex_color}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    """(r, g, b) 0-255 -> #RRGGBB。"""
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, int(round(c)))) for c in rgb))


def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


def rgb_to_lab(rgb):
    """sRGB (0-255) -> CIE-L*ab。"""
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) * 100.0
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100.0
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100.0
    xr, yr, zr = x / _WHITE[0], y / _WHITE[1], z / _WHITE[2]

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(xr), f(yr), f(zr)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def lab_to_rgb(lab):
    """CIE-L*ab -> sRGB (0-255)。"""
    L, a, b = lab
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0

    def finv(t):
        t3 = t ** 3
        return t3 if t3 > 0.008856 else (t - 16 / 116) / 7.787

    x = _WHITE[0] * finv(fx) / 100.0
    y = _WHITE[1] * finv(fy) / 100.0
    z = _WHITE[2] * finv(fz) / 100.0
    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570
    return tuple(max(0, min(255, int(round(_linear_to_srgb(c))))) for c in (r, g, b))


def hex_to_lab(hex_color: str):
    return rgb_to_lab(hex_to_rgb(hex_color))


def lab_to_hex(lab) -> str:
    return rgb_to_hex(lab_to_rgb(lab))


def delta_e_cie2000(lab1, lab2) -> float:
    """两色的 CIEDE2000 色差，越小越接近（<1 为人眼难分辨）。"""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    C_bar = (C1 + C2) / 2.0
    G = 0.5 * (1 - math.sqrt((C_bar ** 7) / (C_bar ** 7 + 25 ** 7)))
    a1p = (1 + G) * a1
    a2p = (1 + G) * a2
    C1p = math.hypot(a1p, b1)
    C2p = math.hypot(a2p, b2)

    def hp(a, b):
        if a == 0 and b == 0:
            return 0.0
        h = math.degrees(math.atan2(b, a))
        return h if h >= 0 else h + 360

    h1p, h2p = hp(a1p, b1), hp(a2p, b2)
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)

    L_bar_p = (L1 + L2) / 2.0
    C_bar_p = (C1p + C2p) / 2.0
    if C1p * C2p == 0:
        h_bar_p = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        h_bar_p = (h1p + h2p) / 2.0
    elif h1p + h2p < 360:
        h_bar_p = (h1p + h2p + 360) / 2.0
    else:
        h_bar_p = (h1p + h2p - 360) / 2.0

    T = (1 - 0.17 * math.cos(math.radians(h_bar_p - 30))
         + 0.24 * math.cos(math.radians(2 * h_bar_p))
         + 0.32 * math.cos(math.radians(3 * h_bar_p + 6))
         - 0.20 * math.cos(math.radians(4 * h_bar_p - 63)))
    d_theta = 30 * math.exp(-(((h_bar_p - 275) / 25) ** 2))
    Rc = 2 * math.sqrt((C_bar_p ** 7) / (C_bar_p ** 7 + 25 ** 7))
    Sl = 1 + (0.015 * (L_bar_p - 50) ** 2) / math.sqrt(20 + (L_bar_p - 50) ** 2)
    Sc = 1 + 0.045 * C_bar_p
    Sh = 1 + 0.015 * C_bar_p * T
    Rt = -math.sin(math.radians(2 * d_theta)) * Rc

    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


def color_distance(hex1: str, hex2: str) -> float:
    """两个 #RRGGBB 颜色的 CIEDE2000 色差。"""
    return delta_e_cie2000(hex_to_lab(hex1), hex_to_lab(hex2))


def mix_lab_colors(labs, weights):
    """按权重在 LAB 空间混合多个颜色，返回 LAB。"""
    if len(labs) != len(weights) or not labs:
        raise ValueError("颜色与权重数量不一致或为空")
    total = sum(weights)
    if total <= 0:
        raise ValueError("权重和必须为正")
    return tuple(sum(l[i] * w for l, w in zip(labs, weights)) / total for i in range(3))
