"""模块六：由图片识别古建筑材质，并推荐修复所需材料。

两个核心能力：
  1) identify_material —— 上传文物照片，提取主色 + 简单纹理统计（粗糙度、
     饱和度、亮度、边缘密度），与材质库典型特征做加权匹配，返回候选材质。
  2) recommend_repair —— 给定材质与病害，汇总该材质所需修复材料 + 病害
     专项材料 + 工艺要点 + 禁忌，输出可执行的修复配材方案。

方法为纯规则 + 图像统计，不依赖深度学习权重，Streamlit Cloud 开箱即用。
结果为辅助参考，实际操作须以检测报告为准。
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Union, BinaryIO
import io

from PIL import Image, ImageFilter, ImageStat

from .. import color_utils as cu
from .. import knowledge_base as kb


@dataclass
class MaterialMatch:
    material: str              # 材质名
    category: str              # 大类
    score: float               # 综合置信度 0-1
    color_gap: float           # 与典型色的最小色差
    dominant_hex: str          # 图像主色
    texture: str               # 材质纹理描述
    roughness: float           # 图像测得粗糙度
    gloss: float               # 图像测得光泽度
    common_diseases: List[str] # 常见病害
    reasoning: str             # 判定理由

    def to_dict(self):
        return asdict(self)


@dataclass
class RepairPlan:
    material: str
    diseases: List[str]
    materials: List[str]       # 修复所需材料（去重）
    craft: str
    taboo: str
    urgency: str
    environment: Dict[str, str]
    reasoning: str

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------- 图像特征
def _image_features(source: Union[str, BinaryIO, Image.Image],
                    max_size: int = 240) -> Dict:
    """提取用于材质判定的图像统计特征。"""
    if isinstance(source, Image.Image):
        img = source.convert("RGB")
    else:
        if hasattr(source, "seek"):
            source.seek(0)
        img = Image.open(source).convert("RGB")
    img.thumbnail((max_size, max_size))
    w, h = img.size
    if w == 0 or h == 0:
        raise ValueError("图片尺寸无效")

    # 主色（复用 K-means 主色提取）
    from .image_color import extract_palette
    swatches = extract_palette(img, top_n=6, max_size=max_size)
    dominant = swatches[0].hex if swatches else "#888888"

    # 亮度 / 饱和度 / 色彩丰富度
    small = img.resize((min(160, w), min(160, h)))
    hsv = small.convert("HSV")
    sat = ImageStat.Stat(hsv.getchannel("S")).mean[0] / 255.0   # 平均饱和度
    val = ImageStat.Stat(hsv.getchannel("V")).mean[0] / 255.0   # 平均明度

    # 边缘密度：用 FIND_EDGES 后的平均强度近似表面纹理复杂度
    gray = small.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0] / 255.0
    texture_var = ImageStat.Stat(gray).stddev[0] / 255.0

    # 粗糙度估计：边缘密度 + 纹理方差 + 低饱和（石/木/灰偏哑光粗糙）
    roughness = min(1.0, 0.45 * (edge_mean * 3.0) + 0.35 * (texture_var * 2.2)
                    + 0.20 * (1.0 - sat))
    # 光泽度估计：高饱和 + 高明度 + 局部强反差（金属/釉面高光）
    gloss = min(1.0, max(0.0, 0.5 * sat + 0.3 * val + 0.2 * (edge_mean * 2.5)))

    return {
        "dominant_hex": dominant,
        "roughness": round(roughness, 3),
        "gloss": round(gloss, 3),
        "saturation": round(sat, 3),
        "lightness": round(val, 3),
        "edge": round(edge_mean, 3),
        "swatches": swatches,
    }


def identify_material(source: Union[str, BinaryIO, Image.Image],
                      top_n: int = 3) -> List[MaterialMatch]:
    """由图片识别最可能的古建筑材质。

    参数:
        source: 图片路径 / 文件对象 / PIL Image
        top_n: 返回候选数量
    返回:
        List[MaterialMatch]，按综合置信度降序
    """
    f = _image_features(source)
    results: List[MaterialMatch] = []

    for m in kb.MATERIALS.values():
        # 1) 色彩相似度：主色及前几主色与材质典型色的最小色差
        gaps = [cu.color_distance(f["dominant_hex"], h) for h in m.signature_hexes]
        for s in f["swatches"][1:4]:
            gaps.extend(cu.color_distance(s.hex, h) for h in m.signature_hexes)
        color_gap = min(gaps) if gaps else 60.0
        color_score = max(0.0, 1.0 - color_gap / 55.0)

        # 2) 粗糙度接近度（差越小分越高）
        rough_score = max(0.0, 1.0 - abs(f["roughness"] - m.roughness) * 1.6)
        # 3) 光泽接近度
        gloss_score = max(0.0, 1.0 - abs(f["gloss"] - m.gloss) * 1.5)

        raw = 0.60 * color_score + 0.25 * rough_score + 0.15 * gloss_score
        score = round(max(0.0, min(1.0, raw)), 2)

        reasoning = (
            f"图像主色 {f['dominant_hex']} 与『{m.name}』典型色最小色差 {color_gap:.1f}；"
            f"测得粗糙度 {f['roughness']:.2f}（材质参考 {m.roughness:.2f}）、"
            f"光泽 {f['gloss']:.2f}（参考 {m.gloss:.2f}）。"
        )
        results.append(MaterialMatch(
            material=m.name,
            category=m.category,
            score=score,
            color_gap=round(color_gap, 2),
            dominant_hex=f["dominant_hex"],
            texture=m.texture,
            roughness=f["roughness"],
            gloss=f["gloss"],
            common_diseases=list(m.common_diseases),
            reasoning=reasoning,
        ))

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_n]


def recommend_repair(material_name: str,
                     diseases: Optional[List[str]] = None,
                     environment: Optional[Dict[str, str]] = None) -> RepairPlan:
    """据材质与病害，给出修复所需材料与工艺方案。

    参数:
        material_name: 材质名（支持模糊匹配，如『汉白玉』『楠木』）
        diseases: 病害名列表，如 ['空鼓','盐析']
        environment: 可选的当前环境（湿度/照度），用于风险提示
    返回:
        RepairPlan
    """
    m = kb.get_material(material_name)
    if m is None:
        raise ValueError(f"材质库中没有『{material_name}』")

    diseases = diseases or []

    def _base(name: str) -> str:
        """取材料核心名用于去重：去掉括号内的补充说明。"""
        return name.split("(")[0].split("（")[0].strip()

    materials: List[str] = []
    seen = set()
    for item in list(m.repair_materials) + [
        item
        for d in diseases
        for item in kb.MATERIAL_DISEASE_FIX.get(d, [])
    ]:
        key = _base(item)
        if key not in seen:
            seen.add(key)
            materials.append(item)

    # 紧迫度：取命中的病害中较高者
    level = {"低": 1, "中": 2, "高": 3}
    urgency = "低"
    for d in diseases:
        rule = kb.DAMAGE_RULES.get(d)
        if rule and level.get(rule.urgency, 0) > level.get(urgency, 0):
            urgency = rule.urgency
    if not diseases:
        urgency = "中"  # 无明确病害时按预防性维护

    env = dict(kb.PROCESS["环境建议"])
    risks: List[str] = []
    if environment:
        import re
        hum = str(environment.get("湿度", ""))
        mh = re.search(r"(\d+(?:\.\d+)?)", hum)
        if mh and float(mh.group(1)) > 60:
            risks.append(f"当前湿度 {hum} 高于 60% RH，须先降湿再行修复")
        lux = str(environment.get("照度", ""))
        ml = re.search(r"(\d+(?:\.\d+)?)", lux)
        if ml and float(ml.group(1)) > 50:
            risks.append(f"当前照度 {lux} 高于 50 lux，须遮光")

    reasoning = (
        f"『{m.name}』（{m.category}）常见病害为 {'、'.join(m.common_diseases)}。"
        + (f"针对所选病害 {'、'.join(diseases)}，在材质常规材料外补充了专项材料。"
           if diseases else "未指明具体病害，按该材质常规维护配材。")
        + "遵循最小干预、可逆性原则。"
    )
    if risks:
        reasoning += " 环境提示：" + "；".join(risks) + "。"

    return RepairPlan(
        material=m.name,
        diseases=list(diseases),
        materials=materials,
        craft=m.craft,
        taboo=m.taboo,
        urgency=urgency,
        environment=env,
        reasoning=reasoning,
    )


if __name__ == "__main__":
    from PIL import Image as _Image
    # 造一张偏汉白玉的浅色图
    im = _Image.new("RGB", (100, 100))
    im.putdata([(230, 226, 214)] * 8000 + [(216, 211, 196)] * 2000)
    for r in identify_material(im, top_n=3):
        print(r.material, r.score, r.dominant_hex, r.roughness, r.gloss)
    plan = recommend_repair("汉白玉", ["空鼓", "盐析"])
    print("修复材料:", plan.materials)
    print("紧迫度:", plan.urgency)
