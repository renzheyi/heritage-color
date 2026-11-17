"""模块四：建筑风格识别。

目标：在色彩考证得到"原始色 / 候选颜料 / 朝代"之后，进一步判断这些
色彩最可能对应哪一类古建筑彩画风格（和玺 / 旋子 / 苏式 / 敦煌壁画等）。

方法：对每种风格计算一个综合得分——
  1) 色彩相似度：输入色与风格标志色的最小 CIEDE2000 色差；
  2) 颜料吻合度：考证出的候选颜料落在该风格标志性颜料中的比例；
  3) 朝代吻合度：朝代落在该风格流行朝代范围内则加分。
三项加权得到置信度，排序返回。纯规则推理，结果可解释。
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .. import color_utils as cu
from .. import knowledge_base as kb


@dataclass
class StyleMatch:
    style: str                  # 风格名
    category: str               # 类别
    score: float                # 综合置信度 0-1
    color_gap: float            # 与标志色的最小色差
    matched_palette: List[str]  # 命中的颜料
    feature: str                # 风格特征
    typical_use: str            # 典型建筑
    rank: str                   # 等级
    reasoning: str              # 判定理由

    def to_dict(self):
        return asdict(self)


def _normalize_score(raw: float) -> float:
    return round(max(0.0, min(1.0, raw)), 2)


def identify_style(color_hex: Optional[str] = None,
                   dynasty: Optional[str] = None,
                   pigment_names: Optional[List[str]] = None,
                   top_n: int = 3) -> List[StyleMatch]:
    """根据色彩与朝代证据，识别最可能的古建筑彩画风格。

    参数:
        color_hex: 考证出的原始色（或实测残留色），如 "#6E2020"
        dynasty: 朝代，如 "清"，用于朝代吻合度
        pigment_names: 候选颜料名列表，如 ["石青", "石绿"]
        top_n: 返回前 N 个候选风格

    返回:
        List[StyleMatch]，按得分降序
    """
    pigment_names = pigment_names or []
    results: List[StyleMatch] = []

    for style in kb.ARCHITECTURE_STYLES.values():
        # 1) 色彩相似度：与所有标志色取最小色差
        color_gap = 60.0
        if color_hex:
            gaps = [cu.color_distance(color_hex, h) for h in style.signature_hexes]
            color_gap = min(gaps) if gaps else 60.0
        color_score = max(0.0, 1.0 - color_gap / 60.0)

        # 2) 颜料吻合度：候选颜料命中风格标志颜料的比例
        style_palette = set(style.palette)
        matched = [p for p in pigment_names if p in style_palette]
        pigment_score = (len(matched) / len(pigment_names)) if pigment_names else 0.0

        # 3) 朝代吻合度
        dynasty_score = 0.0
        if dynasty and dynasty in style.dynasties:
            dynasty_score = 1.0

        # 加权：色彩 0.5 / 颜料 0.3 / 朝代 0.2
        raw = 0.5 * color_score + 0.3 * pigment_score + 0.2 * dynasty_score
        # 若完全没有任何证据，得分没有意义，直接跳过
        if not color_hex and not pigment_names and not dynasty:
            continue

        score = _normalize_score(raw)

        reasoning_parts = []
        if color_hex:
            reasoning_parts.append(f"色彩与标志色最小色差 {color_gap:.1f}")
        if pigment_names:
            reasoning_parts.append(
                f"候选颜料命中 {len(matched)}/{len(pigment_names)}"
                + (f"（{'、'.join(matched)}）" if matched else "")
            )
        if dynasty:
            reasoning_parts.append(
                f"朝代{'吻合' if dynasty_score else '不吻合'}『{style.name}』流行期"
            )
        reasoning = "；".join(reasoning_parts) + "。"

        results.append(StyleMatch(
            style=style.name,
            category=style.category,
            score=score,
            color_gap=round(color_gap, 2),
            matched_palette=matched,
            feature=style.feature,
            typical_use=style.typical_use,
            rank=style.rank,
            reasoning=reasoning,
        ))

    results.sort(key=lambda m: m.score, reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    for m in identify_style("#6E2020", dynasty="清",
                            pigment_names=["朱砂", "石青"]):
        print(m.style, m.score, m.reasoning)
