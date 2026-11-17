"""三个业务功能模块。

- color_authentication：色彩考证
- pigment_inference：颜料推演
- restoration_decision：修复决策
- architecture_style：建筑风格识别
- image_color：上传图片识别现存残留色
"""

from .color_authentication import Evidence, AuthenticationResult, authenticate, parse_document
from .pigment_inference import Formula, infer
from .restoration_decision import DecisionResult, decide
from .architecture_style import StyleMatch, identify_style
from .image_color import ColorSwatch, extract_palette, dominant_color

__all__ = [
    "Evidence", "AuthenticationResult", "authenticate", "parse_document",
    "Formula", "infer",
    "DecisionResult", "decide",
    "StyleMatch", "identify_style",
    "ColorSwatch", "extract_palette", "dominant_color",
]
