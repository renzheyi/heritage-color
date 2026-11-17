"""三个业务功能模块。

- color_authentication：色彩考证
- pigment_inference：颜料推演
- restoration_decision：修复决策
"""

from .color_authentication import Evidence, AuthenticationResult, authenticate, parse_document
from .pigment_inference import Formula, infer
from .restoration_decision import DecisionResult, decide

__all__ = [
    "Evidence", "AuthenticationResult", "authenticate", "parse_document",
    "Formula", "infer",
    "DecisionResult", "decide",
]
