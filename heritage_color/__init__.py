"""heritage_color —— 文物建筑色彩考证 / 颜料推演 / 修复决策工具包。

纯 Python 实现（仅标准库），无需安装第三方依赖。

快速使用：
    from heritage_color import auth_color, infer_pigment, decide_restoration

    # 1. 色彩考证
    r1 = auth_color(observed_hex="#6E2020", dynasty="清",
                    document_text="朱柱青檐")

    # 2. 颜料推演
    r2 = infer_pigment("#2E9070", dynasty="清")

    # 3. 修复决策
    r3 = decide_restoration(pigment="铅白", damage="变黑")

三个函数均返回 dataclass 对象，可调用 .to_dict() 转字典 / JSON。
"""

from .modules import (
    Evidence, AuthenticationResult, authenticate, parse_document,
    Formula, infer,
    DecisionResult, decide,
    StyleMatch, identify_style,
    ColorSwatch, extract_palette, dominant_color,
)

# 对外统一入口（函数别名，语义更直观）
auth_color = authenticate
infer_pigment = infer
decide_restoration = decide
identify_architecture_style = identify_style
extract_image_colors = extract_palette

__version__ = "1.1.0"
__all__ = [
    "auth_color", "infer_pigment", "decide_restoration",
    "identify_architecture_style", "extract_image_colors",
    "Evidence", "AuthenticationResult", "authenticate", "parse_document",
    "Formula", "infer",
    "DecisionResult", "decide",
    "StyleMatch", "identify_style",
    "ColorSwatch", "extract_palette", "dominant_color",
]
