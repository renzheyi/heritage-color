"""三个业务功能模块。

- color_authentication：色彩考证
- pigment_inference：颜料推演
- restoration_decision：修复决策
- architecture_style：建筑风格识别
- image_color：上传图片识别现存残留色
- material_analysis：由图片识别材质 + 修复配材
- text_polish：文献描述智能润色（把口语转为考证书面语并补全色彩关键词）
"""

from .color_authentication import Evidence, AuthenticationResult, authenticate, parse_document
from .pigment_inference import Formula, infer
from .restoration_decision import DecisionResult, decide
from .architecture_style import StyleMatch, identify_style
from .image_color import ColorSwatch, extract_palette, dominant_color
from .material_analysis import MaterialMatch, RepairPlan, identify_material, recommend_repair
from .text_polish import polish_text

__all__ = [
    "Evidence", "AuthenticationResult", "authenticate", "parse_document",
    "Formula", "infer",
    "DecisionResult", "decide",
    "StyleMatch", "identify_style",
    "ColorSwatch", "extract_palette", "dominant_color",
    "MaterialMatch", "RepairPlan", "identify_material", "recommend_repair",
    "polish_text",
]
