"""模块一：色彩考证。

目标：根据"现存残留色 / 光谱测色 + 文献记载 + 朝代风格"等多源证据，
推断文物彩画在历史原初状态下的色彩，并给出置信度与依据。

方法：把每条证据表示为"候选色 + 权重"，在 CIE-Lab 感知空间做加权融合，
得到推断原始色；再用知识库里的颜料老化规律反向校验（推断色应能由某
种颜料的"新鲜态"解释，而现存色应接近其"老化态"）。
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

from .. import color_utils as cu
from .. import knowledge_base as kb


@dataclass
class Evidence:
    """一条色彩证据。"""
    source: str        # 来源：如"现存痕迹实测""文献《XXX》""XRF 光谱"
    hex_color: str     # 该证据指向的颜色
    weight: float = 1.0  # 可信度权重


@dataclass
class AuthenticationResult:
    original_hex: str              # 推断的原始色
    observed_hex: Optional[str]    # 输入的现存色
    dynasty: str
    confidence: float              # 0-1 综合置信度
    matched_pigments: List[Dict]   # 可能用到的颜料（新鲜态匹配）
    evidence_used: List[Dict]      # 参与的证据及权重
    reasoning: str                 # 推理说明

    def to_dict(self):
        return asdict(self)


# 文献关键词 -> 色彩线索（简化的"文献解析"规则）
_TEXT_COLOR_HINTS = {
    "朱": "#A4272B", "丹": "#C1352C", "赤": "#A4272B", "红": "#A4272B",
    "青": "#1B6FA8", "蓝": "#274C8C", "碧": "#2E9070", "绿": "#2E9070",
    "黄": "#E3B21E", "金": "#E3B21E", "白": "#F2EFE6", "素": "#FAF8F0",
    "黑": "#1C1B1A", "墨": "#1C1B1A", "赭": "#9A5B3E",
}


def parse_document(text: str) -> List[Evidence]:
    """从文献描述文本中抽取色彩证据（关键词匹配 prototype）。

    例："檐下青绿彩画，朱柱，间以金线" -> 青、绿、朱、金 四条证据。
    """
    found = []
    for char, color in _TEXT_COLOR_HINTS.items():
        if char in text:
            found.append(Evidence(f"文献关键词『{char}』", color, 0.8))
    return found


def authenticate(observed_hex: Optional[str] = None,
                 dynasty: Optional[str] = None,
                 document_text: Optional[str] = None,
                 extra_evidence: Optional[List[Evidence]] = None,
                 top_k: int = 3) -> AuthenticationResult:
    """执行色彩考证。

    参数:
        observed_hex: 现存残留色的实测值，如 "#6E2020"
        dynasty: 朝代，如 "清"，用于风格先验与颜料筛选
        document_text: 文献描述文本
        extra_evidence: 额外证据列表（如光谱实验室给出的颜色）
        top_k: 返回候选颜料数量

    返回:
        AuthenticationResult
    """
    evidences: List[Evidence] = []
    if observed_hex:
        # 现存色是老化后的结果，权重较高
        evidences.append(Evidence("现存痕迹实测", observed_hex, 1.5))
    if document_text:
        evidences.extend(parse_document(document_text))
    if extra_evidence:
        evidences.extend(extra_evidence)

    if not evidences:
        raise ValueError("至少需要一种证据：现存色 / 文献文本 / 额外证据")

    # 1) 在 Lab 空间加权融合所有证据色
    labs = [cu.hex_to_lab(e.hex_color) for e in evidences]
    weights = [e.weight for e in evidences]
    fused_lab = cu.mix_lab_colors(labs, weights)
    inferred_hex = cu.lab_to_hex(fused_lab)

    # 2) 朝代风格先验：若指定朝代，向该朝代代表色系做轻度靠拢
    if dynasty and dynasty in kb.DYNASTIES:
        style = kb.DYNASTIES[dynasty]
        style_hexes = [kb.PIGMENTS[p].hex_fresh for p in style.palette if p in kb.PIGMENTS]
        if style_hexes:
            style_lab = cu.mix_lab_colors(
                [cu.hex_to_lab(h) for h in style_hexes],
                [1.0] * len(style_hexes))
            inferred_lab = cu.mix_lab_colors([fused_lab, style_lab], [3.0, 1.0])
            inferred_hex = cu.lab_to_hex(inferred_lab)

    # 3) 匹配"新鲜态"最接近的颜料，作为原始用色候选
    candidates = []
    for p in kb.PIGMENTS.values():
        if dynasty and dynasty not in p.dynasties:
            continue
        d = cu.color_distance(inferred_hex, p.hex_fresh)
        candidates.append((d, p))
    candidates.sort(key=lambda x: x[0])
    top = candidates[:top_k]
    matched = [{"颜料": p.name, "成分": p.formula,
                "新鲜态色": p.hex_fresh, "色差": round(d, 2),
                "耐光性": p.lightfastness}
               for d, p in top]

    # 4) 置信度：证据越充分、推断色与最近颜料越接近，置信度越高
    best_d = top[0][0] if top else 100.0
    color_fit = max(0.0, 1 - best_d / 60.0)
    evidence_factor = min(1.0, 0.5 + 0.15 * len(evidences))
    confidence = round(color_fit * evidence_factor, 2)

    reasoning = (
        f"融合 {len(evidences)} 条证据（现存色权重最高）在 Lab 空间得到推断色 {inferred_hex}；"
    )
    if dynasty:
        reasoning += f"按{dynasty}代风格先验轻度校正；"
    reasoning += (
        f"与颜料库比对，最接近『{top[0][1].name if top else '无'}』"
        f"(新鲜态 {top[0][1].hex_fresh if top else '-'}，色差 {best_d:.1f})。"
    )
    if observed_hex and top:
        aged_gap = cu.color_distance(observed_hex, top[0][1].hex_aged)
        reasoning += f"现存色与该颜料老化态色差 {aged_gap:.1f}，"
        reasoning += "相符，老化解释成立。" if aged_gap < 25 else "偏差较大，可能存在混色或后期污染。"

    return AuthenticationResult(
        original_hex=inferred_hex,
        observed_hex=observed_hex,
        dynasty=dynasty or "未指定",
        confidence=confidence,
        matched_pigments=matched,
        evidence_used=[{"来源": e.source, "颜色": e.hex_color, "权重": e.weight}
                       for e in evidences],
        reasoning=reasoning,
    )


# 便于模块单独测试
if __name__ == "__main__":
    r = authenticate(observed_hex="#6E2020", dynasty="清",
                     document_text="檐下青绿彩画，朱柱，间以金线")
    print(r.to_dict())
