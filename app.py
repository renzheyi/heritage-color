"""heritage_color 的 Streamlit Web 界面。

部署到 Streamlit Community Cloud 时，入口文件就选这个。
本地运行：streamlit run app.py
"""

import streamlit as st

from heritage_color import auth_color, infer_pigment, decide_restoration
from heritage_color import knowledge_base as kb

st.set_page_config(
    page_title="文物色彩考证与修复辅助系统",
    layout="wide",
)

st.title("文物色彩考证与修复辅助系统")
st.caption("基于色彩科学 + 知识库 + 规则推理的可运行实现 · 结果仅供辅助参考")

tab1, tab2, tab3 = st.tabs(["① 色彩考证", "② 颜料推演", "③ 修复决策"])

# ---------------------------------------------------------------- 色彩考证
with tab1:
    st.header("色彩考证")
    st.write("根据现存残留色、文献记载与朝代风格，推断文物的原始色彩。")
    col1, col2 = st.columns([1, 1])
    with col1:
        observed = st.color_picker("现存残留色（实测）", "#6E2020")
        dynasty1 = st.selectbox("朝代", ["", *kb.DYNASTIES.keys()], index=5, key="dyn1")
        doc = st.text_area(
            "文献描述文本",
            "檐下青绿彩画，朱柱，间以金线",
            help="含朱/青/绿/金/红/白/黑等色彩关键词即可作为证据",
        )
        top_k = st.slider("候选颜料数量", 1, 5, 3, key="topk1")
        run1 = st.button("开始考证", type="primary", key="run1")
    with col2:
        st.markdown("**推断原始色**")
        if run1:
            try:
                r = auth_color(
                    observed_hex=observed,
                    dynasty=dynasty1 or None,
                    document_text=doc or None,
                    top_k=top_k,
                )
                st.color_picker("原始色（推断）", r.original_hex, disabled=True, key="orig")
                st.metric("置信度", f"{r.confidence:.0%}")
                st.markdown("**匹配颜料**")
                st.dataframe(r.matched_pigments, use_container_width=True)
                st.markdown("**推理说明**")
                st.info(r.reasoning)
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「开始考证」")

# ---------------------------------------------------------------- 颜料推演
with tab2:
    st.header("颜料推演")
    st.write("给定目标颜色，反推可能使用的颜料与配比。")
    col1, col2 = st.columns([1, 1])
    with col1:
        target = st.color_picker("目标颜色", "#2E9070", key="target")
        dynasty2 = st.selectbox("朝代约束", ["", *kb.DYNASTIES.keys()], index=5, key="dyn2")
        allow_mix = st.checkbox("允许混合颜料配方", value=True)
        top_n = st.slider("候选配方数", 1, 5, 3, key="topn2")
        run2 = st.button("开始推演", type="primary", key="run2")
    with col2:
        if run2:
            try:
                r = infer_pigment(target, dynasty=dynasty2 or None,
                                  allow_mixture=allow_mix, top_n=top_n)
                best = r["best_formula"]
                st.success(f"最优配方：{best['pigments']} → {best['result_hex']}"
                           f"（色差 {best['delta_e']}）")
                st.color_picker("配方复现色", best["result_hex"], disabled=True, key="mixres")
                st.markdown("**单颜料候选**")
                st.dataframe(r["single_pigments"], use_container_width=True)
                st.markdown("**混合配方候选**")
                if r["mixtures"]:
                    st.dataframe(r["mixtures"], use_container_width=True)
                st.info(r["reasoning"])
                st.caption(r["note"])
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写左侧参数后点击「开始推演」")

# ---------------------------------------------------------------- 修复决策
with tab3:
    st.header("修复决策")
    st.write("根据颜料、病害与环境，输出结构化修复建议。")
    col1, col2 = st.columns([1, 1])
    with col1:
        pigment = st.selectbox("颜料", ["", *kb.PIGMENTS.keys()], key="pig")
        damage = st.selectbox("病害", list(kb.DAMAGE_RULES.keys()), key="dmg")
        hum = st.text_input("当前湿度", "75% RH")
        lux = st.text_input("当前照度", "")
        run3 = st.button("生成方案", type="primary", key="run3")
    with col2:
        if run3:
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

st.divider()
st.caption(
    "注意：本工具输出为辅助参考，颜料考证与修复决策涉及文物安全，"
    "实际操作须由专业人员依据检测报告（XRF / 拉曼 / 显微）确认。"
)
