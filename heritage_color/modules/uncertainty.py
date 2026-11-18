# -*- coding: utf-8 -*-
"""不确定性量化引擎 —— 把「一个答案」变成「一个概率分布」。

纯标准库实现。包含：

1. 贝叶斯后验：以 CIEDE2000 色差构造似然 exp(-ΔE/κ)，
   乘以朝代先验与文献证据权重，softmax 归一化为候选后验概率。
   相比原先线性的 1-ΔE/60 打分，具备可解释的概率语义。
2. 蒙特卡洛传播：对实测色注入 Lab 测量噪声（分光光度计典型重复精度），
   采样 N 次并重新推断，得到最优候选的频次估计、色域云与收敛曲线。
3. 置信椭圆：对采样点的 a*/b* 协方差矩阵做解析特征分解，
   给出 95% 置信区域的主轴、旋转角，可直接投影到 CIE 色度图。

参考：CIEDE2000 色差与目视容差；贝叶斯证据合成；蒙特卡洛不确定度传播
      (JCGM 100:2008 GUM Supplement 1)。
"""

import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from .. import color_utils as cu


# 分光光度计对彩画残留色的典型重复性（CIE-L*ab 标准差）。
# 彩画表面常有污染、胶结料不均与风化，a*/b* 方向的不确定度取得较宽。
_DEFAULT_SIGMA = (2.0, 3.2, 3.2)


def bayesian_posterior(candidates: Sequence[Tuple[str, str, float]],
                       priors: Optional[Dict[str, float]] = None,
                       doc_bonus: Optional[Dict[str, float]] = None,
                       kappa: float = 12.0) -> List[Dict]:
    """候选后验概率。

    candidates: [(名称, 候选色 hex, 与观测色的 CIEDE2000 色差), ...]
    priors    : 名称 -> 先验权重（如朝代可用性 0.3~1.0）
    doc_bonus : 名称 -> 文献命中加成（0~1）
    返回按后验概率降序的列表，含 log-evidence 分解，便于解释。
    """
    priors = priors or {}
    doc_bonus = doc_bonus or {}
    rows = []
    for name, hex_color, de in candidates:
        log_prior = math.log(max(1e-6, priors.get(name, 1.0)))
        log_lik = -float(de) / kappa
        log_bonus = math.log(1.0 + max(0.0, doc_bonus.get(name, 0.0)))
        rows.append({
            "name": name, "hex": hex_color, "delta_e": round(float(de), 2),
            "log_likelihood": round(log_lik, 3),
            "log_prior": round(log_prior, 3),
            "log_evidence": round(log_bonus, 3),
            "score": log_lik + log_prior + log_bonus,
        })
    if not rows:
        return []
    m = max(r["score"] for r in rows)
    total = sum(math.exp(r["score"] - m) for r in rows)
    for r in rows:
        r["posterior"] = round(math.exp(r["score"] - m) / total, 4)
        r.pop("score")
    rows.sort(key=lambda r: -r["posterior"])
    return rows


def _eig2(a: float, b: float, c: float) -> Tuple[float, float, float]:
    """2×2 对称矩阵 [[a,b],[b,c]] 的解析特征分解。

    返回 (λ1, λ2, 主轴与 x 轴夹角弧度)，λ1 ≥ λ2。
    """
    tr = (a + c) / 2.0
    dif = math.sqrt(max(0.0, ((a - c) / 2.0) ** 2 + b * b))
    l1, l2 = tr + dif, max(0.0, tr - dif)
    angle = 0.5 * math.atan2(2.0 * b, a - c) if abs(b) > 1e-12 else (0.0 if a >= c else math.pi / 2)
    return l1, l2, angle


def monte_carlo(observed_hex: str,
                candidate_hexes: Sequence[str],
                n_samples: int = 2000,
                sigma: Tuple[float, float, float] = _DEFAULT_SIGMA,
                seed: int = 20261118) -> Dict:
    """蒙特卡洛不确定度传播。

    对观测 Lab 注入高斯噪声，逐个样本重新寻找最近候选，
    输出最优候选频次（经验后验）、采样点云、95% 置信椭圆与收敛曲线。
    """
    rng = random.Random(seed)
    base_lab = cu.hex_to_lab(observed_hex)
    cand_labs = [(h, cu.hex_to_lab(h)) for h in candidate_hexes]
    if not cand_labs:
        return {"valid": False}

    winners: Dict[str, int] = {h: 0 for h in candidate_hexes}
    cloud: List[Tuple[float, float, float]] = []   # (a*, b*, L*)
    noisy_labs: List[Tuple[float, float, float]] = []
    convergence: List[Dict] = []
    votes_snapshot = {h: 0 for h in candidate_hexes}
    checkpoint = max(1, n_samples // 20)

    for i in range(1, n_samples + 1):
        noisy = (
            base_lab[0] + rng.gauss(0.0, sigma[0]),
            base_lab[1] + rng.gauss(0.0, sigma[1]),
            base_lab[2] + rng.gauss(0.0, sigma[2]),
        )
        noisy_labs.append(noisy)
        cloud.append((noisy[1], noisy[2], noisy[0]))
        best_h = min(cand_labs, key=lambda c: cu.delta_e_cie2000(noisy, c[1]))[0]
        winners[best_h] += 1
        votes_snapshot[best_h] += 1
        if i % checkpoint == 0 or i == n_samples:
            top = max(votes_snapshot.values()) / i
            convergence.append({"n": i, "top_probability": round(top, 4)})

    n = float(n_samples)
    ma = sum(p[0] for p in cloud) / n
    mb = sum(p[1] for p in cloud) / n
    va = sum((p[0] - ma) ** 2 for p in cloud) / max(1, n - 1)
    vb = sum((p[1] - mb) ** 2 for p in cloud) / max(1, n - 1)
    cab = sum((p[0] - ma) * (p[1] - mb) for p in cloud) / max(1, n - 1)
    l1, l2, angle = _eig2(va, cab, vb)
    # 95% 置信（2D χ² 分位数 5.991）
    chi2 = 5.991

    freq = [{"name": h, "hex": h, "posterior": round(v / n, 4), "votes": v}
            for h, v in winners.items()]
    freq.sort(key=lambda r: -r["posterior"])

    # 初色色域云：把观测色的测量不确定度沿「观测 → 最优候选」的
    # Lab 位移向量传播到初色空间，得到可投影到 CIE 色度图的点云。
    top_hex = freq[0]["hex"]
    top_lab = cu.hex_to_lab(top_hex)
    shift = tuple(top_lab[i] - base_lab[i] for i in range(3))
    stride = max(1, len(noisy_labs) // 240)
    cloud_hexes = [
        cu.lab_to_hex((nl[0] + shift[0], nl[1] + shift[1], nl[2] + shift[2]))
        for nl in noisy_labs[::stride]
    ]

    return {
        "valid": True,
        "n_samples": n_samples,
        "sigma": sigma,
        "observed_hex": observed_hex,
        "top_hex": top_hex,
        "frequentist_posterior": freq,
        "cloud": cloud,
        "cloud_hexes": cloud_hexes,
        "mean_ab": (round(ma, 3), round(mb, 3)),
        "ellipse": {
            "cx": round(ma, 3), "cy": round(mb, 3),
            "rx": round(math.sqrt(l1 * chi2), 3),
            "ry": round(math.sqrt(l2 * chi2), 3),
            "angle_deg": round(math.degrees(angle), 2),
        },
        "convergence": convergence,
        "entropy": round(-sum((v / n) * math.log(v / n)
                              for v in winners.values() if v > 0), 4),
    }


def confidence_summary(mc: Dict, posterior: List[Dict]) -> Dict:
    """汇总成界面指标：最高后验、是否显著、等效候选数、推荐置信等级。"""
    if not mc.get("valid"):
        return {"valid": False}
    top = mc["frequentist_posterior"][0]
    eff = math.exp(mc["entropy"])
    p = top["posterior"]
    level = "高" if p >= 0.75 else ("中" if p >= 0.45 else "低")
    return {
        "valid": True,
        "top_hex": top["hex"],
        "top_probability": p,
        "effective_candidates": round(eff, 2),
        "confidence_level": level,
        "samples": mc["n_samples"],
        "bayesian_top": posterior[0]["name"] if posterior else "-",
        "bayesian_top_p": posterior[0]["posterior"] if posterior else 0.0,
    }
