"""文物色彩考证与修复辅助系统 —— 古风界面（门户导航式）。

首页为五个独立方块，点击进入对应程序；每个程序页可返回首页。
部署到 Streamlit Community Cloud 时，入口文件选这个。
本地运行：streamlit run app.py
"""

import os
from typing import List
import streamlit as st

# 注意：set_page_config 必须是第一个 Streamlit 命令，放在任何 st.* 之前。
st.set_page_config(
    page_title="文物色彩考证与修复辅助系统",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 兼容云端旧缓存：Streamlit Cloud 偶尔会只更新 app.py 而未刷新包文件，
# 导致 from heritage_color import ... 抛 ImportError。这里显式检查并给出
# 可操作的提示，而不是显示被脱敏的红色报错页。
try:
    import heritage_color as _hc
    _REQUIRED = (
        "auth_color", "infer_pigment", "decide_restoration",
        "identify_architecture_style", "extract_image_colors",
        "identify_image_material", "recommend_repair_materials",
    )
    _missing = [n for n in _REQUIRED if not hasattr(_hc, n)]
    if _missing:
        raise ImportError(
            "云端运行的是旧版代码缓存，缺少新模块导出："
            + "、".join(_missing)
            + "。请在 Streamlit Cloud 的 Manage app 中点击 Reboot app，"
            "或确认已部署最新提交 731a23f。"
        )
    auth_color = _hc.auth_color
    infer_pigment = _hc.infer_pigment
    decide_restoration = _hc.decide_restoration
    identify_architecture_style = _hc.identify_architecture_style
    extract_image_colors = _hc.extract_image_colors
    identify_image_material = _hc.identify_image_material
    recommend_repair_materials = _hc.recommend_repair_materials
    from heritage_color import knowledge_base as kb
except Exception as _e:
    st.error(
        "应用初始化失败（多为 Streamlit Cloud 代码缓存未刷新）：\n\n"
        f"{type(_e).__name__}: {_e}\n\n"
        "解决办法：打开右下角 Manage app → 点击 ... → Reboot app；"
        "若仍失败，确认 GitHub 仓库 renzheyi/heritage-color 的 main 分支"
        "最新提交为 731a23f。"
    )
    st.stop()

from theme import apply_theme

apply_theme()

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


# ---------------------------------------------------------------- 通用组件
def banner(image_name: str, title: str, subtitle: str = ""):
    """古建筑图片横幅：有图则显示图片，无图则用 CSS 古风纹样占位。"""
    path = os.path.join(ASSETS, image_name)
    sub = f"<small>{subtitle}</small>" if subtitle else ""
    if os.path.exists(path):
        import base64
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div class="gf-banner">'
            f'<img src="data:image/jpeg;base64,{data}" alt="{title}">'
            f'<div class="gf-banner-cap">{title}{sub}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="gf-banner" style="background:linear-gradient(135deg,#7A2E24,#9E3329 55%,#B08D4F);">'
            f'<div class="gf-cloud-divider" style="color:#F7EFE0;">❖　云　纹　❖</div>'
            f'<div class="gf-banner-cap" style="position:static;background:none;color:#F7EFE0;">'
            f'{title}{sub}</div></div>',
            unsafe_allow_html=True,
        )


def card_start(title: str, desc: str = "") -> str:
    d = f'<div class="gf-card-desc">{desc}</div>' if desc else ""
    return (f'<div class="gf-ornate-card">'
            f'<div class="gf-card-title">{title}</div>{d}')


def swatch_html(hex_color: str, label: str = "") -> str:
    return (f'<span class="gf-swatch" style="background:{hex_color}"></span>'
            f'<span class="gf-swatch-label">{label or hex_color}</span>')


def nav_block(num: str, title: str, desc: str, btn_key: str):
    """渲染一个导航方块，返回是否被点击。整块视觉即一个门牌，按钮为其入口。"""
    with st.container():
        st.markdown(
            f'<div class="gf-nav-card">'
            f'<div class="gf-nav-num">{num}</div>'
            f'<div class="gf-nav-title">{title}</div>'
            f'<div class="gf-nav-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return st.button(f"进入 · {title}　→", key=btn_key, use_container_width=True)


def back_button():
    """程序页顶部的返回按钮。"""
    if st.button("←　返回总览", key="back_home"):
        st.session_state["view"] = "home"
        st.rerun()


def cloud_divider(text: str = "❖　云　纹　❖"):
    st.markdown(f'<div class="gf-cloud-divider">{text}</div>', unsafe_allow_html=True)


def meander():
    st.markdown('<div class="gf-meander"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- 页头
st.markdown(
    '<div class="gf-title">文物色彩考证与修复辅助系统</div>',
    unsafe_allow_html=True,
)
cloud_divider()
st.markdown(
    '<div class="gf-subtitle">'
    '<span class="gf-wadang">考色</span>'
    '&nbsp;&nbsp;以色彩证源流 · 以颜料推古法 · 以风格辨建制 · 以材质续华章&nbsp;&nbsp;'
    '<span class="gf-wadang">存真</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- 视图路由
if "view" not in st.session_state:
    st.session_state["view"] = "home"
view = st.session_state["view"]


# ================================================================ 门户首页
if view == "home":
    banner("forbidden_city.jpg", "丹宸彩画 · 源远流长",
           "故宫太和殿 —— 和玺彩画之典范，青绿为地，金龙腾跃")
    st.markdown(
        '<div style="text-align:center;color:#7A6A50;font-size:15px;'
        'letter-spacing:2px;margin:6px 0 18px;">择一门而入，探文物色彩之奥</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        if nav_block(
            "壹", "色彩考证",
            "参酌现存残留色、文献与朝代，推求文物彩画之初色。",
            "go_auth",
        ):
            st.session_state["view"] = "auth"; st.rerun()
        if nav_block(
            "叁", "建筑风格识别",
            "由色彩与用色制度，辨识和玺、旋子、苏式、敦煌等彩画风格。",
            "go_style",
        ):
            st.session_state["view"] = "style"; st.rerun()
        if nav_block(
            "伍", "材质辨识与配材",
            "上传照片辨识木石金属等材质，据病害给出修复所需材料。",
            "go_material",
        ):
            st.session_state["view"] = "material"; st.rerun()
    with c2:
        if nav_block(
            "贰", "颜料推演",
            "由一色反求所用颜料与调配之法，青绿朱黄，皆溯其源。",
            "go_infer",
        ):
            st.session_state["view"] = "infer"; st.rerun()
        if nav_block(
            "肆", "修复决策",
            "察颜料之性、病害之由、环境之宜，出最小干预之修复策。",
            "go_restore",
        ):
            st.session_state["view"] = "restore"; st.rerun()
        st.markdown(
            '<div class="gf-ornate-card" style="height:168px;'
            'display:flex;flex-direction:column;justify-content:center;">'
            '<div class="gf-nav-title">五门相济</div>'
            '<div class="gf-nav-desc">先辨其色，次溯其料，再识其制，'
            '终辨其质而续其命，循古法以守真。</div></div>',
            unsafe_allow_html=True,
        )

    meander()
    st.markdown(
        '<div style="text-align:center;color:#8A7B60;font-size:12px;'
        'font-family:\'Songti SC\',SimSun,serif;letter-spacing:1px;">'
        '本工具所出结果为辅助参考，实际操作须由专业人员依据检测报告裁定。'
        '</div>',
        unsafe_allow_html=True,
    )


# ================================================================ 壹 色彩考证
elif view == "auth":
    back_button()
    banner("summer_palace.jpg", "壹 · 色彩考证",
           "循残留之色，参文献之载，以推本来面目")
    st.markdown(card_start(
        "壹 · 色彩考证",
        "参酌现存残留色、文献记载与朝代风格，推求文物彩画之初色。",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**一、现存残留色**")
        observed = st.color_picker("现存残留色（实测）", "#6E2020", key="observed")
        with st.expander("上传文物照片，自动识别现存残留色"):
            uploaded = st.file_uploader(
                "上传彩画 / 壁画照片（JPG / PNG）",
                type=["jpg", "jpeg", "png"], key="upload_auth",
            )
            if uploaded is not None:
                st.image(uploaded, caption="已上传图像", width="stretch")
                with st.spinner("正在辨析画面主色……"):
                    try:
                        swatches = extract_image_colors(uploaded, top_n=6)
                        st.markdown("**画面主色（按占比）**")
                        for i, s in enumerate(swatches):
                            a, b = st.columns([1, 3])
                            with a:
                                st.markdown(swatch_html(s.hex, ""), unsafe_allow_html=True)
                            with b:
                                st.write(f"{s.hex} · 占比 {s.ratio:.0%}")
                                if st.button("用作现存色", key=f"pick_{i}"):
                                    st.session_state["observed"] = s.hex
                                    st.session_state["observed_picked"] = s.hex
                                    st.rerun()
                        if "observed_picked" in st.session_state:
                            st.success(
                                f"已采用图像取色 {st.session_state['observed_picked']} "
                                "作为现存残留色。")
                    except Exception as e:
                        st.error(f"图像解析失败：{e}")
        dynasty1 = st.selectbox("朝代", ["", *kb.DYNASTIES.keys()], index=5, key="dyn1")
        doc = st.text_area(
            "文献描述文本", "檐下青绿彩画，朱柱，间以金线",
            help="含朱/青/绿/金/红/白/黑等色彩关键词即可作为证据",
        )
        top_k = st.slider("候选颜料数量", 1, 5, 3, key="topk1")
        run1 = st.button("开始考证", type="primary", key="run1")
    with col2:
        st.markdown('<div class="gf-result-label">推断结果</div>', unsafe_allow_html=True)
        if run1:
            try:
                r = auth_color(
                    observed_hex=observed, dynasty=dynasty1 or None,
                    document_text=doc or None, top_k=top_k,
                )
                st.markdown("**原始色（推求）**")
                st.markdown(swatch_html(r.original_hex, r.original_hex),
                            unsafe_allow_html=True)
                st.metric("置信度", f"{r.confidence:.0%}")
                st.markdown("**匹配颜料**")
                st.dataframe(r.matched_pigments, width="stretch")
                st.markdown("**推理依据**")
                st.info(r.reasoning)
                pigment_names = [m["颜料"] for m in r.matched_pigments]
                styles = identify_architecture_style(
                    color_hex=r.original_hex, dynasty=dynasty1 or None,
                    pigment_names=pigment_names, top_n=3,
                )
                if styles:
                    st.markdown("**对应建筑风格（据色推求）**")
                    for m in styles:
                        st.write(
                            f"- **{m.style}**（{m.category}，匹配度 {m.score:.0%}）"
                            f"— {m.typical_use}")
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「开始考证」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 贰 颜料推演
elif view == "infer":
    back_button()
    banner("dunhuang.jpg", "贰 · 颜料推演",
           "青绿朱黄，皆有所自；一色反求，可溯其源")
    st.markdown(card_start(
        "贰 · 颜料推演",
        "由一色反求其所用颜料与调配之法，青绿朱黄，皆可溯其源。",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        target = st.color_picker("目标颜色", "#2E9070", key="target")
        dynasty2 = st.selectbox("朝代约束", ["", *kb.DYNASTIES.keys()], index=5, key="dyn2")
        allow_mix = st.checkbox("允许混合颜料配方", value=True)
        top_n = st.slider("候选配方数", 1, 5, 3, key="topn2")
        run2 = st.button("开始推演", type="primary", key="run2")
    with col2:
        st.markdown('<div class="gf-result-label">推演结果</div>', unsafe_allow_html=True)
        if run2:
            try:
                r = infer_pigment(target, dynasty=dynasty2 or None,
                                  allow_mixture=allow_mix, top_n=top_n)
                best = r["best_formula"]
                st.markdown("**最优配方**")
                st.markdown(swatch_html(best["result_hex"], best["result_hex"]),
                            unsafe_allow_html=True)
                st.write(f"{best['pigments']} · 色差 {best['delta_e']}")
                st.markdown("**单颜料候选**")
                st.dataframe(r["single_pigments"], width="stretch")
                if r["mixtures"]:
                    st.markdown("**混合配方候选**")
                    st.dataframe(r["mixtures"], width="stretch")
                st.info(r["reasoning"])
                st.caption(r["note"])
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「开始推演」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 叁 建筑风格识别
elif view == "style":
    back_button()
    banner("foguang_temple.jpg", "叁 · 建筑风格识别",
           "观其用色制度，辨其建制源流")
    st.markdown(card_start(
        "叁 · 建筑风格识别",
        "由色彩与用色制度，辨识其所属古建筑彩画风格：和玺、旋子、苏式、敦煌壁画等。",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        style_hex = st.color_picker("已知彩画主色", "#1B6FA8", key="style_color")
        with st.expander("或上传图片自动取色"):
            uploaded3 = st.file_uploader(
                "上传彩画照片取主色", type=["jpg", "jpeg", "png"], key="upload_style")
            if uploaded3 is not None:
                st.image(uploaded3, caption="已上传图像", width="stretch")
                try:
                    sw = extract_image_colors(uploaded3, top_n=6)
                    for i, s in enumerate(sw):
                        a, b = st.columns([1, 3])
                        with a:
                            st.markdown(swatch_html(s.hex, ""), unsafe_allow_html=True)
                        with b:
                            st.write(f"{s.hex} · {s.ratio:.0%}")
                            if st.button("取此色", key=f"style_pick_{i}"):
                                st.session_state["style_color"] = s.hex
                                st.session_state["style_picked"] = s.hex
                                st.rerun()
                    if "style_picked" in st.session_state:
                        st.success(f"已采用图像取色 {st.session_state['style_picked']}")
                except Exception as e:
                    st.error(f"图像解析失败：{e}")
        dynasty3 = st.selectbox("朝代（可选）", ["", *kb.DYNASTIES.keys()], key="dyn3")
        pigment_text = st.text_input(
            "已知颜料（可选，逗号分隔）", "石青,石绿",
            help="如 石青,石绿,朱砂；留空则仅凭色彩与朝代判断")
        run3 = st.button("识别风格", type="primary", key="run3s")
    with col2:
        st.markdown('<div class="gf-result-label">识别结果</div>', unsafe_allow_html=True)
        if run3:
            try:
                names = [p.strip() for p in pigment_text.split(",") if p.strip()]
                matches = identify_architecture_style(
                    color_hex=style_hex, dynasty=dynasty3 or None,
                    pigment_names=names, top_n=3,
                )
                for i, m in enumerate(matches, 1):
                    st.markdown(f"**{i}. {m.style}**　匹配度 `{m.score:.0%}`")
                    st.write(f"- 类别：{m.category}　等级：{m.rank}")
                    st.write(f"- 特征：{m.feature}")
                    st.write(f"- 常见于：{m.typical_use}")
                    st.caption(m.reasoning)
                    if i < len(matches):
                        st.divider()
            except Exception as e:
                st.error(f"识别失败：{e}")
        else:
            st.info("填写左侧参数后点击「识别风格」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 肆 修复决策
elif view == "restore":
    back_button()
    banner("potala.jpg", "肆 · 修复决策",
           "察其材、审其病、度其境，而后出修复之策")
    st.markdown(card_start(
        "肆 · 修复决策",
        "察颜料之性、病害之由、环境之宜，出修复之策，守最小干预之则。",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        pigment = st.selectbox("颜料", ["", *kb.PIGMENTS.keys()], key="pig")
        damage = st.selectbox("病害", list(kb.DAMAGE_RULES.keys()), key="dmg")
        hum = st.text_input("当前湿度", "75% RH")
        lux = st.text_input("当前照度", "")
        run4 = st.button("生成方案", type="primary", key="run4")
    with col2:
        st.markdown('<div class="gf-result-label">修复方案</div>', unsafe_allow_html=True)
        if run4:
            try:
                env = {}
                if hum:
                    env["湿度"] = hum
                if lux:
                    env["照度"] = lux
                r = decide_restoration(pigment=pigment or None, damage=damage,
                                       environment=env or None)
                st.markdown(f"**紧迫度：{r.urgency}**")
                st.write(r.summary)
                st.markdown("**建议工艺步骤**")
                for i, s in enumerate(r.steps, 1):
                    st.write(f"{i}. {s}")
                st.markdown("**建议材料**")
                st.write("、".join(r.materials))
                st.markdown("**环境控制**")
                st.json(r.environment)
                if r.risks:
                    st.warning("风险提示：" + "；".join(r.risks))
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「生成方案」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 伍 材质辨识与配材
elif view == "material":
    back_button()
    banner("foguang_temple.jpg", "伍 · 材质辨识与配材",
           "辨木石金彩之质，定修复配材之方")
    st.markdown(card_start(
        "伍 · 材质辨识与配材",
        "上传文物照片辨识其材质，再据病害给出修复所需材料与工艺要点。",
    ), unsafe_allow_html=True)

    st.markdown("#### 第一步 · 上传照片识别材质")
    up_mat = st.file_uploader(
        "上传木构 / 石刻 / 金属 / 彩画 / 地仗等照片（JPG / PNG）",
        type=["jpg", "jpeg", "png"], key="upload_material",
    )
    detected: List[str] = []
    if up_mat is not None:
        ic, rc = st.columns([1, 1])
        with ic:
            st.image(up_mat, caption="已上传图像", width="stretch")
        with rc:
            with st.spinner("正在辨析材质……"):
                try:
                    matches = identify_image_material(up_mat, top_n=3)
                    st.markdown("**材质候选（按置信度）**")
                    for i, mm in enumerate(matches, 1):
                        st.markdown(
                            f"**{i}. {mm.material}**　（`{mm.category}`，置信度 {mm.score:.0%}）")
                        st.markdown(swatch_html(mm.dominant_hex, mm.dominant_hex),
                                    unsafe_allow_html=True)
                        st.caption(mm.texture)
                        if i < len(matches):
                            st.divider()
                    detected = [m.material for m in matches]
                except Exception as e:
                    st.error(f"图像解析失败：{e}")

    meander()
    st.markdown("#### 第二步 · 据材质与病害给出修复配材")
    c1, c2 = st.columns([1, 1])
    with c1:
        mat_options = ["", *kb.MATERIALS.keys()]
        default_mat = detected[0] if detected else ""
        mat_index = mat_options.index(default_mat) if default_mat in mat_options else 0
        mat_name = st.selectbox("材质", mat_options, index=mat_index, key="mat_sel")
        default_diseases = []
        if mat_name:
            default_diseases = kb.MATERIALS[mat_name].common_diseases[:2]
        diseases = st.multiselect(
            "病害（可多选）", list(kb.DAMAGE_RULES.keys()),
            default=[d for d in default_diseases if d in kb.DAMAGE_RULES],
            key="mat_dis",
        )
        hum2 = st.text_input("当前湿度", "75% RH", key="mat_hum")
        lux2 = st.text_input("当前照度", "", key="mat_lux")
        run5 = st.button("生成修复配材方案", type="primary", key="run5")
    with c2:
        st.markdown('<div class="gf-result-label">修复配材方案</div>', unsafe_allow_html=True)
        if run5:
            if not mat_name:
                st.warning("请先上传照片识别材质，或在左侧下拉框选择材质。")
            else:
                try:
                    env = {}
                    if hum2:
                        env["湿度"] = hum2
                    if lux2:
                        env["照度"] = lux2
                    plan = recommend_repair_materials(mat_name, diseases=diseases,
                                                      environment=env or None)
                    st.markdown(f"**材质：{plan.material}**　紧迫度：`{plan.urgency}`")
                    st.markdown("**修复所需材料**")
                    st.write("、".join(plan.materials))
                    st.markdown("**工艺要点**")
                    st.info(plan.craft)
                    st.markdown("**修复禁忌**")
                    st.warning(plan.taboo)
                    st.markdown("**环境建议**")
                    st.json(plan.environment)
                    st.caption(plan.reasoning)
                except Exception as e:
                    st.error(f"计算失败：{e}")
        else:
            st.info("上传照片或在左侧选定材质与病害后点击「生成修复配材方案」")
    st.markdown("</div>", unsafe_allow_html=True)
