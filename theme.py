"""古风主题：宣纸底 + 朱砂 / 黛青 / 鎏金，注入到 Streamlit 页面。

纹饰体系（均为纯 CSS / SVG data-uri，无需图片文件，云端开箱即用）：
  · 万字回纹铺底 —— 若隐若现的"万字不到头"
  · 四角祥云卷草 —— 卡片四角各一枚，朱砂描边
  · 回纹金线带 —— 页首、页脚、门牌顶部
  · 瓦当徽记 —— 标题两侧的圆形印章
  · 双线金框 —— 图片横幅
  · 菱形点缀 —— 结果标签与分隔带

集中放 CSS，保持 app.py 只管业务逻辑。
"""

GUOFENG_CSS = """
<style>
/* ============ 1. 全局宣纸底 + 万字回纹暗纹 ============ */
[data-testid="stAppViewContainer"] {
    background-color: #F4ECD8;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48' viewBox='0 0 48 48'><path d='M8 8 H40 V40 H8 V8 M16 16 H32 V32 H16 Z M24 8 V16 M24 32 V40 M8 24 H16 M32 24 H40' fill='none' stroke='%23B08D4F' stroke-opacity='0.11' stroke-width='1'/></svg>"),
        radial-gradient(circle at 15% 20%, rgba(160,120,70,0.06) 0 2px, transparent 2px),
        radial-gradient(circle at 80% 65%, rgba(160,120,70,0.05) 0 2px, transparent 2px);
    background-size: 48px 48px, 90px 90px, 130px 130px;
}
[data-testid="stApp"] { color: #2E2A24; font-family: "Songti SC", SimSun, serif; }
h1, h2, h3, [data-testid="stHeader"] { color: #6E2B23 !important; }

/* 页首 / 页脚回纹金线带 */
.gf-top-rule, .gf-bottom-rule {
    height: 12px; margin: 0 0 6px;
    background-color: #7A2E24;
    background-image:
        repeating-linear-gradient(90deg,
            transparent 0, transparent 8px,
            rgba(247,239,224,0.85) 8px, rgba(247,239,224,0.85) 10px,
            transparent 10px, transparent 18px),
        linear-gradient(180deg, transparent 0 4px, rgba(176,141,79,0.9) 4px 6px, transparent 6px);
    border-top: 1px solid #B08D4F; border-bottom: 1px solid #B08D4F;
    border-radius: 2px; opacity: 0.85;
}
.gf-bottom-rule { margin: 16px 0 4px; }

/* ============ 2. 主标题：云纹双翼 + 金线 ============ */
.gf-title {
    position: relative;
    font-family: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
    font-size: 40px; font-weight: 700; letter-spacing: 8px;
    color: #7A2E24; text-align: center;
    padding: 16px 0 10px; margin: 0;
    border-bottom: 2px solid #B08D4F;
    text-shadow: 1px 1px 0 rgba(255,255,255,0.7);
}
.gf-title::before, .gf-title::after {
    content: ""; position: absolute; top: 14px; width: 64px; height: 40px;
    background-repeat: no-repeat; background-size: contain; opacity: 0.75;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 50'><path d='M2 40 Q2 18 24 18 Q40 18 40 32 Q40 44 30 44 Q22 44 22 36 M40 40 Q40 22 58 22 Q74 22 74 40' fill='none' stroke='%239E3329' stroke-width='3'/><circle cx='30' cy='32' r='3' fill='%23B08D4F'/></svg>");
}
.gf-title::before { left: 2%; }
.gf-title::after { right: 2%; transform: scaleX(-1); }

.gf-subtitle {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 15px; letter-spacing: 3px; color: #7A6A50;
    text-align: center; margin: 10px 0 22px;
}

/* ============ 3. 瓦当徽记 / 印章 ============ */
.gf-wadang {
    display: inline-flex; align-items: center; justify-content: center;
    width: 62px; height: 62px; border-radius: 50%;
    background: #9E3329; color: #F7EFE0;
    border: 3px double #F7EFE0; outline: 2px solid #9E3329;
    font-family: "Songti SC", SimSun, serif; font-size: 20px; font-weight: 700;
    box-shadow: 2px 3px 6px rgba(0,0,0,0.18);
    position: relative;
}
.gf-wadang::after {
    content: ""; position: absolute; inset: 6px; border-radius: 50%;
    border: 1px dashed rgba(247,239,224,0.55);
}
.gf-seal {
    display: inline-block; font-family: "Songti SC", "SimSun", serif;
    background: #9E3329; color: #F7EFE0; font-size: 14px;
    padding: 4px 8px; border-radius: 3px; letter-spacing: 2px;
    margin: 0 4px; box-shadow: 2px 2px 0 rgba(0,0,0,0.12);
    border: 1px solid #7A2E24;
}

/* ============ 4. 卡片：四角祥云 + 上下金线 + 朱印标题 ============ */
.gf-ornate-card {
    position: relative;
    background-color: #FBF6EA;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%239E3329' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23B08D4F'/></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='scale(-1,1) translate(-60,0)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%239E3329' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23B08D4F'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='scale(1,-1) translate(0,-60)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%239E3329' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23B08D4F'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='rotate(180 30 30)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%239E3329' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23B08D4F'/></g></svg>");
    background-repeat: no-repeat;
    background-position: top left, top right, bottom left, bottom right;
    background-size: 46px 46px;
    border: 1px solid #D9C8A6;
    border-top: 2px solid #9E3329;
    border-bottom: 2px solid #B08D4F;
    border-radius: 4px;
    padding: 24px 24px 18px; margin: 10px 0 18px;
    box-shadow: 0 2px 8px rgba(90,70,40,0.10);
}
.gf-ornate-card::before {
    content: ""; position: absolute; left: 0; right: 0; top: 0; height: 6px;
    background-image: repeating-linear-gradient(90deg,
        #9E3329 0, #9E3329 6px, transparent 6px, transparent 12px);
    opacity: 0.35;
}
.gf-card-title {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 20px; font-weight: 700; color: #6E2B23;
    letter-spacing: 2px; margin: 0 0 4px;
    padding-left: 30px; position: relative;
}
.gf-card-title::before {
    content: "印"; position: absolute; left: 0; top: 1px;
    width: 22px; height: 22px; line-height: 22px; text-align: center;
    font-size: 12px; color: #F7EFE0; background: #9E3329; border-radius: 2px;
    letter-spacing: 0;
}
.gf-card-desc { font-size: 13px; color: #7A6A50; margin-bottom: 12px; }

/* ============ 5. 门牌方块：四角云纹 + 回纹冠 + 编号印 ============ */
.gf-nav-card {
    position: relative;
    background-color: #FBF6EA;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23B08D4F' stroke-width='2'/></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='scale(-1,1) translate(-40,0)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23B08D4F' stroke-width='2'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='scale(1,-1) translate(0,-40)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23B08D4F' stroke-width='2'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='rotate(180 20 20)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23B08D4F' stroke-width='2'/></g></svg>");
    background-repeat: no-repeat;
    background-position: top left, top right, bottom left, bottom right;
    background-size: 28px 28px;
    border: 1px solid #D9C8A6;
    border-top: 4px solid #9E3329;
    border-radius: 6px 6px 2px 2px;
    padding: 20px 18px 16px; height: 168px;
    box-shadow: 0 3px 10px rgba(90,70,40,0.12);
    display: flex; flex-direction: column; justify-content: center;
}
.gf-nav-card::before {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 5px;
    background-image: repeating-linear-gradient(90deg,
        transparent 0, transparent 6px, #B08D4F 6px, #B08D4F 8px);
    opacity: 0.6;
}
.gf-nav-card::after {
    content: "❖"; position: absolute; top: 6px; right: 10px;
    color: #9E3329; font-size: 14px;
}
.gf-nav-num {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 26px; line-height: 42px; color: #F7EFE0;
    letter-spacing: 1px; margin-bottom: 8px;
    display: inline-block; width: 42px; height: 42px;
    text-align: center; background: #9E3329;
    border: 1px solid #7A2E24; border-radius: 3px;
    box-shadow: 2px 2px 0 rgba(0,0,0,0.12);
    flex-shrink: 0;
}
.gf-nav-title {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 22px; font-weight: 700; color: #6E2B23;
    letter-spacing: 3px; margin-bottom: 6px;
}
.gf-nav-desc { font-size: 13px; color: #7A6A50; line-height: 1.6; }

/* ============ 6. 回纹带 / 云纹分隔 ============ */
.gf-meander {
    height: 14px; margin: 14px 0;
    background-color: #9E3329;
    background-image:
        repeating-linear-gradient(90deg,
            transparent 0, transparent 8px,
            rgba(247,239,224,0.85) 8px, rgba(247,239,224,0.85) 10px,
            transparent 10px, transparent 18px),
        linear-gradient(180deg, transparent 0 5px, #B08D4F 5px 9px, transparent 9px);
    opacity: 0.8; border-radius: 2px;
}
.gf-cloud-divider {
    text-align: center; color: #9E3329; font-size: 18px;
    letter-spacing: 14px; margin: 2px 0 14px; opacity: 0.9;
    position: relative;
}
.gf-cloud-divider::before, .gf-cloud-divider::after {
    content: ""; position: absolute; top: 50%; width: 26%; height: 1px;
    background: linear-gradient(90deg, transparent, #B08D4F, transparent);
}
.gf-cloud-divider::before { left: 4%; }
.gf-cloud-divider::after { right: 4%; transform: scaleX(-1); }

/* ============ 7. 图片横幅：双金线 ============ */
.gf-banner {
    position: relative; border-radius: 4px; overflow: hidden;
    border: 1px solid #B08D4F; outline: 1px solid #9E3329;
    outline-offset: 3px; margin: 8px 0 20px;
    box-shadow: 0 3px 12px rgba(90,70,40,0.15);
    background: #7A2E24;
}
.gf-banner img { display: block; width: 100%; height: 220px; object-fit: cover; }
.gf-banner-cap {
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 26px 20px 10px;
    background: linear-gradient(transparent, rgba(43,38,30,0.82));
    color: #F5EFE1; font-family: "Songti SC", SimSun, serif;
    font-size: 16px; letter-spacing: 4px;
    border-top: 1px solid rgba(176,141,79,0.7);
}
.gf-banner-cap small {
    display: block; font-size: 11px; letter-spacing: 1px;
    opacity: 0.85; margin-top: 3px;
}

/* ============ 8. 结果区标签 / 色卡 / 按钮 ============ */
.gf-result-label {
    font-family: "Songti SC", "SimSun", serif;
    font-size: 17px; font-weight: 700; color: #1F5C57;
    letter-spacing: 2px; border-bottom: 1px dashed #9CB3AF;
    padding-bottom: 4px; margin: 12px 0 8px;
}
.gf-result-label::before { content: "◆ "; color: #B08D4F; font-size: 12px; }
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
[data-testid="stButton"] button {
    font-family: "Songti SC", "SimSun", serif;
    background: #9E3329 !important; color: #F7EFE0 !important;
    border: 1px solid #7A2E24 !important; border-radius: 3px !important;
    letter-spacing: 2px; font-size: 15px !important;
}
[data-testid="stButton"] button:hover { background: #7A2E24 !important; }
[data-testid="stAlert"] {
    background: #F3E9D2 !important;
    border: 1px solid #D9C8A6 !important;
    border-left: 4px solid #9E3329 !important;
    border-radius: 3px !important;
}
.stCaption { color: #8A7B60 !important; }
hr { border-color: #D9C8A6 !important; }
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid #B08D4F; }
[data-baseweb="tab"] {
    font-family: "Songti SC", "SimSun", serif !important;
    font-size: 16px !important; letter-spacing: 2px;
    color: #6E5C42 !important; background: #EDE2CC !important;
    border: 1px solid #D9C8A6 !important; border-bottom: none !important;
    border-radius: 4px 4px 0 0 !important; padding: 10px 18px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #9E3329 !important; color: #F7EFE0 !important;
    border-color: #9E3329 !important;
}

/* 小标题上的朱砂方印 */
.gf-step-title {
    font-family: "Songti SC", SimSun, serif; font-size: 16px;
    color: #6E2B23; letter-spacing: 2px; margin: 6px 0 10px;
    padding-left: 26px; position: relative;
}
.gf-step-title::before {
    content: "壹"; position: absolute; left: 0; top: 0;
    width: 20px; height: 20px; line-height: 20px; text-align: center;
    font-size: 11px; color: #F7EFE0; background: #9E3329;
    border-radius: 2px; letter-spacing: 0;
}
</style>
"""


def apply_theme() -> None:
    """注入古风 CSS。需在 set_page_config 之后、其它组件之前调用。"""
    import streamlit as st
    st.markdown(GUOFENG_CSS, unsafe_allow_html=True)
