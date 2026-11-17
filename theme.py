"""古风主题：宣纸底色 + 朱砂 / 黛青 / 鎏金配色，注入到 Streamlit 页面。

集中放 CSS，保持 app.py 只管业务逻辑。用 st.markdown(unsafe_allow_html=True)
注入；由于 Streamlit DOM 结构，选择器用属性选择器兼顾版本差异。
"""

GUOFENG_CSS = """
<style>
/* ---- 全局宣纸底色与墨色文字 ---- */
[data-testid="stAppViewContainer"] {
    background-color: #F5EFE1;
    background-image:
        radial-gradient(circle at 12% 18%, rgba(160,120,70,0.05) 0 2px, transparent 2px),
        radial-gradient(circle at 78% 62%, rgba(160,120,70,0.045) 0 2px, transparent 2px);
    background-size: 90px 90px, 130px 130px;
}
[data-testid="stApp"] { color: #2E2A24; }
h1, h2, h3, [data-testid="stHeader"] { color: #6E2B23 !important; }

/* ---- 主标题：宋体 + 朱红 + 底部金线 ---- */
.gf-title {
    font-family: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
    font-size: 40px; font-weight: 700; letter-spacing: 6px;
    color: #7A2E24; text-align: center;
    padding: 18px 0 10px; margin: 0;
    border-bottom: 2px solid #B08D4F;
    text-shadow: 1px 1px 0 rgba(255,255,255,0.6);
}
.gf-subtitle {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 15px; letter-spacing: 3px; color: #7A6A50;
    text-align: center; margin: 10px 0 22px;
}
.gf-seal {
    display: inline-block; font-family: "Songti SC", "SimSun", serif;
    background: #9E3329; color: #F7EFE0; font-size: 14px;
    padding: 4px 8px; border-radius: 3px; letter-spacing: 2px;
    margin: 0 4px; box-shadow: 2px 2px 0 rgba(0,0,0,0.12);
}

/* ---- 卡片式分区：米色宣纸卡 + 细边框 ---- */
.gf-card {
    background: #FBF6EA;
    border: 1px solid #D9C8A6;
    border-left: 4px solid #9E3329;
    border-radius: 4px;
    padding: 18px 20px 14px;
    margin: 8px 0 18px;
    box-shadow: 0 2px 6px rgba(90,70,40,0.08);
}
.gf-card-title {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 20px; font-weight: 700; color: #6E2B23;
    letter-spacing: 2px; margin: 0 0 4px;
}
.gf-card-desc { font-size: 13px; color: #7A6A50; margin-bottom: 12px; }

/* ---- 标签页：仿古书签 ---- */
[data-baseweb="tab-list"] {
    gap: 6px; border-bottom: 2px solid #B08D4F;
}
[data-baseweb="tab"] {
    font-family: "Songti SC", "SimSun", serif !important;
    font-size: 16px !important; letter-spacing: 2px;
    color: #6E5C42 !important;
    background: #EDE2CC !important;
    border: 1px solid #D9C8A6 !important;
    border-bottom: none !important;
    border-radius: 4px 4px 0 0 !important;
    padding: 10px 18px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #9E3329 !important; color: #F7EFE0 !important;
    border-color: #9E3329 !important;
}

/* ---- 主按钮：朱砂印章色 ---- */
[data-testid="stButton"] button {
    font-family: "Songti SC", "SimSun", serif;
    background: #9E3329 !important; color: #F7EFE0 !important;
    border: 1px solid #7A2E24 !important; border-radius: 3px !important;
    letter-spacing: 2px; font-size: 15px !important;
}
[data-testid="stButton"] button:hover { background: #7A2E24 !important; }

/* ---- 色卡 swatch ---- */
.gf-swatch {
    display: inline-block; width: 46px; height: 46px;
    border: 2px solid #FBF6EA; border-radius: 3px;
    box-shadow: 0 0 0 1px #B8A986, 1px 2px 4px rgba(0,0,0,0.2);
    vertical-align: middle; margin-right: 8px;
}
.gf-swatch-label {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 15px; color: #4A4034; letter-spacing: 1px;
}

/* ---- 结果区标题 ---- */
.gf-result-label {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 17px; font-weight: 700; color: #1F5C57;
    letter-spacing: 2px; border-bottom: 1px dashed #9CB3AF;
    padding-bottom: 4px; margin: 12px 0 8px;
}

/* ---- 信息框去现代化 ---- */
[data-testid="stAlert"] {
    background: #F3E9D2 !important;
    border: 1px solid #D9C8A6 !important;
    border-radius: 3px !important;
}
.stCaption { color: #8A7B60 !important; }
hr { border-color: #D9C8A6 !important; }

/* ---- 门户导航方块 ---- */
.gf-nav-card {
    background: #FBF6EA;
    border: 1px solid #D9C8A6;
    border-top: 4px solid #9E3329;
    border-radius: 6px 6px 0 0;
    padding: 20px 18px 16px;
    height: 168px;
    box-shadow: 0 3px 10px rgba(90,70,40,0.12);
    display: flex; flex-direction: column; justify-content: center;
}
.gf-nav-num {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 34px; line-height: 1; color: #9E3329;
    letter-spacing: 2px; margin-bottom: 8px;
}
.gf-nav-title {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 22px; font-weight: 700; color: #6E2B23;
    letter-spacing: 3px; margin-bottom: 6px;
}
.gf-nav-desc { font-size: 13px; color: #7A6A50; line-height: 1.6; }
.gf-back { margin-bottom: 8px; }
</style>
"""


def apply_theme() -> None:
    """注入古风 CSS。需在 set_page_config 之后、其它组件之前调用。"""
    import streamlit as st
    st.markdown(GUOFENG_CSS, unsafe_allow_html=True)
