"""模块五：上传图片识别现存残留色。

目标：用户上传一张文物彩画照片，自动提取画面中的主要残留色，
作为"现存残留色"输入，供后续色彩考证 / 颜料推演使用。

方法：用 Pillow 把图片缩放到合适尺寸，过滤掉近黑/近白的背景与阴影，
再按颜色量化（median-cut 精简版）聚类，统计各色簇的像素占比，
输出前 N 个主色及其占比。这是经典的主色提取算法，无需深度学习模型，
在 Streamlit Cloud 上开箱即用（Pillow 是 Streamlit 的既有依赖）。
"""

from dataclasses import dataclass, asdict
from typing import List, Tuple, BinaryIO, Union
import io

from PIL import Image

from .. import color_utils as cu


@dataclass
class ColorSwatch:
    hex: str               # 主色 #RRGGBB
    ratio: float           # 像素占比 0-1
    pixel_count: int       # 像素数

    def to_dict(self):
        return asdict(self)


def _is_valid_pixel(r: int, g: int, b: int,
                    dark_cut: int = 28, light_cut: int = 232) -> bool:
    """过滤过暗（阴影/描线）与过亮（高光/空白）的像素。"""
    if r < dark_cut and g < dark_cut and b < dark_cut:
        return False
    if r > light_cut and g > light_cut and b > light_cut:
        return False
    return True


def _quantize(pixels: List[Tuple[int, int, int]], n_colors: int,
              iterations: int = 12) -> List[Tuple[Tuple[int, int, int], int]]:
    """轻量 K-means 色彩聚类：把像素聚成 n_colors 个色簇。

    初始中心按亮度分位点选取，能较好分离明度不同的色块；随后迭代
    分配-更新。返回 [(代表色(取整), 该簇像素数), ...]，按像素数降序。
    """
    if not pixels:
        return []
    k = max(1, min(n_colors, len(set(pixels))))

    # 按亮度排序，取等距分位点作为初始中心
    ordered = sorted(pixels, key=lambda p: p[0] + p[1] + p[2])
    centers = []
    for i in range(k):
        idx = min(len(ordered) - 1, (2 * i + 1) * len(ordered) // (2 * k))
        centers.append(list(ordered[idx]))

    def nearest(p):
        best, best_d = 0, float("inf")
        for j, c in enumerate(centers):
            d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
            if d < best_d:
                best, best_d = j, d
        return best

    for _ in range(iterations):
        clusters = [[] for _ in range(k)]
        for p in pixels:
            clusters[nearest(p)].append(p)
        for j, cl in enumerate(clusters):
            if cl:
                centers[j] = [sum(p[c] for p in cl) / len(cl) for c in range(3)]

    out = []
    for j, cl in enumerate(clusters):
        if cl:
            out.append((tuple(round(v) for v in centers[j]), len(cl)))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def extract_palette(source: Union[str, BinaryIO, Image.Image],
                    top_n: int = 6,
                    max_size: int = 220) -> List[ColorSwatch]:
    """从图片提取主色（现存残留色候选）。

    参数:
        source: 图片路径、文件对象（如 st.file_uploader 返回对象）或 PIL Image
        top_n: 返回的主色数量
        max_size: 处理时缩放的最大边长（越大越准，越慢）

    返回:
        List[ColorSwatch]，按像素占比降序
    """
    if isinstance(source, Image.Image):
        img = source.convert("RGB")
    else:
        if hasattr(source, "seek"):
            source.seek(0)
        img = Image.open(source).convert("RGB")

    # 等比缩放，控制计算量
    img.thumbnail((max_size, max_size))
    pixels = []
    for r, g, b in img.getdata():
        if _is_valid_pixel(r, g, b):
            pixels.append((r, g, b))

    if not pixels:
        # 极端情况：全黑或全白，退回取图片中心色
        w, h = img.size
        r, g, b = img.getpixel((w // 2, h // 2))
        return [ColorSwatch(cu.rgb_to_hex((r, g, b)), 1.0, 1)]

    clusters = _quantize(pixels, top_n)
    total = sum(cnt for _, cnt in clusters)
    swatches = [
        ColorSwatch(
            hex=cu.rgb_to_hex(rgb),
            ratio=round(cnt / total, 4),
            pixel_count=cnt,
        )
        for rgb, cnt in clusters[:top_n]
    ]
    return swatches


def dominant_color(source: Union[str, BinaryIO, Image.Image],
                   max_size: int = 220) -> str:
    """便捷函数：返回图片中占比最高的一个主色 hex。"""
    swatches = extract_palette(source, top_n=6, max_size=max_size)
    return swatches[0].hex if swatches else "#6E2020"


if __name__ == "__main__":
    # 造一张测试图：70% 暗红 + 30% 石绿
    im = Image.new("RGB", (100, 100))
    im.putdata([(110, 32, 32)] * 7000 + [(46, 144, 112)] * 3000)
    for s in extract_palette(im, top_n=2):
        print(s.hex, f"{s.ratio:.0%}")
