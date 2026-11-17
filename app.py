"""文物色彩考证与修复辅助系统 —— 古风界面。

部署到 Streamlit Community Cloud 时，入口文件选这个。
本地运行：streamlit run app.py
"""

import streamlit as st

from heritage_color import (
    auth_color, infer_pigment, decide_restoration,
    identify_architecture_style, extract_image_colors,
)
from heritage_color import knowledge_base as kb
from theme import apply_theme

st.set_page_config(
    page_title="文物色彩考证与修复辅助系统",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()

# ---------------------------------------------------------------- 页头
st.markdown(
    '<div class="gf-title">文物色彩考证与修复辅助系统</div>'
    '<div class="gf-subtitle">'
    '<span class="gf-seal">考色</span>'
    '以色彩证源流 · 以颜料推古法 · 以风格辨建制 · 以工艺续华章'
    '<span class="gf-seal">存真</span>'
    '</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs([
    "壹 · 色彩考证", "贰 · 颜料推演", "叁 · 建筑风格识别", "肆 · 修复决策",
])


def card_start(title: str, desc: str = ""):
    """开启一个古风卡片分区，返回 HTML 头。"""
    d = f'<div class="gf-card-desc">{desc}</div>' if desc else ""
    return (f'<div class="gf-card">'
            f'<div class="gf-card-title">{title}</div>{d}')


def swatch_html(hex_color: str, label: str = "") -> str:
    return (f'<span class="gf-swatch" style="background:{hex_color}"></span>'
            f'<span class="gf-swatch-label">{label or hex_color}</span>')


# ================================================================ 壹 色彩考证
with tab1:
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
                            c1, c2 = st.columns([1, 3])
                            with c1:
                                st.markdown(
                                    swatch_html(s.hex, ""), unsafe_allow_html=True)
                            with c2:
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
            "文献描述文本",
            "檐下青绿彩画，朱柱，间以金线",
            help="含朱/青/绿/金/红/白/黑等色彩关键词即可作为证据",
        )
        top_k = st.slider("候选颜料数量", 1, 5, 3, key="topk1")
        run1 = st.button("开始考证", type="primary", key="run1")

    with col2:
        st.markdown('<div class="gf-result-label">推断结果</div>',
                    unsafe_allow_html=True)
        if run1:
            try:
                r = auth_color(
                    observed_hex=observed,
                    dynasty=dynasty1 or None,
                    document_text=doc or None,
                    top_k=top_k,
                )
                st.markdown("**原始色（推求）**")
                st.markdown(swatch_html(r.original_hex, r.original_hex),
                            unsafe_allow_html=True)
                st.metric("置信度", f"{r.confidence:.0%}")
                st.markdown("**匹配颜料**")
                st.dataframe(r.matched_pigments, width="stretch")
                st.markdown("**推理依据**")
                st.info(r.reasoning)

                # 联动：由考证结果推断建筑风格
                pigment_names = [m["颜料"] for m in r.matched_pigments]
                styles = identify_architecture_style(
                    color_hex=r.original_hex,
                    dynasty=dynasty1 or None,
                    pigment_names=pigment_names,
                    top_n=3,
                )
                if styles:
                    st.markdown("**对应建筑风格（据色推求）**")
                    for m in styles:
                        st.write(
                            f"- **{m.style}**（{m.category}，匹配度 {m.score:.0%}）"
                            f"— {m.typical_use}"
                        )
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「开始考证」")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================ 贰 颜料推演
with tab2:
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
        st.markdown('<div class="gf-result-label">推演结果</div>',
                    unsafe_allow_html=True)
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
with tab3:
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
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            st.markdown(swatch_html(s.hex, ""), unsafe_allow_html=True)
                        with c2:
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
        st.markdown('<div class="gf-result-label">识别结果</div>',
                    unsafe_allow_html=True)
        if run3:
            try:
                names = [p.strip() for p in pigment_text.split(",") if p.strip()]
                matches = identify_architecture_style(
                    color_hex=style_hex,
                    dynasty=dynasty3 or None,
                    pigment_names=names,
                    top_n=3,
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
with tab4:
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
        st.markdown('<div class="gf-result-label">修复方案</div>',
                    unsafe_allow_html=True)
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

# ---------------------------------------------------------------- 页脚
st.divider()
st.markdown(
    '<div style="text-align:center;color:#8A7B60;font-size:12px;'
    'font-family:\'Songti SC\',SimSun,serif;letter-spacing:1px;">'
    '本工具所出结果为辅助参考，颜料考证与修复决策关乎文物安全，'
    '实际操作须由专业人员依据检测报告（XRF / 拉曼 / 显微）裁定。'
    '</div>',
    unsafe_allow_html=True,
)
