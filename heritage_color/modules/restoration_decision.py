"""模块三：修复决策。

目标：根据"颜料种类 + 病害类型 + 展示/保存环境"，输出结构化的修复
建议（紧迫度、工艺步骤、材料、环境控制、风险与禁忌）。

方法：以知识库中的病害规则为主，叠加颜料特性（耐光性/毒性/化学稳定性）
与环境参数进行修正，遵循最小干预、可逆性等文物保护原则。
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .. import knowledge_base as kb


@dataclass
class DecisionResult:
    pigment: str
    damage: str
    urgency: str                  # 高/中/低
    steps: List[str]              # 建议工艺步骤
    materials: List[str]          # 建议材料
    environment: Dict[str, str]   # 环境控制建议（标准值）
    current_environment: Dict[str, str]  # 用户传入的当前环境
    risks: List[str]              # 风险提示
    principles: List[str]         # 遵循原则
    summary: str

    def to_dict(self):
        return asdict(self)


def _match_damage(name: str):
    if name in kb.DAMAGE_RULES:
        return kb.DAMAGE_RULES[name]
    hits = [r for n, r in kb.DAMAGE_RULES.items() if name in n or n in name]
    if len(hits) == 1:
        return hits[0]
    return None


def decide(pigment: Optional[str] = None,
           damage: Optional[str] = None,
           environment: Optional[Dict] = None,
           urgency_override: Optional[str] = None) -> DecisionResult:
    """生成修复决策。

    参数:
        pigment: 颜料名，如"铅白""朱砂"
        damage: 病害名，如"变黑""剥落""粉化"
        environment: 环境参数，如 {"湿度": "70%", "照度": "300lux"}
        urgency_override: 手动覆盖紧迫度

    返回:
        DecisionResult
    """
    if not damage:
        raise ValueError("必须指定病害类型 damage")
    rule = _match_damage(damage)
    if rule is None:
        raise ValueError(f"未知病害：{damage}。可选：{list(kb.DAMAGE_RULES)}")

    p = kb.get_pigment(pigment) if pigment else None
    steps = list(rule.methods)
    risks = [rule.avoid]
    materials = []

    # 按颜料特性修正
    if p:
        if p.lightfastness <= 2:
            risks.append(f"『{p.name}』耐光性差（{p.lightfastness}/5），严格控制光照")
            steps.insert(0, "优先采用复制件展示，原件降低光照")
        if "铅" in p.toxicity or "汞" in p.toxicity or "砷" in p.toxicity:
            risks.append(f"『{p.name}』{p.toxicity}，操作时佩戴防护、避免粉尘")
        if p.name == "铅白" and rule.name == "变黑":
            materials.append("过氧化氢（局部还原，需专业操作）")
        if p.name in ("朱砂", "银朱") and rule.name == "变黑":
            risks.append("朱砂变黑成因复杂，勿盲目还原，先做成分检测")
        materials.append(f"补色/回贴用颜料应与原颜料一致：{p.name}")

    # 通用材料（按病害）
    if rule.name in ("剥落", "起甲", "粉化"):
        materials.extend(["明胶", "鱼鳔胶"])
    if rule.name == "盐析":
        materials.append("纸浆（脱盐）")
    if not materials:
        materials.append("以物理清理与环境控制为主，慎用化学材料")

    # 建议环境（标准值）+ 用户当前环境（单独存放，用于对比告警）
    env = dict(kb.PROCESS["环境建议"])
    if rule.name == "霉变":
        env["湿度"] = "≤60% RH"
    if rule.name == "褪色":
        env["照度"] = "≤50 lux"
    current_env = dict(environment) if environment else {}

    # 环境超标告警：解析传入的湿度/照度，与建议值比较
    env_warnings = []
    if current_env:
        import re
        hum = str(current_env.get("湿度", ""))
        m = re.search(r"(\d+(?:\.\d+)?)", hum)
        if m and float(m.group(1)) > 60:
            env_warnings.append(f"当前湿度 {hum} 高于建议上限 60% RH，须先降湿")
        lux = str(current_env.get("照度", ""))
        m2 = re.search(r"(\d+(?:\.\d+)?)", lux)
        if m2 and float(m2.group(1)) > 50:
            env_warnings.append(f"当前照度 {lux} 高于建议上限 50 lux，须遮光")
    risks.extend(env_warnings)

    urgency = urgency_override or rule.urgency
    summary = (
        f"针对『{p.name if p else '未指明'}』彩画的『{rule.name}』病害"
        f"（紧迫度：{urgency}）：{rule.causes}。"
        f"建议 {len(steps)} 步处理，核心是 {steps[0]}；"
        f"环境上重点控制温度与湿度（建议 {env['温度']} / {env['湿度']}）。"
    )
    if env_warnings:
        summary += " 注意：" + "；".join(env_warnings) + "。"

    return DecisionResult(
        pigment=p.name if p else (pigment or "未指明"),
        damage=rule.name,
        urgency=urgency,
        steps=steps,
        materials=list(dict.fromkeys(materials)),
        environment=env,
        current_environment=current_env,
        risks=list(dict.fromkeys(risks)),
        principles=kb.PROCESS["修复原则"],
        summary=summary,
    )


if __name__ == "__main__":
    print(decide(pigment="铅白", damage="变黑", environment={"湿度": "75%"}))
