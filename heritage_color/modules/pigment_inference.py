"""模块二：颜料推演。

目标：给定一个目标颜色（实测色或考证出的原始色），推演可能使用了哪些
颜料、以及大致的配比。

方法：
  1) 单颜料匹配：按色差排序，找最接近的若干颜料。
  2) 混色求解：若单颜料色差偏大，尝试从常用颜料中两两/三三线性组合
     （在 Lab 空间混合），搜索能最好复现目标色的配方。
  3) 结合朝代约束与颜料耐光性给出可信度。
"""

from dataclasses import dataclass, asdict
from itertools import combinations
from typing import List, Dict, Optional, Tuple

from .. import color_utils as cu
from .. import knowledge_base as kb


@dataclass
class Formula:
    pigments: Dict[str, float]   # 颜料名 -> 配比(0-1)
    result_hex: str              # 该配比混出的颜色
    delta_e: float               # 与目标色色差
    confidence: float            # 0-1

    def to_dict(self):
        d = asdict(self)
        d["pigments"] = {k: round(v, 3) for k, v in self.pigments.items()}
        d["delta_e"] = round(self.delta_e, 2)
        return d


def _single_pigment_formulas(target_hex: str, dynasty: Optional[str]):
    target_lab = cu.hex_to_lab(target_hex)
    out = []
    for p in kb.PIGMENTS.values():
        if dynasty and dynasty not in p.dynasties:
            continue
        d = cu.color_distance(target_hex, p.hex_fresh)
        conf = max(0.0, 1 - d / 60.0) * (0.6 + 0.08 * p.lightfastness)
        out.append(Formula({p.name: 1.0}, p.hex_fresh, d, round(min(conf, 0.99), 2)))
    out.sort(key=lambda f: f.delta_e)
    return out


def _mixture_formulas(target_hex: str, dynasty: Optional[str],
                      max_components: int = 3, top_n: int = 3):
    """在 Lab 空间暴力搜索 2~max_components 种颜料的等权/加权组合。"""
    target_lab = cu.hex_to_lab(target_hex)
    pool = [p for p in kb.PIGMENTS.values()
            if not dynasty or dynasty in p.dynasties]
    ratios = (0.25, 0.5, 0.75)
    results = []

    for n in (2, 3):
        if n > max_components:
            break
        for combo in combinations(pool, n):
            labs = [cu.hex_to_lab(p.hex_fresh) for p in combo]
            # 等权 + 让每种颜料占主次的若干配比
            weight_sets = [[1] * n]
            if n == 2:
                weight_sets += [[r, 1 - r] for r in ratios]
            for w in weight_sets:
                mixed_lab = cu.mix_lab_colors(labs, w)
                mixed_hex = cu.lab_to_hex(mixed_lab)
                d = cu.delta_e_cie2000(target_lab, mixed_lab)
                total = sum(w)
                formula = {p.name: round(wi / total, 3) for p, wi in zip(combo, w)}
                avg_lf = sum(p.lightfastness for p in combo) / n
                conf = max(0.0, 1 - d / 45.0) * (0.55 + 0.07 * avg_lf)
                results.append(Formula(formula, mixed_hex, d, round(min(conf, 0.98), 2)))
    results.sort(key=lambda f: f.delta_e)
    return results[:top_n]


def infer(target_hex: str, dynasty: Optional[str] = None,
          allow_mixture: bool = True, top_n: int = 3) -> Dict:
    """根据颜色推演颜料配方。

    参数:
        target_hex: 目标颜色，如 "#2E9070"
        dynasty: 朝代约束（可选）
        allow_mixture: 是否允许混合颜料配方
        top_n: 返回候选配方数

    返回:
        dict: 含单颜料候选、混合候选、最优配方、说明
    """
    singles = _single_pigment_formulas(target_hex, dynasty)[:top_n]
    best_single = singles[0] if singles else None

    mixtures = []
    best = best_single
    if allow_mixture:
        mixtures = _mixture_formulas(target_hex, dynasty, top_n=top_n)
        if mixtures and (best is None or mixtures[0].delta_e < best.delta_e - 3):
            best = mixtures[0]

    if best is None:
        raise ValueError("颜料库中无可用颜料（检查朝代约束是否过窄）")

    reasoning = f"目标色 {target_hex}："
    reasoning += f"最接近的单颜料是『{best_single.pigments and next(iter(best_single.pigments))}』，色差 {best_single.delta_e:.1f}；" if best_single else ""
    if mixtures:
        reasoning += f"最佳混合配方色差降至 {best.delta_e:.1f}，"
        if best.delta_e < best_single.delta_e - 3:
            reasoning += "显著优于单颜料，判断为多颜料调配。"
        else:
            reasoning += "与单颜料接近，优先采用更简单的单颜料解释。"
    if dynasty:
        reasoning += f" 已限定{dynasty}代可用颜料范围。"

    return {
        "target_hex": target_hex,
        "dynasty": dynasty or "未指定",
        "best_formula": best.to_dict(),
        "single_pigments": [f.to_dict() for f in singles],
        "mixtures": [f.to_dict() for f in mixtures],
        "reasoning": reasoning,
        "note": "配比为 Lab 空间线性近似的示意结果，真实配方需以显微 / XRF / 拉曼检测为准。",
    }


if __name__ == "__main__":
    print(infer("#2E9070", dynasty="清"))
