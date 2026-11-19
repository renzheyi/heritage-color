"""文物色彩考证与修复辅助系统 —— 古风界面（门户导航式）。

首页为五个独立方块，点击进入对应程序；每个程序页可返回首页。
部署到 Streamlit Community Cloud 时，入口文件选这个。
本地运行：streamlit run app.py
"""

import os
from typing import List
from html import escape as _esc
import streamlit as st

# 注意：set_page_config 必须是第一个 Streamlit 命令，放在任何 st.* 之前。
st.set_page_config(
    page_title="考色 KAOSE · 文物色彩智能考证平台",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 兼容云端旧缓存：Streamlit Cloud 偶尔会只更新 app.py 而未刷新包文件，
# 导致 from heritage_color import ... 抛 ImportError。这里显式检查并给出
# 可操作的提示，而不是显示被脱敏的红色报错页。
try:
    import heritage_color as _hc
    from heritage_color.heritages import HERITAGES, get_heritage
    _REQUIRED = (
        "auth_color", "infer_pigment", "decide_restoration",
        "identify_architecture_style", "extract_image_colors",
        "identify_image_material", "recommend_repair_materials",
        "polish_text",
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
    polish_text = _hc.polish_text
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

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 数智中枢为可选增强：即使 Streamlit Cloud 只刷新了 app.py、包文件仍是旧缓存，
# 主站五个模块照常可用，只是暂不显示技术增强面板（避免整站红页）。
# 注意包内 __init__ 已把三个增强模块软导出（缺失时为 None），这里双重保险。
try:
    from heritage_color import spectral as sp, uncertainty as unc, viz
    _TECH_OK = bool(sp and unc and viz)
except Exception:
    _TECH_OK = False


def _background_uri() -> str:
    """把描边抠主体、虚化后的古建筑图转成 data URI，作为页面淡淡衬底。"""
    path = os.path.join(ASSETS, "bg_arch.jpg")
    if not os.path.exists(path):
        return ""
    import base64
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


# Streamlit Cloud 偶发只刷新 app.py、theme.py 仍是旧缓存（旧版 apply_theme 无参数）。
# 这里按实际签名调用，新旧版本都能工作，避免 TypeError 红页。
import inspect as _inspect
if "background_uri" in _inspect.signature(apply_theme).parameters:
    apply_theme(_background_uri())
else:
    apply_theme()

# ---------------------------------------------------------------- 站内跳转配置
# 发布平台要求访问链接带分享码：裸 "?view=xxx" 会返回 403。
# 因此所有 HTML 站内链接都沿用当前 URL 上的 sharecode 等参数（view/product 除外）。
from urllib.parse import quote as _urlquote


def _build_share_qs() -> str:
    parts = []
    for _k, _v in st.query_params.items():
        if _k in ("view", "product"):
            continue
        _val = _v if isinstance(_v, str) else (_v[0] if _v else "")
        if _val:
            parts.append(f"{_urlquote(str(_k))}={_urlquote(str(_val))}")
    return ("&" + "&".join(parts)) if parts else ""


_QS = _build_share_qs()

# 首页只放板块入口；各板块的具体内容在这些独立页面里呈现。
# (编号, 英文标签, 标题, 说明, commerce 中的渲染函数名)
_BOARD_PAGES = {
    "solutions": ("02", "INDUSTRY SOLUTIONS", "面向真实文保场景的解决方案",
                  "不同机构、不同阶段的色彩工作，需要不同的证据链与交付物。", "solutions"),
    "moat": ("03", "TECHNOLOGY MOAT", "技术壁垒 · 数智中枢",
             "以色彩科学与概率推断为内核，而非滤镜式上色；每条结论都可回到物理与文献证据。", "tech_moat"),
    "pricing": ("04", "SERVICE PLANS", "服务方案",
                "从在线试用到机构私有化部署，按项目规模与数据合规要求灵活选择。", "pricing"),
    "process": ("05", "COOPERATION PROCESS", "合作流程",
                "四步完成从需求沟通到交付上线，全程有明确的验收口径。", "process"),
    "faq": ("06", "FREQUENTLY ASKED QUESTIONS", "常见问题",
            "关于结论效力、数据合规与部署方式，先把边界说清楚。", "faq"),
}

# Streamlit Cloud 偶发只刷新 app.py、theme.py 仍是旧缓存。这里把新版关键样式
# 随 app.py 一起注入：圆周布局、去外部圆环、图标尺寸、门牌高度、全新朱砂鎏金配色，
# 任何缓存状态下都能正确显示，不依赖 theme.py 是否刷新。
_BG_URI_FOR_PATCH = _background_uri()
_CRITICAL_CSS = f"""
<style>
:root {{
    --gf-red: #C4322B; --gf-red-deep: #8E1F1A; --gf-red-ink: #6E1713;
    --gf-gold: #D4AF37; --gf-gold-deep: #A8801F;
    --gf-paper: #F7EEDC; --gf-card: #FDF8EC; --gf-teal: #126A66; --gf-ink: #2B1D16;
}}
[data-testid="stAppViewContainer"] {{
    background-color: #F7EEDC !important;
    background-image:
        radial-gradient(circle at 50% 42%, rgba(212,175,55,0.16), transparent 58%),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'><path d='M8 8 H47 V47 H8 V8 M15 15 H40 V40 H15 Z M24 8 V15 M24 40 V47 M8 24 H15 M40 24 H47 M27 27 H33 V33 H27 Z' fill='none' stroke='%23A8801F' stroke-opacity='0.10' stroke-width='1'/></svg>"),
        linear-gradient(rgba(247,238,220,0.26), rgba(228,210,172,0.30)),
        url("{_BG_URI_FOR_PATCH}") !important;
    background-size: cover, 56px 56px, cover, cover !important;
    background-position: center, center, center, center center !important;
    background-attachment: fixed, fixed, fixed, fixed !important;
    background-repeat: no-repeat, repeat, no-repeat, no-repeat !important;
}}
h1, h2, h3, [data-testid="stHeader"] {{ color: #8E1F1A !important; }}
.gf-title {{ color: #8E1F1A !important; border-bottom-color: #D4AF37 !important; }}
.gf-subtitle {{ color: #6E5C42 !important; }}
.gf-top-rule, .gf-bottom-rule, .gf-meander {{
    background-color: #8E1F1A !important; border-color: #D4AF37 !important;
}}

/* ===== 五门环形舞台：正上 / 右上 / 右下 / 左下 / 左上，间隔 72° ===== */
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) {{
    position: relative;
    flex: 0 0 auto !important;
    --r: clamp(195px, 21vw, 225px);
    --rx: clamp(205px, 24vw, 255px);
    width: 100%; max-width: 1100px;
    height: calc(var(--r) + var(--r) + 290px);
    margin: -40px auto 6px !important;
}}
/* 取消舞台内部容器的定位上下文，让圆心与门牌相对舞台绝对定位 */
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stElementContainer"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stMarkdown"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stMarkdownContainer"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stLayoutWrapper"] {{ position: static !important; }}
.gf-ring-stage-marker, .gf-ring-node-marker {{ display: none !important; }}
.gf-ring-center {{
    position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 2;
}}
/* 去除「考色」外部圆环，只留圆形球体本身 */
.gf-orbit-ring, .gf-orbit-wrap::before, .gf-orbit-wrap::after,
.gf-ring-track, .gf-ring-track-inner {{ display: none !important; }}
.gf-ring-center .gf-orbit-core {{
    position: relative;
    width: 132px !important; height: 132px !important; font-size: 16px !important;
    background:
        radial-gradient(circle at 32% 26%, rgba(255,244,218,0.65), rgba(255,244,218,0) 44%),
        radial-gradient(circle at 68% 76%, rgba(80,12,10,0.55), rgba(80,12,10,0) 56%),
        radial-gradient(circle at 38% 32%, #E05A4A, #C4322B 58%, #7E1712 100%) !important;
    border: 3px double #F3D98A !important;
    box-shadow:
        inset -9px -11px 24px rgba(70,10,8,0.55),
        inset 7px 7px 20px rgba(255,238,200,0.30),
        0 0 0 6px rgba(212,175,55,0.18),
        0 10px 30px rgba(142,31,26,0.45) !important;
}}
.gf-ring-center .gf-orbit-core small {{ color: #F3D98A !important; }}
.gf-ring-center .gf-orbit-core::before {{
    content: ""; position: absolute; left: 28px; top: 22px;
    width: 32px; height: 19px; border-radius: 50%;
    background: radial-gradient(ellipse, rgba(255,248,232,0.72), rgba(255,248,232,0) 70%);
    transform: rotate(-28deg); pointer-events: none;
}}

div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{
    position: absolute; width: 224px; z-index: 3;
    transform: translate(-50%, -50%);
    transition: transform .28s cubic-bezier(.34,1.56,.64,1);
}}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n1):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{ left: 50%; top: calc(50% - var(--r)); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n2):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{ left: calc(50% + var(--rx) * 0.951); top: calc(50% - var(--r) * 0.309); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n3):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{ left: calc(50% + var(--rx) * 0.588); top: calc(50% + var(--r) * 0.809); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n4):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{ left: calc(50% - var(--rx) * 0.588); top: calc(50% + var(--r) * 0.809); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n5):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{ left: calc(50% - var(--rx) * 0.951); top: calc(50% - var(--r) * 0.309); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {{ z-index: 6; }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n1):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {{ transform: translate(-50%, calc(-50% - 8px)) scale(1.03); }}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n2):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n3):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n4):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n5):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {{ transform: translate(-50%, calc(-50% - 8px)) scale(1.03); }}

.gf-nav-card {{
    box-sizing: border-box !important; width: 100% !important;
    height: 158px !important; min-height: 158px; max-height: 158px;
    overflow: hidden; background-color: #FDF8EC !important;
    border-color: #D4AF37 !important; border-top-color: #C4322B !important;
    border-bottom-color: #D4AF37 !important;
}}
.gf-nav-num {{ background: #C4322B !important; border-color: #8E1F1A !important; }}
.gf-nav-title {{ color: #8E1F1A !important; }}
/* 推演/考证结果横向并排，窄屏才回退单列 */
.gf-result-panel {{
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
    gap: 12px 16px !important; align-items: start !important;
}}
@media (max-width: 700px) {{
    .gf-result-panel {{ grid-template-columns: 1fr !important; }}
}}
/* 风格候选卡片横向并排，窄屏回退单列 */
.gf-sec-wide {{ grid-column: 1 / -1 !important; }}
.gf-style-list {{
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
    gap: 10px 14px !important; align-items: start !important;
}}
.gf-style-item {{
    box-sizing: border-box !important; padding: 10px 12px !important;
    background: rgba(255,243,220,0.55) !important; border: 1px solid #E0CB95 !important;
    border-radius: 4px !important;
}}
@media (max-width: 700px) {{
    .gf-style-list {{ grid-template-columns: 1fr !important; }}
}}
/* 表头多为英文字段名，改用清晰黑体，避免行楷连笔看不清 */
.gf-table th {{
    font-family: "Noto Sans CJK SC","Microsoft YaHei","PingFang SC",Arial,sans-serif !important;
    font-style: normal !important; font-weight: 700 !important;
    font-size: 16px !important; letter-spacing: 0.5px !important;
}}
.gf-nav-icon {{
    position: absolute !important; right: 12px !important; top: 12px !important;
    width: 34px !important; height: 34px !important;
    object-fit: contain; pointer-events: none;
}}
[data-testid="stButton"] button {{
    background: linear-gradient(180deg, #D9483B, #A82821) !important;
    border: 1px solid #D4AF37 !important;
    box-shadow: 0 4px 12px rgba(142,31,26,0.38) !important;
}}
[data-testid="stButton"] button:hover {{
    background: linear-gradient(180deg, #C4322B, #8E1F1A) !important;
    box-shadow: 0 0 0 1px #F3D98A, 0 8px 20px rgba(142,31,26,0.48) !important;
}}

@media (max-width: 760px) {{
    div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) {{
        height: auto; margin-top: 0 !important; display: flex; flex-direction: column; align-items: center; gap: 14px;
    }}
    .gf-ring-center {{ position: relative; left: auto; top: auto; transform: none; order: -1; }}
    div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {{
        position: relative; left: auto !important; top: auto !important;
        transform: none !important; width: min(100%, 320px);
    }}
    div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {{ transform: translateY(-6px) scale(1.02) !important; }}
}}

/* ===== 古建照片轮播：随 app.py 注入，防 Cloud 缓存旧 theme ===== */
.gf-carousel-hint {{
    text-align: center; margin: 6px 0 0;
    font-family: var(--gf-song) !important; font-size: 16px !important;
    letter-spacing: 1px !important; color: #6E5C42 !important;
}}
.gf-carousel {{
    position: relative; overflow: hidden;
    width: 100%; margin: 16px auto 20px; padding: 10px 0;
    border: 1px solid #D4AF37 !important; border-radius: 6px !important;
    background: rgba(253,248,236,0.55) !important;
    box-shadow: 0 6px 22px rgba(142,31,26,0.18), inset 0 0 0 4px rgba(212,175,55,0.10) !important;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
    mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
    animation: gfCarouselIn 0.9s ease-out both !important;
}}
@keyframes gfCarouselIn {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.gf-carousel-track {{
    display: flex !important; width: max-content !important;
    animation: gfCarouselScroll 52s linear infinite !important;
}}
.gf-carousel:hover .gf-carousel-track,
.gf-carousel:focus-within .gf-carousel-track {{ animation-play-state: paused !important; }}
@keyframes gfCarouselScroll {{
    from {{ transform: translateX(0); }}
    to   {{ transform: translateX(-50%); }}
}}
.gf-slide {{
    position: relative !important; flex: 0 0 auto !important;
    width: 348px !important; height: 226px !important; margin-right: 18px !important;
    border-radius: 4px !important; overflow: hidden !important;
    text-decoration: none !important; color: inherit !important;
    border: 1px solid #E0CB95 !important; background: #3E372D !important;
    box-shadow: 0 3px 12px rgba(62,55,45,0.22) !important;
    transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s !important;
}}
.gf-slide:hover {{
    transform: translateY(-6px) scale(1.02) !important;
    box-shadow: 0 10px 26px rgba(142,31,26,0.42) !important; z-index: 2;
}}
.gf-slide img {{
    width: 100% !important; height: 100% !important; object-fit: cover !important;
    display: block !important; filter: saturate(1.06) contrast(1.04);
    transition: transform .5s ease !important;
}}
.gf-slide:hover img {{ transform: scale(1.06) !important; }}
.gf-slide-cap {{
    position: absolute !important; left: 0; right: 0; bottom: 0;
    padding: 30px 14px 12px !important; pointer-events: none;
    display: flex !important; flex-direction: column !important; gap: 3px !important;
    background: linear-gradient(180deg, rgba(28,20,14,0) 0%, rgba(28,20,14,0.72) 42%, rgba(28,20,14,0.94) 100%) !important;
}}
.gf-slide-title {{
    font-family: var(--gf-xing) !important; color: #F3D98A !important;
    font-size: 16px !important; font-weight: 700 !important; letter-spacing: 2px !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.6);
}}
.gf-slide-sub {{
    font-family: var(--gf-song) !important; color: #FDF8EC !important;
    font-size: 16px !important; line-height: 1.45 !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.75);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.gf-slide-more {{
    margin-top: 3px; font-family: var(--gf-song) !important;
    font-size: 16px !important; letter-spacing: 1px !important; color: #F3D98A !important;
}}
@media (max-width: 760px) {{
    .gf-slide {{ width: 268px !important; height: 196px !important; }}
    .gf-slide-title {{ font-size: 16px !important; }}
}}

/* ===== 数智中枢：深色科技仪表盘（随 app.py 注入防缓存） ===== */
.gf-tech-card {{
    box-sizing: border-box !important; margin: 12px 0 !important; padding: 16px 18px !important;
    background: linear-gradient(160deg, #0C1418, #132127 70%, #0E1A1F) !important;
    border: 1px solid rgba(212,175,55,0.42) !important; border-radius: 6px !important;
    box-shadow: 0 8px 26px rgba(12,20,24,0.28), inset 0 0 0 1px rgba(87,207,195,0.06) !important;
    color: #DCE7DF !important;
}}
.gf-tech-h {{
    font-family: Georgia,"Times New Roman",serif !important; font-size: 16px !important;
    letter-spacing: 2px !important; color: #F3D98A !important;
    padding-bottom: 8px !important; margin-bottom: 6px !important;
    border-bottom: 1px solid rgba(212,175,55,0.28) !important;
}}
.gf-tech-sub {{
    font-size: 16px !important; color: #8FA8A2 !important;
    letter-spacing: 0.5px !important; margin-bottom: 12px !important; line-height: 1.6 !important;
}}
.gf-tech-metrics {{
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(118px, 1fr)) !important;
    gap: 10px !important; margin-top: 12px !important;
}}
.gf-tech-metrics > div {{
    background: rgba(87,207,195,0.06) !important;
    border: 1px solid rgba(212,175,55,0.20) !important;
    border-radius: 4px !important; padding: 10px 8px !important; text-align: center !important;
}}
.gf-tech-metrics b {{
    display: block !important; font-family: Georgia,serif !important;
    font-size: 16px !important; color: #F3D98A !important; letter-spacing: 1px !important;
}}
.gf-tech-metrics span {{
    display: block !important; font-size: 16px !important;
    color: #8FA8A2 !important; margin-top: 4px !important;
}}
.gf-tech-note {{
    margin: 10px 0 4px !important; padding: 10px 12px !important;
    background: rgba(87,207,195,0.06) !important; border-left: 3px solid #57CFC3 !important;
    font-size: 16px !important; line-height: 1.75 !important;
    color: #B9CDC7 !important; border-radius: 0 4px 4px 0 !important;
}}
.gf-tech-compare {{
    display: flex !important; align-items: center !important; justify-content: center !important;
    gap: 18px !important; flex-wrap: wrap !important; margin: 10px 0 !important;
}}
.gf-tech-compare > div {{ text-align: center !important; min-width: 130px !important; }}
.gf-tech-compare span {{
    display: block !important; font-size: 16px !important; color: #8FA8A2 !important;
    margin-bottom: 6px !important; letter-spacing: 1px !important;
}}
.gf-tech-compare i {{
    display: block !important; width: 100% !important; height: 56px !important;
    border-radius: 4px !important; border: 1px solid rgba(212,175,55,0.45) !important;
    box-shadow: inset 0 0 12px rgba(0,0,0,0.25) !important;
}}
.gf-tech-compare b {{
    display: block !important; margin-top: 6px !important;
    font-family: Georgia,serif !important; font-size: 16px !important;
    color: #F3D98A !important; letter-spacing: 1px !important;
}}
.gf-tech-compare > .gf-tech-arrow {{
    color: #D4AF37 !important; font-size: 16px !important;
    letter-spacing: 1px !important; min-width: 120px !important;
}}
.gf-tech-table {{ width: 100% !important; border-collapse: collapse !important; font-size: 16px !important; }}
.gf-tech-table th {{
    background: rgba(196,50,43,0.30) !important; color: #F3D98A !important;
    text-align: left !important; padding: 8px 10px !important;
    font-family: "Noto Sans CJK SC","Microsoft YaHei",Arial,sans-serif !important;
    font-weight: 700 !important; letter-spacing: 0.5px !important;
    border-bottom: 1px solid rgba(212,175,55,0.35) !important;
}}
.gf-tech-table td {{
    padding: 7px 10px !important; color: #C6D6D0 !important;
    border-bottom: 1px dotted rgba(212,175,55,0.18) !important;
}}
@media (max-width: 700px) {{
    .gf-tech-compare > div {{ min-width: 100px !important; }}
}}
</style>
"""
st.markdown(_CRITICAL_CSS, unsafe_allow_html=True)

# 商业化展示层样式：与 _CRITICAL_CSS 一样随 app.py 注入，
# 不依赖 theme.py 是否刷新，保证任何部署缓存状态下品牌视觉一致。
_BIZ_CSS = """
<style>
:root{
  --biz-sans: "Noto Sans CJK SC","Microsoft YaHei","PingFang SC","Hiragino Sans GB",Arial,sans-serif;
  --biz-red:#C4322B; --biz-red-deep:#8E1F1A; --biz-gold:#D4AF37;
  --biz-ink:#2B1D16; --biz-ink-deep:#231812; --biz-paper:#FDF8EC;
  --biz-mute:#6E5C42; --biz-line:rgba(168,128,31,.30);
}
.biz-nav{
  position:relative; width:100%; margin:0 0 18px;
  background:linear-gradient(100deg,#231812 0%,#3A2018 58%,#5A231C 100%);
  border:1px solid var(--biz-gold); border-radius:6px;
  box-shadow:0 6px 20px rgba(43,29,22,.22);
}
.biz-nav::before{
  content:""; position:absolute; inset:4px; border:1px solid rgba(212,175,55,.22);
  border-radius:3px; pointer-events:none;
}
.biz-nav-inner{
  display:flex; align-items:center; justify-content:space-between;
  gap:18px; flex-wrap:wrap; padding:12px 20px;
}
.biz-nav-brand{display:flex; align-items:center; gap:10px; white-space:nowrap;}
.biz-seal{
  display:inline-flex; align-items:center; justify-content:center;
  width:34px; height:34px; flex:0 0 34px;
  background:var(--biz-red); color:#FFF3D6;
  font-family:var(--gf-li),"STLiti","LiSu",serif !important;
  font-size:16px !important; font-weight:700;
  border:1px solid var(--biz-gold); border-radius:4px;
  box-shadow:inset 0 0 0 2px rgba(255,243,214,.25);
}
.biz-nav-name{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F7EEDC !important; letter-spacing:2px !important;
}
.biz-nav-name b{font-family:Georgia,serif !important; font-size:16px !important; color:var(--biz-gold) !important; letter-spacing:1px;}
.biz-nav-tag{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#E8C86A !important; border-left:1px solid rgba(212,175,55,.5);
  padding-left:12px; letter-spacing:1px;
}
.biz-nav-links{display:flex; align-items:center; gap:4px; flex-wrap:wrap;}
.biz-nav-link{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:600 !important; color:#EADFC6 !important;
  text-decoration:none !important; padding:7px 12px; border-radius:3px;
  letter-spacing:1px; transition:background .2s,color .2s;
}
.biz-nav-link:hover,.biz-nav-link.is-active{background:rgba(212,175,55,.18) !important; color:#FFF0C0 !important;}

/* ===== 首屏 ===== */
.biz-hero{
  background:linear-gradient(135deg,rgba(253,248,236,.94),rgba(247,238,220,.72));
  border:1px solid var(--biz-line); border-left:4px solid var(--biz-red);
  border-radius:6px; padding:28px 30px 24px; margin:0 0 14px;
  box-shadow:0 8px 26px rgba(43,29,22,.10);
}
.biz-eyebrow{
  display:flex; align-items:center; gap:9px;
  font-family:Georgia,var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; letter-spacing:2.4px !important;
  color:var(--biz-red-deep) !important; margin:0 0 12px;
}
.biz-eyebrow i{display:inline-block; width:22px; height:2px; background:var(--biz-gold);}
.biz-h1{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; line-height:1.25 !important;
  letter-spacing:4px !important; color:var(--biz-red-deep) !important;
  margin:0 0 6px !important; text-shadow:1px 1px 0 rgba(255,255,255,.7);
}
.biz-hero-en{
  font-family:Georgia,serif !important; font-size:16px !important;
  letter-spacing:1.6px !important;   color:#A8801F !important; margin:0 0 16px;
}
.biz-lead{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.95 !important; color:#4A3B2C !important; margin:0 0 14px;
}
.biz-lead strong{color:var(--biz-red-deep) !important; font-weight:700 !important;}
.biz-hero-points{list-style:none; margin:0 0 14px; padding:0;}
.biz-hero-points li{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.8 !important; color:#4A3B2C !important; margin:5px 0;
  display:flex; align-items:baseline; gap:10px;
}
.biz-hero-points li span{
  font-family:Georgia,serif !important; font-size:16px !important;
  color:#FFF !important; background:var(--biz-red); border-radius:2px;
  padding:1px 6px; flex:0 0 auto; font-weight:700;
}
.biz-hero-note{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:var(--biz-mute) !important; border-top:1px dashed var(--biz-line);
  padding-top:10px; letter-spacing:.5px;
}
.biz-metrics-wrap{
  background:var(--biz-ink-deep); border:1px solid var(--biz-gold);
  border-radius:6px; padding:18px 18px 14px; margin:0 0 14px;
  box-shadow:0 8px 26px rgba(43,29,22,.24); height:calc(100% - 14px);
}
.biz-metrics-head{
  display:flex; align-items:baseline; justify-content:space-between;
  border-bottom:1px solid rgba(212,175,55,.35); padding-bottom:9px; margin-bottom:14px;
}
.biz-metrics-head span{font-family:Georgia,serif !important; font-size:16px !important; letter-spacing:1.8px !important; color:#C9A94E !important;}
.biz-metrics-head b{font-family:var(--biz-sans) !important; font-size:16px !important; color:#F7EEDC !important; letter-spacing:1px !important;}
.biz-metrics{display:grid; grid-template-columns:1fr 1fr; gap:10px;}
.biz-metric{
  background:rgba(212,175,55,.07); border:1px solid rgba(212,175,55,.26);
  border-radius:4px; padding:12px 10px; text-align:center;
}
.biz-metric b{
  display:block; font-family:Georgia,serif !important; font-size:16px !important;
  color:#F3D98A !important; line-height:1.1 !important; letter-spacing:1px !important;
}
.biz-metric-label{
  display:block; font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F7EEDC !important; margin-top:5px;
}
.biz-metric-sub{
  display:block; font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#B6A585 !important; margin-top:4px; line-height:1.5;
}
.biz-metrics-foot{
  font-family:Georgia,serif !important; font-size:16px !important;
  color:#C9A94E !important; text-align:center; margin:13px 0 4px; letter-spacing:.6px;
}
.biz-metrics-disclaimer{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#8E8069 !important; text-align:center;
}
.biz-trust{
  display:flex; align-items:center; gap:12px; flex-wrap:wrap;
  background:rgba(253,248,236,.82); border:1px solid var(--biz-line);
  border-radius:4px; padding:11px 16px; margin:0 0 16px;
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#4A3B2C !important;
}
.biz-trust-label{
  font-weight:700 !important; color:var(--biz-red-deep) !important;
  border-right:1px solid var(--biz-line); padding-right:12px; letter-spacing:1px;
}
.biz-trust i{width:4px; height:4px; background:var(--biz-gold); border-radius:50%; flex:0 0 4px;}
.biz-trust-badge{
  margin-left:auto; background:rgba(196,50,43,.10); color:var(--biz-red-deep) !important;
  border:1px solid rgba(196,50,43,.30); border-radius:20px;
  padding:3px 12px; font-size:16px !important; font-weight:700 !important; white-space:nowrap;
}

/* ===== 通用区块标题 ===== */
.biz-section-head{margin:30px 0 16px; scroll-margin-top:18px;}
.biz-section-no{
  font-family:Georgia,serif !important; font-size:16px !important;
  letter-spacing:2.2px !important; color:#A8801F !important; font-weight:700;
}
.biz-h2{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; color:var(--biz-red-deep) !important;
  letter-spacing:2px !important; margin:5px 0 6px !important;
}
.biz-section-desc{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:var(--biz-mute) !important; line-height:1.8 !important; margin:0 !important;
}
.biz-section-line{height:2px; width:56px; background:linear-gradient(90deg,var(--biz-red),var(--biz-gold)); margin-top:11px; border-radius:2px;}

/* ===== 卡片网格 ===== */
.biz-grid-4{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px;}
.biz-grid-3{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:16px;}
.biz-card{
  background:var(--biz-paper); border:1px solid var(--biz-line);
  border-top:3px solid var(--biz-red); border-radius:5px;
  padding:18px 17px 16px; box-shadow:0 4px 14px rgba(43,29,22,.08);
  transition:transform .25s ease,box-shadow .25s ease;
}
.biz-card:hover{transform:translateY(-5px); box-shadow:0 12px 26px rgba(142,31,26,.18);}
.biz-card-top{display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;}
.biz-card-icon{
  display:inline-flex; align-items:center; justify-content:center;
  width:34px; height:34px; background:var(--biz-red); color:#FFF3D6;
  font-family:var(--gf-kai),"KaiTi",serif !important; font-size:16px !important;
  border-radius:4px; border:1px solid var(--biz-gold);
}
.biz-card-no{font-family:Georgia,serif !important; font-size:16px !important; color:#D9C398 !important;}
.biz-card h3{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:var(--biz-ink) !important; margin:0 0 8px !important;
}
.biz-card p{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.8 !important; color:#5C4C39 !important; margin:0 0 12px; min-height:66px;
}
.biz-tags{display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px;}
.biz-tag{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:var(--biz-red-deep) !important; background:rgba(196,50,43,.08);
  border:1px solid rgba(196,50,43,.22); border-radius:2px; padding:3px 7px;
}
.biz-card-output{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#7A6A50 !important; border-top:1px dashed var(--biz-line); padding-top:10px;
}

/* ===== 技术壁垒 ===== */
.biz-moat-wrap{
  display:grid; grid-template-columns:0.85fr 2fr; gap:18px;
  background:var(--biz-ink-deep); border:1px solid var(--biz-gold);
  border-radius:6px; padding:20px; box-shadow:0 8px 26px rgba(43,29,22,.2);
}
.biz-moat-intro{border-right:1px solid rgba(212,175,55,.3); padding-right:16px;}
.biz-moat-intro span{
  font-family:Georgia,serif !important; font-size:16px !important;
  letter-spacing:2px !important; color:#C9A94E !important;
}
.biz-moat-intro p{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.95 !important; color:#DCCFB2 !important; margin:12px 0 0;
}
.biz-moat-list{display:grid; grid-template-columns:1fr 1fr; gap:14px;}
.biz-moat{display:flex; gap:12px; background:rgba(212,175,55,.06); border:1px solid rgba(212,175,55,.20); border-radius:4px; padding:13px;}
.biz-moat-no{font-family:Georgia,serif !important; font-size:16px !important; color:#C9A94E !important; flex:0 0 auto;}
.biz-moat-body h4{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F3D98A !important; margin:0 0 6px !important;
}
.biz-moat-spec{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.7 !important; color:#B8C7C0 !important;
}
.biz-moat-value{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#EFE2C4 !important; margin-top:7px; border-left:2px solid var(--biz-gold); padding-left:8px;
}

/* ===== 服务方案 ===== */
.biz-plan{
  position:relative; background:var(--biz-paper); border:1px solid var(--biz-line);
  border-radius:6px; padding:22px 20px 18px; box-shadow:0 4px 16px rgba(43,29,22,.09);
  display:flex; flex-direction:column;
}
.biz-plan.is-featured{border:2px solid var(--biz-red); box-shadow:0 10px 30px rgba(142,31,26,.20);}
.biz-plan-badge{
  position:absolute; top:-12px; right:16px; background:var(--biz-red);
  color:#FFF3D6 !important; font-family:var(--biz-sans) !important;
  font-size:16px !important; font-weight:700 !important; letter-spacing:1px;
  padding:4px 12px; border-radius:20px; border:1px solid var(--biz-gold);
}
.biz-plan-en{font-family:Georgia,serif !important; font-size:16px !important; letter-spacing:2px !important; color:#A8801F !important;}
.biz-plan h3{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; color:var(--biz-red-deep) !important; margin:5px 0 3px !important;
}
.biz-plan-desc{font-family:var(--biz-sans) !important; font-size:16px !important; color:var(--biz-mute) !important; margin-bottom:12px;}
.biz-plan-price{
  font-family:Georgia,var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:var(--biz-ink) !important;
  border-bottom:1px solid var(--biz-line); padding-bottom:12px; margin-bottom:12px;
}
.biz-plan-price small{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:var(--biz-mute) !important; margin-left:8px; font-weight:400 !important;
}
.biz-plan-list{list-style:none; margin:0 0 16px; padding:0; flex:1;}
.biz-plan-list li{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#4A3B2C !important; margin:7px 0; display:flex; gap:8px; line-height:1.6;
}
.biz-plan-list li span{color:var(--biz-red) !important; font-weight:700 !important;}
.biz-plan-cta{
  text-align:center; font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:var(--biz-red-deep) !important;
  border:1px solid rgba(196,50,43,.4); border-radius:3px; padding:9px;
  background:rgba(196,50,43,.06); letter-spacing:1px;
}
.biz-plan.is-featured .biz-plan-cta{background:var(--biz-red); color:#FFF3D6 !important; border-color:var(--biz-red);}
.biz-plan-note{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#8A7B60 !important; margin-top:12px; line-height:1.7;
}

/* ===== 合作流程 ===== */
.biz-process{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; counter-reset:step;}
.biz-step{
  position:relative; background:rgba(253,248,236,.9); border:1px solid var(--biz-line);
  border-radius:5px; padding:16px 15px 14px;
}
.biz-step::after{
  content:"→"; position:absolute; right:-13px; top:38%; z-index:2;
  font-family:var(--biz-sans) !important; color:var(--biz-gold) !important;
  font-size:16px !important; font-weight:700;
}
.biz-step:last-child::after{display:none;}
.biz-step-no{
  width:28px; height:28px; display:flex; align-items:center; justify-content:center;
  background:var(--biz-red-deep); color:#FFF3D6; border-radius:50%;
  font-family:var(--gf-li),"LiSu",serif !important; font-size:16px !important; margin-bottom:10px;
}
.biz-step h4{font-family:var(--biz-sans) !important; font-size:16px !important; font-weight:700 !important; color:var(--biz-ink) !important; margin:0 0 6px !important;}
.biz-step p{font-family:var(--biz-sans) !important; font-size:16px !important; line-height:1.75 !important; color:#5C4C39 !important; margin:0;}

/* ===== FAQ ===== */
.biz-faq{display:grid; gap:9px;}
.biz-faq-item{
  background:var(--biz-paper); border:1px solid var(--biz-line);
  border-radius:4px; overflow:hidden;
}
.biz-faq-item summary{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:var(--biz-ink) !important;
  padding:13px 16px; cursor:pointer; list-style:none;
  display:flex; align-items:center; justify-content:space-between; gap:12px;
}
.biz-faq-item summary::-webkit-details-marker{display:none;}
.biz-faq-item[open] summary{color:var(--biz-red-deep) !important; border-bottom:1px solid var(--biz-line);}
.biz-faq-plus{font-size:16px !important; color:var(--biz-red) !important; flex:0 0 auto;}
.biz-faq-item[open] .biz-faq-plus{transform:rotate(45deg);}
.biz-faq-body{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.9 !important; color:#4A3B2C !important; padding:12px 16px 15px;
  background:rgba(247,238,220,.55);
}

/* ===== CTA 与企业页脚 ===== */
.biz-cta{
  margin:28px 0 18px; border-radius:6px; border:1px solid var(--biz-gold);
  background:linear-gradient(110deg,#231812,#5A231C 62%,#8E1F1A);
  box-shadow:0 8px 26px rgba(43,29,22,.22); overflow:hidden;
}
.biz-cta-inner{display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; padding:24px 28px;}
.biz-cta-en{font-family:Georgia,serif !important; font-size:16px !important; letter-spacing:2.4px !important; color:#E8C86A !important;}
.biz-cta h2{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; color:#FFF3D6 !important; letter-spacing:2px !important;
  margin:6px 0 6px !important;
}
.biz-cta p{font-family:var(--biz-sans) !important; font-size:16px !important; color:#E3D3B4 !important; margin:0 0 8px;}
.biz-cta-sub{font-family:var(--biz-sans) !important; font-size:16px !important; color:#C9A94E !important; letter-spacing:1px;}
.biz-footer{
  margin:16px 0 6px; border-radius:6px; border:1px solid rgba(212,175,55,.5);
  background:var(--biz-ink-deep); color:#DCCFB2;
}
.biz-footer-inner{display:grid; grid-template-columns:1.1fr 1.4fr 1.3fr; gap:22px; padding:22px 24px 18px;}
.biz-footer-brand{display:flex; align-items:center; gap:10px;}
.biz-footer-brand span:last-child{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F7EEDC !important; letter-spacing:1px;
}
.biz-footer-brand b{font-family:Georgia,serif !important; font-size:16px !important; color:var(--biz-gold) !important;}
.biz-footer-full{font-family:var(--biz-sans) !important; font-size:16px !important; color:#C9B990 !important; margin-top:10px;}
.biz-footer-slogan{font-family:var(--gf-kai),"KaiTi",serif !important; font-size:16px !important; color:#F3D98A !important; margin-top:6px; letter-spacing:2px;}
.biz-footer-col h5{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F3D98A !important;
  letter-spacing:1.5px !important; margin:0 0 10px !important;
  padding-bottom:7px; border-bottom:1px solid rgba(212,175,55,.28);
}
.biz-footer-line{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.9 !important; color:#BDAE90 !important;
}
.biz-footer-bottom{
  display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;
  border-top:1px solid rgba(212,175,55,.25); padding:12px 24px 14px;
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#9C8D72 !important; line-height:1.7;
}
.biz-footer-bottom span:first-child{color:#C9A94E !important; font-weight:700;}

/* ===== 内页品牌条 / 演示页 ===== */
.biz-rail-slogan{
  display:flex; align-items:center; justify-content:center; gap:12px;
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:var(--biz-mute) !important; padding-top:9px; white-space:nowrap;
}
.biz-rail-slogan b{color:var(--biz-red-deep) !important; font-size:16px !important; letter-spacing:1px;}
.biz-rail-slogan span{color:#7A6A50 !important;}
.biz-rail-slogan em{font-style:normal; color:#A8801F !important; border-left:1px solid var(--biz-line); padding-left:12px; font-size:16px !important;}
.biz-demo-head{margin:8px 0 18px;}
.biz-demo-aside{
  background:var(--biz-ink-deep); border:1px solid var(--biz-gold); border-radius:6px;
  padding:20px 22px; color:#DCCFB2;
}
.biz-demo-aside h4{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; color:#F3D98A !important; margin:0 0 12px !important;
}
.biz-demo-aside ul{margin:0; padding-left:18px;}
.biz-demo-aside li{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:2 !important; color:#D6C7A8 !important;
}
.biz-demo-aside-note{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#A89878 !important; border-top:1px solid rgba(212,175,55,.28);
  margin-top:14px; padding-top:12px; line-height:1.7;
}
.biz-success{
  background:rgba(253,248,236,.95); border:1px solid var(--biz-gold);
  border-left:4px solid var(--biz-red); border-radius:6px;
  padding:22px 24px; margin:16px 0;
}
.biz-success-mark{
  width:38px; height:38px; border-radius:50%; background:var(--biz-red);
  color:#FFF3D6; display:flex; align-items:center; justify-content:center;
  font-size:16px !important; font-weight:700; margin-bottom:10px;
}
.biz-success h3{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; color:var(--biz-red-deep) !important; margin:0 0 8px !important;
}
.biz-success p{font-family:var(--biz-sans) !important; font-size:16px !important; line-height:1.85 !important; color:#4A3B2C !important; margin:0 0 12px;}
.biz-success-warn{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.8 !important; color:#8E1F1A !important;
  background:rgba(196,50,43,.08); border:1px dashed rgba(196,50,43,.35);
  border-radius:3px; padding:10px 12px;
}

@media (max-width: 900px){
  .biz-h1{font-size:16px !important;}
  .biz-moat-wrap{grid-template-columns:1fr;}
  .biz-moat-intro{border-right:none; border-bottom:1px solid rgba(212,175,55,.3); padding:0 0 12px;}
  .biz-footer-inner{grid-template-columns:1fr 1fr;}
  .biz-step::after{display:none;}
}
@media (max-width: 700px){
  .biz-nav-inner{padding:10px 12px;}
  .biz-nav-tag{display:none;}
  .biz-nav-link{font-size:16px !important; padding:6px 8px;}
  .biz-h1{font-size:16px !important; letter-spacing:2px !important;}
  .biz-hero{padding:20px 18px;}
  .biz-moat-list{grid-template-columns:1fr;}
  .biz-footer-inner{grid-template-columns:1fr;}
  .biz-trust-badge{margin-left:0;}
  .biz-rail-slogan{display:none;}
}

/* ===== 在线支付 / 收银台 ===== */
.biz-pay-safety{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:8px; margin:0 0 14px;}
.biz-pay-safety-item{
  font-family:var(--biz-sans) !important; font-size:16px !important; color:#6B5A40 !important;
  background:rgba(253,248,236,.9); border:1px solid var(--biz-line);
  border-radius:3px; padding:7px 10px; text-align:center;
}
.biz-pay-card{
  background:linear-gradient(160deg,#2B1D16,#3D2A1D 60%,#2B1D16);
  border:1px solid var(--biz-gold); border-radius:6px; padding:20px 24px;
  margin:6px 0; box-shadow:0 10px 30px rgba(43,29,22,.25);
}
.biz-pay-card h4{
  font-family:var(--biz-sans) !important; color:#F3D98A !important;
  font-size:16px !important; font-weight:800 !important; letter-spacing:1.5px;
  margin:0 0 10px !important;
}
.biz-pay-amount{
  font-family:Georgia,serif !important; font-size:16px !important;
  font-weight:700 !important; color:#FFF3D6 !important; margin:6px 0 10px;
}
.biz-pay-amount small{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#C9A94E !important; font-weight:400 !important; margin-left:10px;
}
.biz-pay-row{
  display:flex; justify-content:space-between; gap:10px;
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#EFE2C4 !important; margin:0; padding:6px 0;
  border-bottom:1px dashed rgba(201,169,78,.25);
}
.biz-pay-row b{color:#F3D98A !important; font-weight:700 !important;}
.biz-pay-badge{
  display:inline-block; font-family:var(--biz-sans) !important; font-size:16px !important;
  padding:3px 12px; border-radius:20px; letter-spacing:1px; white-space:nowrap;
}
.biz-pay-badge.demo{background:rgba(201,169,78,.18); color:#F3D98A !important; border:1px solid var(--biz-gold);}
.biz-pay-badge.paid{background:rgba(110,180,110,.22); color:#C4ECBC !important; border:1px solid #6EB46E;}
.biz-pay-badge.pending{background:rgba(230,160,60,.18); color:#F5C98A !important; border:1px solid #E6A03C;}
.biz-pay-qrwrap{text-align:center; margin:16px 0 6px;}
.biz-pay-qrwrap img{
  width:186px; height:186px; border:6px solid #FFFFFF;
  border-radius:6px; box-shadow:0 6px 18px rgba(0,0,0,.35);
}
.biz-pay-qr-hint{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#C9A94E !important; margin-top:8px; letter-spacing:.5px;
}
.biz-pay-bank{
  background:rgba(253,248,236,.92); border:1px solid var(--biz-line);
  border-radius:5px; padding:14px 16px; margin:10px 0;
}
.biz-pay-bank div{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#4A3B2C !important; margin:5px 0; line-height:1.6;
}
.biz-pay-bank b{color:var(--biz-red-deep) !important;}
.biz-pay-note{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  color:#8A7B60 !important; line-height:1.7; margin-top:8px;
}
.biz-pay-qhead{
  font-family:var(--biz-sans) !important; font-size:16px !important; font-weight:800 !important;
  color:var(--biz-red-deep) !important; letter-spacing:1.5px;
  border-top:1px solid var(--biz-line); padding-top:14px; margin-top:16px;
}

/* ===== 首页板块入口方块：整块可点，点击进入独立页面 ===== */
.biz-boards-head{margin:34px 0 18px; scroll-margin-top:18px;}
.biz-boards-head.is-compact{margin:34px 0 14px;}
.biz-boards{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(212px,1fr));
  gap:16px; margin:0 0 20px;
}
.biz-board{
  position:relative; display:flex; flex-direction:column; align-items:flex-start;
  box-sizing:border-box; min-height:186px; padding:18px 18px 16px;
  background:linear-gradient(165deg,#FDF8EC 0%,#F7EEDC 100%);
  border:1px solid var(--biz-line); border-top:4px solid var(--biz-red);
  border-radius:6px; text-decoration:none !important; color:inherit !important;
  box-shadow:0 4px 14px rgba(43,29,22,.10); overflow:hidden;
  transition:transform .28s cubic-bezier(.34,1.56,.64,1),box-shadow .28s,border-color .28s;
}
.biz-board::before{
  content:""; position:absolute; inset:4px; border:1px solid rgba(212,175,55,.22);
  border-radius:3px; pointer-events:none;
}
.biz-board::after{
  content:""; position:absolute; right:-30px; bottom:-30px;
  width:96px; height:96px; border:1px solid rgba(196,50,43,.14);
  border-radius:50%; pointer-events:none; transition:transform .4s;
}
.biz-board:hover{
  transform:translateY(-6px); border-color:var(--biz-gold);
  border-top-color:var(--biz-red);
  box-shadow:0 14px 30px rgba(142,31,26,.22);
}
.biz-board:hover::after{transform:scale(1.5) rotate(20deg);}
.biz-board:active{transform:translateY(-2px) scale(.99);}
.biz-board-no{
  position:absolute; top:14px; right:16px;
  font-family:Georgia,serif !important; font-size:16px !important;
  color:#D9C398 !important; letter-spacing:1px;
}
.biz-board-icon{
  display:inline-flex; align-items:center; justify-content:center;
  width:38px; height:38px; flex:0 0 38px; margin-bottom:12px;
  background:var(--biz-red); color:#FFF3D6;
  font-family:var(--gf-kai),"KaiTi",serif !important; font-size:16px !important;
  border:1px solid var(--biz-gold); border-radius:4px;
  box-shadow:inset 0 0 0 2px rgba(255,243,214,.25);
}
.biz-board-title{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:800 !important; color:var(--biz-red-deep) !important;
  letter-spacing:2px !important; margin:0 0 8px !important;
}
.biz-board-desc{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  line-height:1.8 !important; color:#5C4C39 !important; flex:1; margin-bottom:12px;
}
.biz-board-go{
  font-family:var(--biz-sans) !important; font-size:16px !important;
  font-weight:700 !important; letter-spacing:1px;
  color:var(--biz-red-deep) !important;
  border-top:1px dashed var(--biz-line); padding-top:10px; width:100%;
}
.biz-board:hover .biz-board-go{color:var(--biz-red) !important;}
.biz-board.is-current{
  border-color:var(--biz-gold) !important; border-top-color:var(--biz-gold) !important;
  background:linear-gradient(165deg,#FBF3DD,#F2E4C0);
  opacity:.62;
}
.biz-board.is-current .biz-board-go::after{content:"　· 当前板块"; font-weight:400;}
@media (max-width:900px){
  .biz-boards{grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px;}
}
</style>
"""
st.markdown(_BIZ_CSS, unsafe_allow_html=True)

# 移动端排版优化：手机上压缩 Streamlit 默认大留白、强制分栏堆叠、
# 拉开五门/卡片间距、放大过小的字号。仅在窄屏生效，桌面端布局不变。
_MOBILE_CSS = """
<style>
@media (max-width: 640px){
  /* ---- Streamlit 容器：顶部仍为悬浮 header 让位，但压缩无效留白 ---- */
  [data-testid="stMainBlockContainer"]{ padding: 72px 12px 56px !important; }
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]){
    flex-direction: column !important; gap: 12px !important;
  }
  [data-testid="stColumn"]{ width: 100% !important; flex: 1 1 auto !important; }
  [data-testid="stButton"] button{ min-height: 46px; font-size: 16px !important; }

  /* ---- 门户大标题：缩小行楷标题与副标题 ---- */
  .gf-title{ font-size: 16px !important; letter-spacing: 5px !important; padding: 12px 0 8px !important; }
  .gf-subtitle{ font-size: 16px !important; margin: 8px 0 14px !important; }

  /* ---- 五门舞台：拉开间距，门牌高度自适应、卡内更透气 ---- */
  div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)){
    gap: 18px !important; margin: 0 auto 10px !important;
  }
  .gf-ring-center .gf-orbit-core{ width: 120px !important; height: 120px !important; font-size: 16px !important; }
  div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)){
    width: min(100%, 340px) !important;
  }
  .gf-nav-card{ height: auto !important; min-height: 176px; max-height: none !important; padding: 20px 18px 16px !important; }
  .gf-nav-num{ font-size: 16px !important; width: 44px !important; height: 44px !important; line-height: 44px !important; margin-bottom: 10px !important; }
  .gf-nav-title{ font-size: 16px !important; margin-bottom: 8px !important; }
  .gf-nav-desc{ font-size: 16px !important; line-height: 1.75 !important; }

  /* ---- 古建轮播：略缩卡片，标题更易读 ---- */
  .gf-carousel{ margin: 12px auto 16px !important; }
  .gf-slide{ width: 248px !important; height: 180px !important; }
  .gf-slide-title{ font-size: 16px !important; }
  .gf-carousel-hint{ font-size: 16px !important; }

  /* ---- 数智中枢 ---- */
  .gf-tech-card{ padding: 18px 16px !important; margin: 14px 0 !important; }
  .gf-tech-h{ font-size: 16px !important; }
  .gf-tech-sub{ font-size: 16px !important; line-height: 1.75 !important; }
  .gf-tech-note{ font-size: 16px !important; line-height: 1.8 !important; }
  .gf-tech-metrics > div{ padding: 12px 8px !important; }
  .gf-tech-metrics b{ font-size: 16px !important; }
  .gf-tech-metrics span{ font-size: 16px !important; }
  .gf-tech-table{ font-size: 16px !important; }

  /* ---- 品牌导航：链接加大触控区 ---- */
  .biz-nav{ margin-bottom: 16px !important; }
  .biz-nav-inner{ padding: 12px 14px !important; gap: 10px !important; }
  .biz-nav-name{ font-size: 16px !important; }
  .biz-nav-links{ gap: 6px !important; }
  .biz-nav-link{ font-size: 16px !important; padding: 8px 12px !important; }

  /* ---- Hero ---- */
  .biz-hero{ padding: 24px 18px 20px !important; margin-bottom: 16px !important; }
  .biz-h1{ padding: 0 !important; font-size: 16px !important; }
  .biz-lead{ font-size: 16px !important; line-height: 2 !important; }
  .biz-hero-points li{ font-size: 16px !important; line-height: 1.9 !important; margin: 7px 0 !important; }
  .biz-hero-en{ margin-bottom: 14px !important; }

  /* ---- 指标速览 ---- */
  .biz-metrics-wrap{ padding: 20px 16px 16px !important; }
  .biz-metrics{ gap: 12px !important; }
  .biz-metric{ padding: 14px 12px !important; }
  .biz-metric b{ font-size: 16px !important; }
  .biz-metric-label{ font-size: 16px !important; }
  .biz-metric-sub{ font-size: 16px !important; }

  /* ---- 信任条 / 区块标题 ---- */
  .biz-trust{ padding: 13px 14px !important; font-size: 16px !important; line-height: 1.85 !important; }
  .biz-section-head{ margin: 36px 0 18px !important; }
  .biz-h2{ padding: 4px 0 6px !important; font-size: 16px !important; }
  .biz-section-desc{ font-size: 16px !important; line-height: 1.9 !important; }

  /* ---- 解决方案卡片：单列下放开最小高度、放大正文 ---- */
  .biz-grid-3, .biz-grid-4{ gap: 16px !important; }
  .biz-card{ padding: 20px 18px 18px !important; }
  .biz-card h3{ font-size: 16px !important; }
  .biz-card p{ font-size: 16px !important; line-height: 1.85 !important; min-height: 0 !important; margin-bottom: 14px !important; }
  .biz-tag{ font-size: 16px !important; padding: 4px 9px !important; }
  .biz-card-output{ font-size: 16px !important; }

  /* ---- 技术壁垒 ---- */
  .biz-moat-wrap{ padding: 20px 16px !important; gap: 16px !important; }
  .biz-moat-intro p{ font-size: 16px !important; }
  .biz-moat-list{ gap: 12px !important; }
  .biz-moat{ padding: 16px 14px !important; }
  .biz-moat-body h4{ font-size: 16px !important; }
  .biz-moat-spec{ font-size: 16px !important; line-height: 1.8 !important; }
  .biz-moat-value{ font-size: 16px !important; }

  /* ---- 服务方案 ---- */
  .biz-plan{ padding: 24px 20px 20px !important; }
  .biz-plan h3{ font-size: 16px !important; }
  .biz-plan-desc{ font-size: 16px !important; }
  .biz-plan-price{ font-size: 16px !important; }
  .biz-plan-list li{ font-size: 16px !important; margin: 9px 0 !important; line-height: 1.7 !important; }
  .biz-plan-cta{ padding: 13px !important; font-size: 16px !important; }
  .biz-plan-note{ font-size: 16px !important; }

  /* ---- 合作流程 / FAQ / CTA ---- */
  .biz-process{ gap: 14px !important; }
  .biz-step{ padding: 18px 16px !important; }
  .biz-step h4{ font-size: 16px !important; }
  .biz-step p{ font-size: 16px !important; line-height: 1.8 !important; }
  .biz-faq{ gap: 11px !important; }
  .biz-faq-item summary{ font-size: 16px !important; padding: 15px 16px !important; }
  .biz-faq-body{ font-size: 16px !important; padding: 14px 16px !important; }
  .biz-cta-inner{ padding: 26px 20px !important; }
  .biz-cta h2{ padding: 4px 0 6px !important; font-size: 16px !important; }
  .biz-cta p{ font-size: 16px !important; }
  .biz-cta-sub{ font-size: 16px !important; }

  /* ---- 页脚 ---- */
  .biz-footer-inner{ padding: 24px 18px 20px !important; gap: 20px !important; }
  .biz-footer-full{ font-size: 16px !important; line-height: 1.8 !important; }
  .biz-footer-slogan{ font-size: 16px !important; }
  .biz-footer-col h5{ font-size: 16px !important; }
  .biz-footer-line{ font-size: 16px !important; line-height: 2 !important; }
  .biz-footer-bottom{ font-size: 16px !important; padding: 12px 16px 14px !important; }

  /* ---- 预约演示 / 提交成功 ---- */
  .biz-demo-aside{ padding: 22px 18px !important; }
  .biz-demo-aside li{ font-size: 16px !important; }
  .biz-success{ padding: 24px 18px !important; }
  .biz-success h3{ font-size: 16px !important; }
  .biz-success p{ font-size: 16px !important; }
  .biz-success-warn{ font-size: 16px !important; }

  /* ---- 收银台 ---- */
  .biz-pay-safety-item{ font-size: 16px !important; padding: 9px 10px !important; }
  .biz-pay-card{ padding: 22px 18px !important; }
  .biz-pay-amount{ font-size: 16px !important; }
  .biz-pay-row{ font-size: 16px !important; }
  .biz-pay-qrwrap img{ width: 200px !important; height: 200px !important; }
  .biz-pay-bank div{ font-size: 16px !important; }
  .biz-pay-note{ font-size: 16px !important; }
  .biz-pay-qhead{ font-size: 16px !important; }

  /* ---- 首页标语 / 免责声明（覆盖 inline style 的过密小字） ---- */
  div[style*="color:#7A6A50;font-size:16px"]{ font-size: 16px !important; letter-spacing: 1.5px !important; }
  div[style*="color:#8A7B60;font-size:16px"]{ font-size: 16px !important; }

  /* ---- 板块入口方块：单列、留白充足、触控区够大 ---- */
  .biz-boards-head{ margin: 30px 0 16px !important; }
  .biz-boards{ grid-template-columns: 1fr !important; gap: 14px !important; margin-bottom: 16px !important; }
  .biz-board{ min-height: 0 !important; padding: 18px 18px 16px !important; }
  .biz-board-icon{ width: 40px !important; height: 40px !important; flex-basis: 40px !important; margin-bottom: 12px !important; }
  .biz-board-title{ font-size: 16px !important; margin-bottom: 8px !important; }
  .biz-board-desc{ font-size: 16px !important; line-height: 1.85 !important; margin-bottom: 14px !important; }
  .biz-board-go{ font-size: 16px !important; padding-top: 12px !important; }
  .biz-board-no{ font-size: 16px !important; }
  .biz-boards-head.is-compact{ margin: 28px 0 14px !important; }
}
</style>
"""
st.markdown(_MOBILE_CSS, unsafe_allow_html=True)

# ================================================================ 全站字号统一（最后注入）
# 上面各样式层里的 font-size 已统一为 16px；这里再兜底覆盖 Streamlit 原生控件
# （标题 / 按钮 / 输入框 / 单选 / 数字指标 / 数据表格 / 代码块）与 SVG 图表内文字，
# 保证页面上任意可见文字的 computed font-size 完全一致，不受平台默认样式影响。
_UNIFORM_FONT_CSS = """
<style>
html body .stApp *:not(text):not(tspan),
html body .stApp *:not(text):not(tspan)::before,
html body .stApp *:not(text):not(tspan)::after,
html body [data-testid="stApp"] *:not(text):not(tspan),
html body [data-testid="stApp"] *:not(text):not(tspan)::before,
html body [data-testid="stApp"] *:not(text):not(tspan)::after{
  font-size: 16px !important;
}
/* SVG 图表内的坐标刻度 / 数据标注属于图形元素（viz.py 用 font-size 属性给出 9~15px），
   保留原尺寸：强行统一放大会让刻度与图例相互重叠、图表不可读。 */
/* 大标题缩到统一字号后，原来的大字距需同步收紧，避免散字 */
.gf-title{ letter-spacing: 3px !important; }
</style>
"""
st.markdown(_UNIFORM_FONT_CSS, unsafe_allow_html=True)

# ================================================================ PWA：可安装应用到手机/电脑桌面
# manifest / 图标 / Service Worker 放在 static/，由 serve.py 的 enableStaticServing 提供。
# 通过 st.html 的 JS 注入到页面 head（Streamlit 本身不提供自定义 head 的接口）。
_PWA_BOOT = """
<script>
(function () {
  function once(sel, make) { if (!document.querySelector(sel)) { document.head.appendChild(make()); } }
  var manifestHref = '/app/static/manifest.webmanifest';
  // 保留当前分享码：线上平台要求 URL 带 sharecode，否则安装后打开会 403
  try {
    var sc = new URLSearchParams(location.search).get('sharecode');
    if (sc) manifestHref += '?sharecode=' + encodeURIComponent(sc);
  } catch (e) {}

  once('link[rel="manifest"]', function () {
    var l = document.createElement('link'); l.rel = 'manifest'; l.href = manifestHref; return l;
  });
  once('meta[name="theme-color"]', function () {
    var m = document.createElement('meta'); m.name = 'theme-color'; m.content = '#C4322B'; return m;
  });
  once('meta[name="apple-mobile-web-app-capable"]', function () {
    var m = document.createElement('meta'); m.name = 'apple-mobile-web-app-capable'; m.content = 'yes'; return m;
  });
  once('meta[name="mobile-web-app-capable"]', function () {
    var m = document.createElement('meta'); m.name = 'mobile-web-app-capable'; m.content = 'yes'; return m;
  });
  once('meta[name="apple-mobile-web-app-status-bar-style"]', function () {
    var m = document.createElement('meta'); m.name = 'apple-mobile-web-app-status-bar-style'; m.content = 'black-translucent'; return m;
  });
  once('meta[name="apple-mobile-web-app-title"]', function () {
    var m = document.createElement('meta'); m.name = 'apple-mobile-web-app-title'; m.content = '考色'; return m;
  });
  once('link[rel="apple-touch-icon"]', function () {
    var l = document.createElement('link'); l.rel = 'apple-touch-icon'; l.href = '/app/static/icon-192.png'; return l;
  });

  if ('serviceWorker' in navigator) {
    // 先尝试根作用域，Streamlit 静态服务不带 Service-Worker-Allowed 头时会失败，回退静态目录作用域
    navigator.serviceWorker.register('/app/static/sw.js', { scope: '/' })
      .catch(function () { return navigator.serviceWorker.register('/app/static/sw.js', { scope: '/app/static/' }); })
      .catch(function () {});
  }
})();
</script>
"""
try:
    st.html(_PWA_BOOT, unsafe_allow_javascript=True)
except Exception:
    # 旧版 Streamlit 无 unsafe_allow_javascript 时降级为普通注入（不影响主站）
    try:
        st.html(_PWA_BOOT)
    except Exception:
        pass

# 商业化文案模块为可选增强：即使部署环境只刷新了 app.py、commerce.py 还是旧缓存，
# 主站功能照常运行，仅跳过商业化板块，绝不出现整站红页。
try:
    import commerce as biz
    _BIZ_OK = True
except Exception:
    biz = None
    _BIZ_OK = False

# 在线支付模块同理：payments.py 缺失时收银台入口自动降级，不影响主站。
try:
    import payments as pay_mod
    _PAY_OK = True
except Exception:
    pay_mod = None
    _PAY_OK = False

# 云服务接入同为可选增强：配置未就绪时自动降级为本地需求库，主站照常运行。
try:
    import cloud as cloud_mod
    _CLOUD_OK = True
except Exception:
    cloud_mod = None
    _CLOUD_OK = False

# 预约需求本地持久化：模块缺失时提交页仍可用，仅不落库并给出明确提示。
try:
    import demo_store as demo_db
    _DEMO_OK = True
except Exception:
    demo_db = None
    _DEMO_OK = False


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
            f'<div class="gf-cloud-band" style="filter:brightness(3)"></div>'
            f'<div class="gf-banner-cap" style="position:static;background:none;color:#F7EFE0;">'
            f'{title}{sub}</div></div>',
            unsafe_allow_html=True,
        )


def _carousel_thumb(path: str) -> str:
    """把古建图缩成约 700px 宽的 JPEG 再转 base64，避免整页内嵌数兆原图。"""
    import base64
    import io
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((700, 460), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=76, optimize=True)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()


def heritage_carousel():
    """古建照片轮播：横向自动滚动，每张可点击进入对应古建详情页。"""
    slides = ""
    for h in HERITAGES:
        path = os.path.join(ASSETS, h["image"])
        if not os.path.exists(path):
            continue
        data = _carousel_thumb(path)
        slides += (
            f'<a class="gf-slide" href="?view=hc_{_esc(h["key"])}{_QS}" target="_self" '
            f'title="点击进入 · {_esc(h["name"])}">'
            f'<img src="data:image/jpeg;base64,{data}" alt="{_esc(h["caption"])}">'
            f'<div class="gf-slide-cap">'
            f'<span class="gf-slide-title">{_esc(h["banner_title"])}</span>'
            f'<span class="gf-slide-sub">{_esc(h["banner_sub"])}</span>'
            f'<span class="gf-slide-more">点击进入「{_esc(h["name"])}」色彩修复案例 →</span>'
            f'</div></a>'
        )
    if not slides:
        return
    st.markdown(
        '<div class="gf-carousel-hint">'
        '古建巡览 · 五处遗产的色彩修复实录　|　照片横向缓缓呈现，'
        '鼠标悬停即停，点击任一画面查阅详情 →</div>',
        unsafe_allow_html=True,
    )
    # 复制一遍实现无缝循环
    st.markdown(
        f'<div class="gf-carousel"><div class="gf-carousel-track">{slides}{slides}</div></div>',
        unsafe_allow_html=True,
    )


def card_start(title: str, desc: str = "", icon: str = "") -> str:
    d = f'<div class="gf-card-desc">{desc}</div>' if desc else ""
    ic = ""
    if icon:
        uri = _icon_uri(icon)
        if uri:
            ic = f'<img class="gf-card-icon" src="{uri}" alt="">'
    return (f'<div class="gf-ornate-card gf-enter">'
            f'{ic}<div class="gf-card-title">{title}</div>{d}')


def swatch_html(hex_color: str, label: str = "") -> str:
    return (f'<span class="gf-swatch" style="background:{hex_color}"></span>'
            f'<span class="gf-swatch-label">{label or hex_color}</span>')


def _icon_uri(name: str) -> str:
    """把网络检索得到的古风小图标转成 data URI，云端无需外网。"""
    path = os.path.join(ASSETS, "emoji", name + ".png")
    if not os.path.exists(path):
        return ""
    import base64
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def nav_block(num: str, title: str, desc: str, btn_key: str,
              icon: str = "", slot_class: str = ""):
    """渲染一个导航方块（含真实 st.button），返回是否被点击。整块视觉即一个门牌。"""
    icon_html = ""
    if icon:
        uri = _icon_uri(icon)
        if uri:
            icon_html = f'<img class="gf-nav-icon" src="{uri}" alt="">'
    cls = "gf-nav-card" + ((" " + slot_class) if slot_class else "")
    marker = ""
    if slot_class:
        node_cls = slot_class.split()[-1]  # n1 ... n5
        marker = f'<div class="gf-ring-node-marker {node_cls}"></div>'
    with st.container():
        st.markdown(
            marker
            + f'<div class="{cls}">'
            f'<span class="gf-card-glow"></span>'
            f'{icon_html}'
            f'<div class="gf-nav-num">{num}</div>'
            f'<div class="gf-nav-title">{title}</div>'
            f'<div class="gf-nav-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return st.button(f"进入 · {title}　→", key=btn_key, use_container_width=True)


def orbit_center():
    """主页环形布局的中心徽记：旋转金环 + 朱印核心。"""
    st.markdown(
        '<div class="gf-orbit-wrap"><div class="gf-orbit-center">'
        '<div class="gf-orbit-ring"></div>'
        '<div class="gf-orbit-core">考色<small>五门拱卫</small></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def sec_title(text: str) -> str:
    """结果区统分区标题。"""
    return f'<div class="gf-sec-title">{text}</div>'


def badge(text: str, tone: str = "red") -> str:
    """结果区徽章：red / gold / teal。"""
    return f'<span class="gf-badge gf-badge-{tone}">{text}</span>'


def kv(key: str, val: str) -> str:
    """结果区键值行。"""
    return f'<div class="gf-kv"><span class="gf-kv-key">{key}</span><span class="gf-kv-val">{val}</span></div>'


def note(text: str) -> str:
    """结果区说明文字块。"""
    return f'<div class="gf-note">{text}</div>'


def html_table(data) -> str:
    """把 列表[dict] / DataFrame / dict / 列表 渲染成古风表格。"""
    import html
    if data is None:
        return ""
    if hasattr(data, "to_dict"):
        data = data.to_dict("records")
    if isinstance(data, dict):
        head = ["项目", "内容"]
        rows = [[html.escape(str(k)), html.escape(str(v))] for k, v in data.items()]
    elif isinstance(data, (list, tuple)) and len(data) > 0:
        if isinstance(data[0], dict):
            head = [html.escape(str(h)) for h in data[0].keys()]
            rows = [[html.escape(str(row.get(h, ""))) for h in data[0].keys()] for row in data]
        else:
            head = ["序号", "内容"]
            rows = [[str(i + 1), html.escape(str(x))] for i, x in enumerate(data)]
    else:
        return ""
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="gf-table"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def result_panel(sections) -> str:
    """把 [(小节标题, HTML正文), ...] 渲染成一张整洁的结果卷宗。"""
    wide_titles = ("对应建筑风格（据色推求）", "风格候选（按匹配度）")
    body = ""
    for title, content in sections:
        if content is None or content == "":
            continue
        cls = "gf-sec gf-sec-wide" if title in wide_titles else "gf-sec"
        body += (f'<div class="{cls}">{sec_title(title)}'
                 f'<div class="gf-sec-body">{content}</div></div>')
    return f'<div class="gf-result-panel">{body}</div>'


def tech_card(title: str, subtitle: str = "", body_html: str = ""):
    """数智中枢深色卡片：用于承载纯 HTML / SVG 内容。"""
    st.markdown(
        f'<div class="gf-tech-card">'
        f'<div class="gf-tech-h">{title}</div>'
        f'<div class="gf-tech-sub">{subtitle}</div>'
        f'{body_html}</div>',
        unsafe_allow_html=True,
    )


def deep_analysis(observed_hex: str, result_hex: str,
                  candidates, module_label: str = ""):
    """结果区深度分析：CIE 色度定位 + 贝叶斯后验 + 蒙特卡洛不确定度。

    candidates: [(名称, 候选色 hex), ...]
    """
    if not _TECH_OK:
        return
    from heritage_color import color_utils as cu
    pairs = [(n, hx) for n, hx in candidates if hx]
    if not pairs:
        return
    cand_hexes = [hx for _, hx in pairs]
    mc = unc.monte_carlo(observed_hex, cand_hexes, n_samples=1200)
    rows = unc.bayesian_posterior(
        [(n, hx, cu.color_distance(hx, result_hex)) for n, hx in pairs]
    )
    summary = unc.confidence_summary(mc, rows)
    extra = [(n[:6], hx, "#F3D98A" if i == 0 else "#57CFC3")
             for i, (n, hx) in enumerate(pairs[:4])]

    with st.expander("◈ 深度分析 · 光谱色度 / 贝叶斯 / 蒙特卡洛", expanded=False):
        st.markdown(
            f'<div class="gf-tech-card"><div class="gf-tech-h">'
            f'推理可信度 · {_esc(module_label or "本次推求")}</div>'
            f'<div class="gf-tech-metrics">'
            f'<div><b>{summary["top_probability"] * 100:.1f}%</b><span>最优后验概率</span></div>'
            f'<div><b>{summary["effective_candidates"]:.2f}</b><span>等效候选数 e^H</span></div>'
            f'<div><b>{summary["samples"]}</b><span>蒙特卡洛采样</span></div>'
            f'<div><b>{mc["ellipse"]["rx"]:.1f}×{mc["ellipse"]["ry"]:.1f}</b>'
            f'<span>95% 置信椭圆 / a*b*</span></div>'
            f'<div><b>{summary["confidence_level"]}</b><span>置信等级</span></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1.45, 1], gap="medium")
        with c1:
            st.markdown(viz.chromaticity_diagram(
                observed_hex, result_hex, mc["cloud_hexes"],
                mc["ellipse"], extra), unsafe_allow_html=True)
        with c2:
            st.markdown(viz.posterior_bars(rows), unsafe_allow_html=True)
            st.markdown(viz.convergence_chart(mc["convergence"]),
                        unsafe_allow_html=True)
        st.markdown(
            '<div class="gf-tech-card"><div class="gf-tech-note">'
            '推理链：实测色注入 Lab 测量噪声（σ = 2.0 / 3.2 / 3.2）→ '
            '蒙特卡洛传播 1200 次 → CIEDE2000 似然 exp(−ΔE/κ) × 朝代先验 × 文献证据 '
            '→ softmax 后验；色度图基于 CIE 1931 2° 标准观察者与光谱轨迹，'
            '点云为不确定度在初色空间的投影，虚线为 95% 置信区域。'
            '</div></div>',
            unsafe_allow_html=True,
        )


def goto(view_name: str):
    """切换视图并递增动画令牌，使入场特效在每次进入时重播。"""
    st.query_params["view"] = view_name
    st.session_state["view"] = view_name
    st.session_state["anim_token"] = st.session_state.get("anim_token", 0) + 1
    st.rerun()


def enter_animation():
    """渲染揭幕转场层。HTML 中含令牌，视图切换时节点重建，动画随之重播。"""
    token = st.session_state.get("anim_token", 0)
    st.markdown(
        f'<div class="gf-curtain" data-token="{token}">'
        f'<div class="gf-curtain-seal">考</div>'
        f'<div class="gf-curtain-line"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def back_button():
    """程序页顶部的返回条：品牌标语 + 商务演示入口（商业化版）。"""
    if _BIZ_OK:
        _c1, _c2, _c3 = st.columns([1, 2.2, 1.2])
        with _c1:
            if st.button("←　返回总览", key="back_home"):
                goto("home")
        with _c2:
            st.markdown(biz.rail_slogan(), unsafe_allow_html=True)
        with _c3:
            if st.button("预约商业演示 →", key="back_demo"):
                goto("demo")
    else:
        if st.button("←　返回总览", key="back_home"):
            goto("home")


def cloud_divider(text: str = ""):
    """页头云纹分隔带：默认只显示云纹图形，不显示文字。"""
    if text:
        st.markdown(f'<div class="gf-cloud-divider">{text}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="gf-cloud-band"></div>', unsafe_allow_html=True)


def meander():
    st.markdown('<div class="gf-meander"></div>', unsafe_allow_html=True)


def dynasty_options(default: str = "清"):
    """朝代下拉框的选项与默认值索引，默认指向指定朝代。"""
    opts = ["", *kb.DYNASTIES.keys()]
    idx = opts.index(default) if default in opts else 0
    return opts, idx


def ai_polish_block(text_key: str, label: str = "文献描述", dynasty_key: str = None):
    """在文本框下方渲染"AI 润色"程序：把口语描述改为考证书面语并补全色彩关键词。

    text_key: 对应文本输入框的 session_state key（润色结果写回此 key）。
    dynasty_key: 可选，朝代输入框的 key，用于按朝代补充用色线索。
    使用 on_click 回调在 widget 实例化前写入 session_state，避免新版
    Streamlit 的"widget 已实例化不可改"报错。
    """
    def _do_polish():
        src = st.session_state.get(text_key, "") or ""
        dy = st.session_state.get(dynasty_key, "") if dynasty_key else None
        result = polish_text(src, dynasty=dy or None)
        st.session_state[text_key] = result["polished"]
        st.session_state[f"{text_key}_polish_info"] = result

    btn_col, hint_col = st.columns([1, 2])
    with btn_col:
        st.button(
            "✦ AI 润色提示词", on_click=_do_polish,
            key=f"polish_{text_key}", help="将口语描述润色为文物考证书面语，并补全色彩关键词以提升考证准确度",
        )
    info = st.session_state.get(f"{text_key}_polish_info")
    if info:
        with st.expander("润色说明", expanded=False):
            st.markdown("**改动点**")
            for c in info["changes"]:
                st.write("- " + c)
            if info["keywords"]:
                st.markdown("**提取的色彩关键词**：" + "、".join(info["keywords"]))
            st.caption("润色采用内置文物考证书面语规则，无需联网；结果仅供描述优化参考。")


# ---------------------------------------------------------------- 页头（商业化品牌识别）
enter_animation()
st.markdown('<div class="gf-top-rule"></div>', unsafe_allow_html=True)
if _BIZ_OK:
    # 主页与各板块页显示完整导航（板块页高亮当前板块，便于互相跳转）；
    # 功能/收银台等内页显示精简品牌栏（避免品牌信息重复出现）。
    _hdr_view = st.query_params.get("view") or st.session_state.get("view", "home")
    if _hdr_view in _BOARD_PAGES:
        st.markdown(biz.nav(active=_hdr_view, qs=_QS), unsafe_allow_html=True)
    elif _hdr_view != "home":
        st.markdown(
            '<div class="biz-nav" id="biz-brand">'
            '<div class="biz-nav-inner">'
            '<div class="biz-nav-brand">'
            '<span class="biz-seal">考</span>'
            '<span class="biz-nav-name">考色 <b>KAOSE</b></span>'
            '<span class="biz-nav-tag" style="font-size:16px;">'
            '文物色彩智能考证平台 · Heritage Color Intelligence Platform</span>'
            '</div>'
            '<div style="font-family:var(--biz-sans);font-size:16px;color:#C9A94E;'
            'letter-spacing:1.5px;white-space:nowrap;">数字文保 · 智能决策平台 '
            '<b style="font-family:Georgia,serif;color:#F3D98A;">v2.0</b></div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="gf-title" style="font-size:16px;letter-spacing:6px;">'
        '考色 · 让千年色彩，有据可循</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="gf-title">文物色彩考证与修复辅助系统</div>',
        unsafe_allow_html=True,
    )
cloud_divider()
_hdr_l, _hdr_r = _icon_uri("lantern"), _icon_uri("dragon")
_hdr_icons = (
    f'<img class="gf-inline-icon" src="{_hdr_l}" alt="">'
    if _hdr_l else ""
) + (
    f'<img class="gf-inline-icon" src="{_hdr_r}" alt="">'
    if _hdr_r else ""
)
st.markdown(
    f'<div class="gf-subtitle">'
    f'{_hdr_icons}'
    '&nbsp;让千年色彩，有据可循　·　以色彩证源流 · 以颜料推古法 · 以风格辨建制 · 以材质续华章&nbsp;'
    f'{_hdr_icons}'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- 视图路由
# 支持三种导航：① 环形门牌用 ?view=xxx 链接；② 程序页按钮用 session_state；
# ③ 古建案例页用 ?view=hc_<key> 链接。
_VALID_VIEWS = ("home", "auth", "infer", "style", "restore", "material",
                "tech", "demo", "pay", "inquiries",
                "solutions", "moat", "pricing", "process", "faq")
_qp_view = st.query_params.get("view")
if _qp_view:
    if _qp_view in _VALID_VIEWS or _qp_view.startswith("hc_"):
        st.session_state["view"] = _qp_view
    else:
        st.session_state["view"] = "home"
if "view" not in st.session_state:
    st.session_state["view"] = "home"
view = st.session_state["view"]


# ================================================================ 门户首页
if view == "home":
    # ======================== 商业化官网首屏（可选增强，缺失模块时自动跳过） ======
    if _BIZ_OK:
        st.markdown(biz.nav(active="home", qs=_QS), unsafe_allow_html=True)
        _hl, _hr = st.columns([1.16, 0.84])
        with _hl:
            st.markdown(biz.hero(), unsafe_allow_html=True)
            _hc1, _hc2 = st.columns([1, 1])
            with _hc1:
                if st.button("▶　免费体验五大能力", key="hero_experience",
                             use_container_width=True):
                    goto("auth")
            with _hc2:
                if st.button("预约商业演示　→", key="hero_demo",
                             use_container_width=True):
                    goto("demo")
        with _hr:
            st.markdown(biz.metrics(), unsafe_allow_html=True)
        st.markdown(biz.trust_bar(), unsafe_allow_html=True)
        st.markdown(
            biz.section_head(
                "01", "PRODUCT CAPABILITIES", "核心能力 · 五大模块",
                "从色彩考证、颜料推演、风格辨识到修复决策与材质配材，"
                "覆盖文物色彩工作全链路；点击下方门牌即可进入对应程序。",
                "biz-capability",
            ),
            unsafe_allow_html=True,
        )
    # ======================== 原有首页内容（结构与文案保持不变） =================
    heritage_carousel()
    st.markdown(
        '<div style="text-align:center;color:#7A6A50;font-size:16px;'
        'letter-spacing:2px;margin:6px 0 6px;">择一门而入，探文物色彩之奥</div>',
        unsafe_allow_html=True,
    )
    # 数智中枢入口：独立一行按钮，不改动下方五门环绕布局。
    # 按钮无条件显示——即使 Cloud 包缓存未刷新（_TECH_OK=False），入口也必须可见，
    # 进入后显示降级介绍页并给出 Reboot 指引，避免"新模块凭空消失"。
    _tl, _tm, _tr = st.columns([1, 1.7, 1])
    with _tm:
        if st.button("◈ 数智中枢　·　光谱引擎 / 贝叶斯推断 / 蒙特卡洛　→",
                     key="go_tech_home", use_container_width=True):
            goto("tech")
        if not _TECH_OK:
            st.markdown(
                '<div style="text-align:center;color:#8A7B60;font-size:16px;'
                'margin-top:2px;">（云端计算内核尚未加载：右下角 Manage app → '
                'Reboot app 即可启用）</div>',
                unsafe_allow_html=True,
            )
    # 五门真正沿圆周均匀环绕：正上 → 右上 → 右下 → 左下 → 左上，
    # 每门间隔 72°，中心只保留「考色 / 五门拱卫」球体，外部圆圈全部去除。
    # 门牌仍是原来的卡片 + 真实 st.button，样式与文案一字未改。
    with st.container():
        st.markdown('<div class="gf-ring-stage-marker"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gf-ring-center">'
            '<div class="gf-orbit-core">考色<small>五门拱卫</small></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if nav_block("壹", "色彩考证",
                     "参酌现存残留色、文献与朝代，推求文物彩画之初色。",
                     "go_auth", icon="palette", slot_class="gf-ring-slot n1"):
            goto("auth")
        if nav_block("贰", "颜料推演",
                     "由一色反求所用颜料与调配之法，青绿朱黄，皆溯其源。",
                     "go_infer", icon="brush", slot_class="gf-ring-slot n2"):
            goto("infer")
        if nav_block("叁", "建筑风格识别",
                     "由色彩与用色制度，辨识和玺、旋子、苏式、敦煌等彩画风格。",
                     "go_style", icon="castle", slot_class="gf-ring-slot n3"):
            goto("style")
        if nav_block("肆", "修复决策",
                     "察颜料之性、病害之由、环境之宜，出最小干预之修复策。",
                     "go_restore", icon="scroll", slot_class="gf-ring-slot n4"):
            goto("restore")
        if nav_block("伍", "材质辨识与配材",
                     "上传照片辨识木石金属等材质，据病害给出修复所需材料。",
                     "go_material", icon="rock", slot_class="gf-ring-slot n5"):
            goto("material")

    meander()
    st.markdown(
        '<div style="text-align:center;color:#8A7B60;font-size:16px;'
        'font-family:\'Songti SC\',SimSun,serif;letter-spacing:1px;">'
        '本工具所出结果为辅助参考，实际操作须由专业人员依据检测报告裁定。'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)

    # ============ 平台板块入口（首页只放入口，具体内容在各独立页面） ============
    if _BIZ_OK:
        st.markdown(biz.boards(_QS), unsafe_allow_html=True)


# ================================================================ 板块独立页
# 首页只保留入口；解决方案 / 技术壁垒 / 服务方案 / 合作流程 / 常见问题
# 各自成为独立页面，点击首页方块或顶部导航自动跳转过来。
elif view in _BOARD_PAGES:
    back_button()
    _no, _en, _title, _desc, _render_name = _BOARD_PAGES[view]
    st.markdown(
        biz.section_head(_no, _en, _title, _desc, "biz-" + view),
        unsafe_allow_html=True,
    )
    if _BIZ_OK:
        _render = getattr(biz, _render_name, None)
        if _render is not None:
            # 服务方案的价格卡含站内跳转链接，需沿用 sharecode
            _html = _render(_QS) if view == "pricing" else _render()
            st.markdown(_html, unsafe_allow_html=True)
        if view == "moat":
            _ml, _mm, _mr = st.columns([1, 1.5, 1])
            with _mm:
                if st.button("◈　进入数智中枢 · 查看算法内核", key="board_moat_tech",
                             use_container_width=True):
                    goto("tech")
        if view == "pricing":
            st.markdown(biz.cta_band(), unsafe_allow_html=True)
            _ca, _cb1, _cb2, _cd = st.columns([0.8, 1.3, 1.3, 0.8])
            with _cb1:
                if st.button("▶　立即免费体验", key="board_cta_experience",
                             use_container_width=True):
                    goto("auth")
            with _cb2:
                if st.button("预约商业演示　→", key="board_cta_demo",
                             use_container_width=True):
                    goto("demo")
    else:
        st.info("该板块内容暂未加载，请返回总览后重新进入。")
    # 板块页底部：其它板块快捷入口，方便连续浏览（精简版，避免重复大标题）
    if _BIZ_OK:
        st.markdown(biz.boards(_QS, compact=True, active=view), unsafe_allow_html=True)
    meander()
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)


# ================================================================ 预约商业演示（商务入口）
elif view == "pay":
    back_button()
    if not (_BIZ_OK and _PAY_OK):
        st.error("支付模块暂未加载：请确认 payments.py 与 commerce.py 已随项目部署，刷新页面即可恢复。")
    else:
        st.markdown(biz.pay_head(), unsafe_allow_html=True)
        _pl, _pc, _pr = st.columns([1, 2.3, 1])
        with _pc:
            st.markdown(biz.pay_safety(), unsafe_allow_html=True)
            step = st.session_state.get("pay_step", 1)

            # ---------- ① 选品下单 ----------
            if step == 1:
                _prod_labels = [
                    f'{p["plan"]} · {p["name"]}　—　¥{p["price"]} / {p["unit"]}'
                    for p in pay_mod.PRODUCTS
                ]
                _qp_prod = st.query_params.get("product")
                _default_idx = next(
                    (i for i, p in enumerate(pay_mod.PRODUCTS) if p["id"] == _qp_prod), 0
                )
                sel_prod = st.radio(
                    "① 选择服务商品", _prod_labels, index=_default_idx, key="pay_prod_sel"
                )
                _meth_labels = [
                    f'{m["name"]}　·　{m["desc"]}' for m in pay_mod.PAYMENT_METHODS
                ]
                sel_meth = st.radio(
                    "② 选择支付方式（五种方式任选）",
                    _meth_labels, index=0, key="pay_meth_sel",
                )
                contact = st.text_input(
                    "③ 联系方式（写入电子收据）", key="pay_contact",
                    placeholder="邮箱或电话（演示环境不会发送）",
                )
                if st.button("确认下单　→", key="pay_create", type="primary",
                             use_container_width=True):
                    p = pay_mod.PRODUCTS[_prod_labels.index(sel_prod)]
                    m = pay_mod.PAYMENT_METHODS[_meth_labels.index(sel_meth)]
                    _order = pay_mod.create_order(p["id"], m["id"], contact)
                    st.session_state["pay_order"] = _order["order_no"]
                    st.session_state["pay_step"] = 2
                    st.rerun()
                st.markdown(
                    '<div class="biz-pay-note">※ 当前为<b>演示收银台</b>：订单保存于本站订单库，'
                    '扫码与支付结果均为流程模拟，不产生真实扣款；正式商户通道接入后自动切换真实收款。'
                    f'订单存储：{pay_mod.storage_kind()}。</div>',
                    unsafe_allow_html=True,
                )

            # ---------- ② 收银台 ----------
            elif step == 2:
                no = st.session_state.get("pay_order", "")
                _o = pay_mod.get_order(no)
                if not _o:
                    st.warning("订单不存在或已被清理，请重新下单。")
                    if st.button("← 重新下单", key="pay_reorder", use_container_width=True):
                        st.session_state["pay_step"] = 1
                        st.rerun()
                else:
                    _m = pay_mod.method(_o["method"]) or pay_mod.PAYMENT_METHODS[0]
                    _status = _o["status"]
                    _badge_cls = {"created": "demo", "pending": "pending", "paid": "paid"}.get(
                        _status, "demo")
                    _badge_txt = {"created": "待支付", "pending": "等待对账确认",
                                  "paid": "已支付"}.get(_status, _status)
                    _rows = (
                        f'<div class="biz-pay-row"><span>订单编号</span><b>{_o["order_no"]}</b></div>'
                        f'<div class="biz-pay-row"><span>商品</span><b>{_esc(_o["product_name"])}</b></div>'
                        f'<div class="biz-pay-row"><span>支付方式</span><b>{_m["name"]}</b></div>'
                        f'<div class="biz-pay-row"><span>下单时间</span><b>{_o["created_at"]}</b></div>'
                        f'<div class="biz-pay-row"><span>订单状态</span>'
                        f'<span class="biz-pay-badge {_badge_cls}">{_badge_txt}</span></div>'
                    )
                    st.markdown(
                        '<div class="biz-pay-card">'
                        '<h4>KAOSE 收银台</h4>'
                        f'<div class="biz-pay-amount">¥ {_o["amount"]}'
                        f'<small>演示环境 · 不产生真实扣款</small></div>'
                        f'{_rows}</div>',
                        unsafe_allow_html=True,
                    )
                    _kind, _qtext, _extra = pay_mod.checkout_payload(_o, _o["method"])
                    if _kind == "qrcode":
                        _uri = pay_mod.qrcode_data_uri(_qtext)
                        if _uri:
                            st.markdown(
                                f'<div class="biz-pay-qrwrap"><img src="{_uri}" alt="支付二维码">'
                                f'<div class="biz-pay-qr-hint">请使用{_m["name"]}扫码完成支付'
                                '（演示二维码，不指向真实收款）</div></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.info("二维码组件未安装（pip install qrcode），可改用对公转账方式下单。")
                        if pay_mod.gateway_status(_o["method"]) == "demo":
                            if st.button("✓　模拟支付成功（演示通道）", key="pay_demo",
                                         type="primary", use_container_width=True):
                                pay_mod.mark_paid(no, f"DEMO-{no[-6:] if no else 'PAID'}")
                                st.session_state["pay_step"] = 3
                                st.rerun()
                        else:
                            st.info("真实商户通道已配置：请扫码完成支付，支付结果经回调自动确认。")
                    else:  # 对公转账
                        _bank_rows = "".join(
                            f'<div><b>{_esc(k)}：</b>{_esc(v)}</div>'
                            for k, v in pay_mod.BANK_ACCOUNT.items()
                        )
                        st.markdown(
                            f'<div class="biz-pay-bank">{_bank_rows}'
                            '<div style="margin-top:6px;font-size:16px;color:#8A7B60;">'
                            '转账时请注明订单编号，转账完成后在下方登记回单凭证号，'
                            '我们将在 1 个工作日内对账确认。</div></div>',
                            unsafe_allow_html=True,
                        )
                        _receipt_no = st.text_input(
                            "转账凭证号 / 回单编号", key="pay_bank_receipt",
                            placeholder="如：TXT-20261119-001",
                        )
                        if st.button("提交转账凭证（提交后等待对账确认）",
                                     key="pay_bank_submit", use_container_width=True):
                            if _receipt_no.strip():
                                pay_mod.submit_bank_receipt(no, _receipt_no.strip())
                                st.session_state["pay_step"] = 3
                                st.rerun()
                            else:
                                st.warning("请填写银行回单上的凭证号。")
                    if st.button("← 取消订单并返回", key="pay_cancel", use_container_width=True):
                        pay_mod.update_order(no, status="cancelled")
                        st.session_state["pay_step"] = 1
                        st.rerun()

            # ---------- ③ 支付结果 ----------
            else:
                no = st.session_state.get("pay_order", "")
                _o = pay_mod.get_order(no) or {}
                _paid = _o.get("status") == "paid"
                st.markdown(
                    '<div class="biz-success">'
                    f'<div class="biz-success-mark">{"✓" if _paid else "⏳"}</div>'
                    f'<h3>{"支付成功（演示通道）" if _paid else "凭证已登记，等待对账确认"}</h3>'
                    f'<p>订单 <b>{no}</b> · {_esc(_o.get("product_name", ""))}'
                    f'　·　¥{_o.get("amount", 0)}　·　'
                    f'{pay_mod.method(_o.get("method", "")).get("name", "") if _o else ""}</p>'
                    '<div class="biz-success-warn">演示环境不产生真实扣款；正式商户通道接入后，'
                    '本页将展示真实支付结果与电子发票开具入口。</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                if _o:
                    st.download_button(
                        "↓　下载电子收据（.txt）",
                        data=pay_mod.receipt_text(_o).encode("utf-8-sig"),
                        file_name=f"考色_电子收据_{no}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                _c1, _c2 = st.columns(2)
                with _c1:
                    if st.button("再下一单", key="pay_again", use_container_width=True):
                        st.session_state["pay_step"] = 1
                        st.rerun()
                with _c2:
                    if st.button("返回主页", key="pay_home", use_container_width=True):
                        goto("home")

            # ---------- 订单查询 ----------
            st.markdown('<div class="biz-pay-qhead">ORDER LOOKUP · 订单查询</div>',
                        unsafe_allow_html=True)
            _qno = st.text_input("输入订单编号查询支付状态", key="pay_query_no",
                                 placeholder="KA2026…………")
            if st.button("查询订单", key="pay_query", use_container_width=True):
                _qo = pay_mod.get_order(_qno.strip())
                if _qo:
                    _bm = pay_mod.method(_qo["method"]) or {}
                    _badge_cls = {"paid": "paid", "pending": "pending"}.get(
                        _qo["status"], "demo")
                    _badge_txt = pay_mod.ORDER_STATUS.get(_qo["status"], _qo["status"])
                    st.markdown(
                        '<div class="biz-pay-card">'
                        f'<div class="biz-pay-row"><span>订单编号</span><b>{_esc(_qo["order_no"])}</b></div>'
                        f'<div class="biz-pay-row"><span>商品</span><b>{_esc(_qo["product_name"])}</b></div>'
                        f'<div class="biz-pay-row"><span>金额</span><b>¥ {_qo["amount"]}</b></div>'
                        f'<div class="biz-pay-row"><span>支付方式</span><b>{_bm.get("name", "")}</b></div>'
                        f'<div class="biz-pay-row"><span>下单时间</span><b>{_qo["created_at"]}</b></div>'
                        f'<div class="biz-pay-row"><span>状态</span>'
                        f'<span class="biz-pay-badge {_badge_cls}">{_badge_txt}</span></div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                elif _qno.strip():
                    st.warning("未找到该订单编号，请核对后重试（订单编号以 KA 开头）。")

            _recent = pay_mod.list_orders(5)
            if _recent:
                st.markdown('<div class="biz-pay-note">最近订单：</div>', unsafe_allow_html=True)
                _tbl = [{
                    "订单号": _r["order_no"],
                    "商品": _r["product_name"],
                    "金额": f'¥ {_r["amount"]}',
                    "方式": (pay_mod.method(_r["method"]) or {}).get("name", _r["method"]),
                    "状态": pay_mod.ORDER_STATUS.get(_r["status"], _r["status"]),
                } for _r in _recent]
                st.dataframe(_tbl, use_container_width=True, hide_index=True)


elif view == "demo":
    back_button()
    if _BIZ_OK:
        _dl, _dr = st.columns([1.35, 0.85])
        with _dl:
            st.markdown(biz.demo_head(), unsafe_allow_html=True)
        with _dr:
            st.markdown(biz.demo_aside(), unsafe_allow_html=True)

        with st.form("demo_form", clear_on_submit=False):
            _f1, _f2 = st.columns([1, 1])
            with _f1:
                org = st.text_input("机构 / 单位名称 *", placeholder="如：某博物院文物保护部")
                contact = st.text_input("联系人 *", placeholder="姓名")
            with _f2:
                org_type = st.selectbox("机构类型", [
                    "文博单位 / 博物馆", "文物保护工程机构", "数字展陈 / 文创机构",
                    "高校 / 科研院所", "其他",
                ])
                channel = st.text_input("联系方式 *", placeholder="邮箱或电话（演示站不发送）")
            interest = st.multiselect("关注方向", [
                "色彩考证与数字档案", "修复方案论证", "虚拟复原与展陈配色",
                "光谱与不确定度分析", "私有化部署 / API 对接", "教学与科研",
            ], default=["色彩考证与数字档案"])
            demand = st.text_area("需求描述", height=110,
                                  placeholder="简述文保对象、现有资料与期望产出…")
            submitted = st.form_submit_button("提交演示预约", use_container_width=True)

        if submitted:
            if not (org.strip() and contact.strip() and channel.strip()):
                st.warning("请至少填写机构名称、联系人与联系方式。")
            else:
                rec = {
                    "机构": org, "联系人": contact, "机构类型": org_type,
                    "联系方式": channel, "关注方向": "、".join(interest) or "未填写",
                    "需求描述": demand or "未填写",
                }
                st.session_state["demo_record"] = rec
                # 只在「本次提交」写一次库；后续 rerun（下载、刷新）不重复落库。
                try:
                    row = demo_db.save_request(rec) if _DEMO_OK else None
                except Exception:
                    row = None
                st.session_state["demo_ref"] = (row or {}).get("id", "")
                st.session_state["demo_submitted"] = True

        if st.session_state.get("demo_submitted"):
            rec = st.session_state.get("demo_record", {})
            _ref = st.session_state.get("demo_ref", "")
            _cloud_saved = bool(_CLOUD_OK and cloud_mod.cloud_ready())
            if _cloud_saved:
                cloud_mod.demo_sync_component(rec, ref=_ref)
            st.markdown(biz.demo_success(rec.get("机构", ""), rec.get("联系人", ""),
                                         saved=bool(_ref), cloud_saved=_cloud_saved,
                                         ref=_ref),
                        unsafe_allow_html=True)
            lines = ["考色 KAOSE · 商业演示需求确认单", "=" * 34]
            lines += [f"{k}：{v}" for k, v in rec.items()]
            if _cloud_saved:
                lines += ["", "※ 本文件由在线演示站生成；本次需求已保存至本站需求库"
                          "并同步至云端，此确认单供你自行留存核对。"]
            elif _ref:
                lines += ["", f"※ 需求编号：{_ref}；本次填写内容已保存至本站需求库，"
                          "此确认单供你自行留存核对。"]
            else:
                lines += ["", "※ 本文件由在线演示站生成，仅保存在当前会话，"
                          "未上传服务器，也未用于任何商务跟进。"]
            st.download_button(
                "↓　下载需求确认单（.txt）",
                data="\n".join(lines).encode("utf-8-sig"),
                file_name="考色_演示预约确认单.txt",
                mime="text/plain",
                use_container_width=True,
            )
            if st.button("重新填写", key="demo_reset"):
                st.session_state["demo_submitted"] = False
                st.rerun()
        if st.button("需求记录（管理员）", key="demo_inquiries"):
            goto("inquiries")
    else:
        st.info("商务演示模块暂未加载，请重新部署或重启应用后刷新页面。")


# ================================================================ 需求记录（管理员）
elif view == "inquiries":
    back_button()
    st.markdown(
        '<div class="biz-demo-head"><div class="biz-eyebrow"><i></i> INQUIRIES / 需求记录</div>'
        '<h2 class="biz-h2">已收到的预约需求</h2>'
        '<p>此页仅供站点管理员查看。数据真实保存在应用服务器本地需求库；'
        '重新发布应用会清空历史记录，请及时导出 CSV 留存。</p></div>',
        unsafe_allow_html=True,
    )
    _expect_tok = os.environ.get("DEMO_ADMIN_TOKEN") or "kaose-admin"
    _tok = st.text_input("管理员口令", type="password", key="inq_token",
                         placeholder="请输入管理员口令")
    if not _tok:
        st.info("请输入管理员口令查看预约记录。")
    elif _tok != _expect_tok:
        st.error("口令不正确。")
    elif not _DEMO_OK:
        st.error("需求库模块未加载，请重新部署后重试。")
    else:
        _rows = demo_db.list_requests(50)
        st.caption(f"存储方式：{demo_db.storage_kind()} ｜ 最近 {len(_rows)} 条")
        st.download_button(
            "↓　导出全部预约（CSV）",
            data=demo_db.csv_bytes(),
            file_name="考色_预约需求记录.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if _rows:
            st.dataframe([{
                "需求编号": r["id"], "提交时间": r["created_at"],
                "机构": r["org"], "联系人": r["contact_person"],
                "联系方式": r["contact_method"], "机构类型": r["org_type"],
                "关注方向": r["directions"], "需求描述": r["message"],
            } for r in _rows], use_container_width=True, hide_index=True)
        else:
            st.info("暂无预约记录。提交一次「预约商业演示」后即可在此查看。")


# ================================================================ 数智中枢（技术内核）
elif view == "tech":
    back_button()
    if not _TECH_OK:
        # 降级介绍页：不依赖 spectral/uncertainty/viz 包文件，纯 HTML 渲染，
        # 让用户在任何缓存状态下都能看到新模块的说明与启用指引。
        st.warning(
            "⚠ 数智中枢计算内核（spectral / uncertainty / viz）尚未在云端生效。"
            "请点击页面右下角 **Manage app** → **...** → **Reboot app**，"
            "约 1 分钟后刷新即可体验完整功能。"
        )
        tech_card(
            "数智中枢 · SPECTRAL INTELLIGENCE",
            "CIE 1931 标准观察者 / Kubelka-Munk 物理混色 / 贝叶斯证据合成 / 蒙特卡洛不确定度传播",
            '<div class="gf-tech-metrics">'
            '<div><b>18</b><span>朝代风格库</span></div>'
            '<div><b>15</b><span>矿物/有机颜料</span></div>'
            '<div><b>36</b><span>光谱通道 380–730nm</span></div>'
            '<div><b>1200</b><span>蒙特卡洛采样</span></div>'
            '<div><b>ΔE₀₀</b><span>CIEDE2000 色差</span></div>'
            '<div><b>10 nm</b><span>光谱采样间隔</span></div>'
            '</div>',
        )
        tech_card(
            "推理链路 · 从光子到决策",
            "6 阶段可解释流水线（Reboot 后提供交互式版本）",
            '<div class="gf-tech-compare">'
            '<div><b>① 实测</b><span>sRGB / 文献</span></div>'
            '<div class="gf-tech-arrow">→</div>'
            '<div><b>② 光谱</b><span>36 通道重建</span></div>'
            '<div class="gf-tech-arrow">→</div>'
            '<div><b>③ 物理</b><span>K-M 混色</span></div>'
            '<div class="gf-tech-arrow">→</div>'
            '<div><b>④ 似然</b><span>CIEDE2000</span></div>'
            '<div class="gf-tech-arrow">→</div>'
            '<div><b>⑤ 后验</b><span>贝叶斯 + MC</span></div>'
            '<div class="gf-tech-arrow">→</div>'
            '<div><b>⑥ 决策</b><span>最小干预</span></div>'
            '</div>',
        )
        tech_card(
            "核心能力",
            "色彩考证与颜料推演两大模块的深度分析面板同步获得增强",
            '<div class="gf-tech-note">'
            "① <b>光谱级取色</b>：不再停留于 RGB 三通道，把每个颜色重建为 380–730nm "
            "36 通道反射率光谱，用 CIE 1931 标准观察者做色度学定位；<br>"
            "② <b>物理混色</b>：Kubelka-Munk 单常数 K/S 模型按颜料光学密度混合，"
            "预测调配后的真实光谱而非简单平均；<br>"
            "③ <b>不确定性量化</b>：1200 次蒙特卡洛传播测量噪声，给出 95% 置信椭圆；"
            "贝叶斯后验融合朝代先验与文献权重，输出每种候选颜料的概率；<br>"
            "④ <b>时光倒流</b>：可逆老化动力学（光褪色 + 硫化变黑双通道）从现存色反演"
            "任意年代的原始色；<br>"
            "⑤ <b>同色异谱检测</b>：换光源（D65 / A / 烛光 / LED）计算色度漂移与"
            "异谱指数，评估修复配色在不同展陈光环境下的稳定性。"
            '</div>',
        )
    else:
        from heritage_color import color_utils as _cu

        tech_card(
            "数智中枢 · SPECTRAL INTELLIGENCE",
            "CIE 1931 标准观察者 / Kubelka-Munk 物理混色 / 贝叶斯证据合成 / 蒙特卡洛不确定度传播",
            f'<div class="gf-tech-metrics">'
            f'<div><b>{len(kb.DYNASTIES)}</b><span>朝代风格库</span></div>'
            f'<div><b>{len(kb.PIGMENTS)}</b><span>矿物/有机颜料</span></div>'
            f'<div><b>{sp._N}</b><span>光谱通道 380–730nm</span></div>'
            f'<div><b>1200</b><span>蒙特卡洛采样</span></div>'
            f'<div><b>ΔE₀₀</b><span>CIEDE2000 色差</span></div>'
            f'<div><b>10 nm</b><span>光谱采样间隔</span></div>'
            f'</div>',
        )
        st.markdown(viz.flow_diagram([
            ("① 实测", "sRGB / 文献"), ("② 光谱", "36 通道重建"),
            ("③ 物理", "K-M 混色"), ("④ 似然", "CIEDE2000"),
            ("⑤ 后验", "贝叶斯 + MC"), ("⑥ 决策", "最小干预"),
        ]), unsafe_allow_html=True)

        ca, cb, cc = st.columns(3)
        with ca:
            pigment = st.selectbox("考察颜料", list(kb.PIGMENTS.keys()),
                                   key="tech_pigment")
        with cb:
            years = st.slider("时光倒流 · 反演年代（年）", 20, 500, 200, 20,
                              key="tech_years")
        with cc:
            test_light = st.selectbox("同色异谱 · 对照光源",
                                      ("A", "烛光", "展厅LED"),
                                      key="tech_light")

        p = kb.PIGMENTS[pigment]
        fresh_hex = p.hex_fresh
        ag = sp.aging_curve(fresh_hex, pigment, 400, 12)
        aged_hex = ag[-1]["hex"]
        rev = sp.reverse_aging(aged_hex, pigment, years)
        shift = sp.illuminant_shift(fresh_hex, "D65", test_light)
        # 同色异谱对照：取同色系的两种颜料做配比优化，使 D65 下可调至等色
        _same = [q for q in kb.PIGMENTS.values()
                 if q.family == p.family and q.name != pigment]
        _alt_names = ([q.name for q in _same[:2]] if len(_same) >= 2
                      else ["石青", "藤黄"])
        mm = sp.metamerism_index([(pigment, 1.0)],
                                 [(_alt_names[0], 0.5), (_alt_names[1], 0.5)],
                                 test_light)

        near = [(q.name, q.hex_fresh) for q in sorted(
            kb.PIGMENTS.values(),
            key=lambda q: _cu.color_distance(fresh_hex, q.hex_fresh))[:4]]
        mc = unc.monte_carlo(aged_hex, [hx for _, hx in near], n_samples=1200)

        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            st.markdown(viz.chromaticity_diagram(
                aged_hex, rev["restored_hex"], mc["cloud_hexes"][:130],
                mc["ellipse"], [(pigment, fresh_hex, "#F3D98A")]),
                unsafe_allow_html=True)
        with c2:
            st.markdown(viz.spectrum_chart([
                (pigment + " 新鲜态", sp.reflectance_from_hex(fresh_hex), "#E0574A"),
                ("现存老化态", sp.reflectance_from_hex(aged_hex), "#57CFC3"),
                ("D65 光源 SPD", sp.illuminant("D65"), "#D4AF37"),
            ], y_max=1.35), unsafe_allow_html=True)

        # —— 时光倒流：老化动力学 + 解析反演 ——
        st.markdown(viz.aging_timeline(
            sp.aging_curve(fresh_hex, pigment, years, 10)), unsafe_allow_html=True)
        tech_card(
            "时光倒流 · 解析反演",
            "光致褪色（漂白）+ 含铅/汞颜料硫化变黑双通道，闭式逆变换直接解出初色",
            f'<div class="gf-tech-compare">'
            f'<div><span>推求初色 · t = 0</span>'
            f'<i style="background:{rev["restored_hex"]}"></i>'
            f'<b>{rev["restored_hex"]}</b></div>'
            f'<div class="gf-tech-arrow">⟶ 历经 {years} 年 ⟶</div>'
            f'<div><span>现存残留色 · t = {years}</span>'
            f'<i style="background:{aged_hex}"></i><b>{aged_hex}</b></div>'
            f'</div>'
            f'<div class="gf-tech-note">老化时间常数 τ = {rev["tau_years"]} 年'
            f'（由耐光等级 {p.lightfastness}/5 推得）；正向老化累计色差 '
            f'ΔE₀₀ = {ag[-1]["delta_e"]}；把反演初色重新正向老化，'
            f'与观测色残差仅 {rev["residual_delta_e"]} ΔE₀₀，验证逆变换自洽。</div>',
        )

        # —— 同色异谱：展厅照明风险 ——
        mm_txt = ""
        if mm.get("valid"):
            mm_txt = (f'配方级同色异谱指数 MI = {mm["metamerism_index"]} ΔE₀₀'
                      f'（D65 下两配方等色至 {mm["delta_e_d65"]}，换 {_esc(test_light)} '
                      f'光源后为 {mm["delta_e_test"]}；优化配比 {mm["optimized_formula"]}）'
                      f'—— MI 越低，补色方案在照明变化下越稳定')
        tech_card(
            "同色异谱 · 展厅照明评估",
            "同一反射光谱在不同光源 SPD 下的呈色漂移；补色在暖光下「跳色」的量化风险",
            f'<div class="gf-tech-compare">'
            f'<div><span>D65 标准日光</span>'
            f'<i style="background:{shift["a"]["hex"]}"></i>'
            f'<b>{shift["a"]["hex"]}</b></div>'
            f'<div class="gf-tech-arrow">⟶ 换光源 ⟶</div>'
            f'<div><span>{_esc(test_light)}</span>'
            f'<i style="background:{shift["b"]["hex"]}"></i>'
            f'<b>{shift["b"]["hex"]}</b></div>'
            f'</div>'
            f'<div class="gf-tech-note">色度漂移 x: '
            f'{shift["a"]["xy"][0]:.3f}→{shift["b"]["xy"][0]:.3f}，'
            f'y: {shift["a"]["xy"][1]:.3f}→{shift["b"]["xy"][1]:.3f}；'
            f'呈色差 ΔE₀₀ = {shift["delta_e"]}。{mm_txt}</div>',
        )

        # —— 贝叶斯后验 + 蒙特卡洛收敛 ——
        rows = unc.bayesian_posterior(
            [(n, hx, _cu.color_distance(hx, fresh_hex)) for n, hx in near]
        )
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.markdown(viz.posterior_bars(rows), unsafe_allow_html=True)
        with d2:
            st.markdown(viz.convergence_chart(mc["convergence"]),
                        unsafe_allow_html=True)

        # —— 算法栈 ——
        stack = [
            ("色空间", "sRGB ↔ CIE XYZ ↔ CIE-L*ab（D65）", "三刺激值与感知均匀空间互转"),
            ("色差", "CIEDE2000（CIE 142-2001）", "含明度/彩度/色相加权与旋转项"),
            ("标准观察者", "CIE 1931 2° CMF（Wyman 2013 解析拟合）", "36 通道光谱积分与 xy 色度"),
            ("光源", "Planck 黑体辐射 · D65/A/烛光/LED", "同色异谱与照明漂移评估"),
            ("混色物理", "Kubelka-Munk 单常数 K/S 模型", "颜料浓度加权的非线性混色"),
            ("老化", "光褪色 + 硫化变黑双通道（可逆）", "解析逆变换「时光倒流」"),
            ("证据", "贝叶斯似然 × 朝代先验 × 文献权重", "softmax 后验概率"),
            ("不确定度", "蒙特卡洛传播 + 协方差特征分解", "95% 置信椭圆 / 收敛诊断"),
        ]
        tbl = ('<table class="gf-tech-table"><tr><th>层</th><th>算法 / 标准</th>'
               '<th>在本系统中的作用</th></tr>'
               + "".join(f'<tr><td>{_esc(a)}</td><td>{_esc(b)}</td>'
                         f'<td>{_esc(c)}</td></tr>' for a, b, c in stack)
               + '</table>')
        tech_card("算法栈 · 标准与实现",
                  "纯 Python 标准库实现，无外部模型权重；推理过程全程可解释、可复现",
                  tbl)

        st.markdown(
            '<div class="gf-tech-card"><div class="gf-tech-note">说明：反射率由颜料典型色反演重建'
            '（同色异谱近似，闭环残差 &lt; 2.1 ΔE₀₀），属教学/演示级参考光谱，'
            '不替代实测分光光度数据；实际修复须以检测报告为准。</div></div>',
            unsafe_allow_html=True,
        )
    meander()
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)


# ================================================================ 古建案例详情
elif view.startswith("hc_"):
    _hc_data = get_heritage(view[len("hc_"):])
    if _hc_data is None:
        st.info("未找到该古建案例，请返回总览。")
        back_button()
    else:
        back_button()
        banner(_hc_data["image"], _hc_data["banner_title"], _hc_data["caption"])
        st.markdown(card_start(
            _hc_data["name"] + " · 色彩修复案例",
            _hc_data["intro"],
            icon="lantern",
        ), unsafe_allow_html=True)
        def _case_list(items):
            return "".join(f'<div class="gf-step-line">{_esc(str(x))}</div>'
                           for x in items)

        def _case_points(items):
            return "".join(f'<div class="gf-kv">'
                           f'<span class="gf-kv-val">{_esc(str(x))}</span></div>'
                           for x in items)

        st.markdown('<div class="gf-result-label">AI 与数字化修复经历</div>',
                    unsafe_allow_html=True)
        st.markdown(result_panel([("数字化与 AI 应用", _case_list(_hc_data["ai_history"]))]),
                    unsafe_allow_html=True)

        st.markdown('<div class="gf-result-label">当前的修复困难</div>',
                    unsafe_allow_html=True)
        st.markdown(result_panel([("修复困难", _case_list(_hc_data["difficulties"]))]),
                    unsafe_allow_html=True)

        st.markdown('<div class="gf-result-label">本系统能解决什么</div>',
                    unsafe_allow_html=True)
        st.markdown(result_panel([("「考色」五门对应之策", _case_points(_hc_data["solutions"]))]),
                    unsafe_allow_html=True)

        cta1, cta2, cta3 = st.columns([1, 2, 1])
        with cta2:
            if st.button("进入「色彩考证」体验本技术", type="primary",
                         key="hc_go_auth", width="stretch"):
                goto("auth")
    st.markdown("</div>", unsafe_allow_html=True)
    meander()
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)


# ================================================================ 壹 色彩考证
elif view == "auth":
    back_button()
    banner("summer_palace.jpg", "壹 · 色彩考证",
           "循残留之色，参文献之载，以推本来面目")
    st.markdown(card_start(
        "壹 · 色彩考证",
        "参酌现存残留色、文献记载与朝代风格，推求文物彩画之初色。",
        icon="palette",
    ), unsafe_allow_html=True)
    _in_left, col1, _in_right = st.columns([1, 2, 1])
    with col1:
        st.markdown("**一、现存残留色**")
        if "observed" not in st.session_state:
            st.session_state["observed"] = "#6E2020"
        observed = st.color_picker("现存残留色（实测）", key="observed")
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

                        def _pick_auth_color(hex_value=None):
                            """回调：在 color_picker 实例化前写回现存色。"""
                            st.session_state["observed"] = hex_value
                            st.session_state["observed_picked"] = hex_value

                        for i, s in enumerate(swatches):
                            a, b = st.columns([1, 3])
                            with a:
                                st.markdown(swatch_html(s.hex, ""), unsafe_allow_html=True)
                            with b:
                                st.write(f"{s.hex} · 占比 {s.ratio:.0%}")
                                st.button(
                                    "用作现存色", key=f"pick_{i}",
                                    on_click=_pick_auth_color, args=(s.hex,),
                                )
                        if "observed_picked" in st.session_state:
                            st.success(
                                f"已采用图像取色 {st.session_state['observed_picked']} "
                                "作为现存残留色。")
                    except Exception as e:
                        st.error(f"图像解析失败：{e}")
        dy_opts, dy_idx = dynasty_options("清")
        dynasty1 = st.selectbox("朝代", dy_opts, index=dy_idx, key="dyn1")
        if "doc" not in st.session_state:
            st.session_state["doc"] = "檐下青绿彩画，朱柱，间以金线"
        doc = st.text_area(
            "文献描述文本", key="doc",
            help="含朱/青/绿/金/红/白/黑等色彩关键词即可作为证据",
        )
        ai_polish_block("doc", dynasty_key="dyn1")
        top_k = st.slider("候选颜料数量", 1, 5, 3, key="topk1")
        run1 = st.button("开始考证", type="primary", key="run1")
    with st.container():
        st.markdown('<div class="gf-result-label">推断结果</div>', unsafe_allow_html=True)
        if run1:
            try:
                r = auth_color(
                    observed_hex=observed, dynasty=dynasty1 or None,
                    document_text=doc or None, top_k=top_k,
                )
                sections = []
                sections.append((
                    "原始色（推求）",
                    f'<div class="gf-swatch-row">{swatch_html(r.original_hex, "")}'
                    f'<span class="gf-num">{r.original_hex}</span>'
                    f'{badge(f"置信度 {r.confidence:.0%}", "gold")}</div>',
                ))
                sections.append(("匹配颜料", html_table(r.matched_pigments)))
                sections.append(("推理依据", note(_esc(str(r.reasoning)))))
                pigment_names = [m["颜料"] for m in r.matched_pigments]
                styles = identify_architecture_style(
                    color_hex=r.original_hex, dynasty=dynasty1 or None,
                    pigment_names=pigment_names, top_n=3,
                )
                if styles:
                    items = ""
                    for m in styles:
                        items += (
                            '<div class="gf-style-item">'
                            + badge(f"{_esc(str(m.style))}　{m.score:.0%}", "teal")
                            + kv("类别", _esc(str(m.category)))
                            + kv("常见于", _esc(str(m.typical_use)))
                            + note(_esc(str(m.reasoning)))
                            + '</div>'
                        )
                    sections.append(("对应建筑风格（据色推求）",
                                     f'<div class="gf-style-list">{items}</div>'))
                st.markdown(result_panel(sections), unsafe_allow_html=True)
                # 深度分析：把「一个答案」展开成色度定位 + 概率分布
                from heritage_color import color_utils as _cu
                _pairs = [(m["颜料"], kb.PIGMENTS[m["颜料"]].hex_fresh)
                          for m in r.matched_pigments
                          if m.get("颜料") in kb.PIGMENTS]
                if not _pairs:
                    _pairs = [(p.name, p.hex_fresh) for p in sorted(
                        kb.PIGMENTS.values(),
                        key=lambda p: _cu.color_distance(r.original_hex, p.hex_fresh))[:4]]
                deep_analysis(observed, r.original_hex, _pairs, "色彩考证")
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写上方参数后点击「开始考证」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 贰 颜料推演
elif view == "infer":
    back_button()
    banner("dunhuang.jpg", "贰 · 颜料推演",
           "青绿朱黄，皆有所自；一色反求，可溯其源")
    st.markdown(card_start(
        "贰 · 颜料推演",
        "由一色反求其所用颜料与调配之法，青绿朱黄，皆可溯其源。",
        icon="brush",
    ), unsafe_allow_html=True)
    _in_left, col1, _in_right = st.columns([1, 2, 1])
    with col1:
        target = st.color_picker("目标颜色", "#2E9070", key="target")
        dy_opts2, dy_idx2 = dynasty_options("清")
        dynasty2 = st.selectbox("朝代约束", dy_opts2, index=dy_idx2, key="dyn2")
        allow_mix = st.checkbox("允许混合颜料配方", value=True)
        top_n = st.slider("候选配方数", 1, 5, 3, key="topn2")
        run2 = st.button("开始推演", type="primary", key="run2")
    with st.container():
        st.markdown('<div class="gf-result-label">推演结果</div>', unsafe_allow_html=True)
        if run2:
            try:
                r = infer_pigment(target, dynasty=dynasty2 or None,
                                  allow_mixture=allow_mix, top_n=top_n)
                best = r["best_formula"]
                delta_badge = badge("色差 " + str(best["delta_e"]), "gold")
                sections = []
                sections.append((
                    "最优配方",
                    f'<div class="gf-swatch-row">{swatch_html(best["result_hex"], "")}'
                    f'<span class="gf-num">{best["result_hex"]}</span>'
                    f'{delta_badge}</div>'
                    + kv("颜料", _esc(str(best["pigments"]))),
                ))
                sections.append(("单颜料候选", html_table(r["single_pigments"])))
                if r["mixtures"]:
                    sections.append(("混合配方候选", html_table(r["mixtures"])))
                sections.append(("推演依据", note(_esc(str(r["reasoning"])))))
                if r.get("note"):
                    sections.append(("附注", note(_esc(str(r["note"])))))
                st.markdown(result_panel(sections), unsafe_allow_html=True)
                from heritage_color import color_utils as _cu
                _pairs = [(p.name, p.hex_fresh) for p in sorted(
                    kb.PIGMENTS.values(),
                    key=lambda p: _cu.color_distance(best["result_hex"], p.hex_fresh))[:4]]
                deep_analysis(target, best["result_hex"], _pairs, "颜料推演")
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写上方参数后点击「开始推演」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 叁 建筑风格识别
elif view == "style":
    back_button()
    banner("foguang_temple.jpg", "叁 · 建筑风格识别",
           "观其用色制度，辨其建制源流")
    st.markdown(card_start(
        "叁 · 建筑风格识别",
        "由色彩与用色制度，辨识其所属古建筑彩画风格：和玺、旋子、苏式、敦煌壁画等。",
        icon="castle",
    ), unsafe_allow_html=True)
    _in_left, col1, _in_right = st.columns([1, 2, 1])
    with col1:
        if "style_color" not in st.session_state:
            st.session_state["style_color"] = "#1B6FA8"
        style_hex = st.color_picker("已知彩画主色", key="style_color")
        with st.expander("或上传图片自动取色"):
            uploaded3 = st.file_uploader(
                "上传彩画照片取主色", type=["jpg", "jpeg", "png"], key="upload_style")
            if uploaded3 is not None:
                st.image(uploaded3, caption="已上传图像", width="stretch")
                try:
                    sw = extract_image_colors(uploaded3, top_n=6)

                    def _pick_style_color(hex_value=None):
                        """回调：在 color_picker 实例化前写回主色。"""
                        st.session_state["style_color"] = hex_value
                        st.session_state["style_picked"] = hex_value

                    for i, s in enumerate(sw):
                        a, b = st.columns([1, 3])
                        with a:
                            st.markdown(swatch_html(s.hex, ""), unsafe_allow_html=True)
                        with b:
                            st.write(f"{s.hex} · {s.ratio:.0%}")
                            st.button(
                                "取此色", key=f"style_pick_{i}",
                                on_click=_pick_style_color, args=(s.hex,),
                            )
                    if "style_picked" in st.session_state:
                        st.success(f"已采用图像取色 {st.session_state['style_picked']}")
                except Exception as e:
                    st.error(f"图像解析失败：{e}")
        dynasty3 = st.selectbox("朝代（可选）", ["", *kb.DYNASTIES.keys()], key="dyn3")
        pigment_text = st.text_input(
            "已知颜料（可选，逗号分隔）", "石青,石绿",
            help="如 石青,石绿,朱砂；留空则仅凭色彩与朝代判断")
        run3 = st.button("识别风格", type="primary", key="run3s")
    with st.container():
        st.markdown('<div class="gf-result-label">识别结果</div>', unsafe_allow_html=True)
        if run3:
            try:
                names = [p.strip() for p in pigment_text.split(",") if p.strip()]
                matches = identify_architecture_style(
                    color_hex=style_hex, dynasty=dynasty3 or None,
                    pigment_names=names, top_n=3,
                )
                items = ""
                for i, m in enumerate(matches, 1):
                    items += (
                        '<div class="gf-style-item">'
                        + badge(f"{i}. {_esc(str(m.style))}", "red")
                        + badge(f"匹配 {m.score:.0%}", "gold")
                        + kv("类别 / 等级", _esc(str(m.category)) + "　" + _esc(str(m.rank)))
                        + kv("特征", _esc(str(m.feature)))
                        + kv("常见于", _esc(str(m.typical_use)))
                        + note(_esc(str(m.reasoning)))
                        + '</div>'
                    )
                st.markdown(
                    result_panel([("风格候选（按匹配度）",
                                   f'<div class="gf-style-list">{items}</div>')]),
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"识别失败：{e}")
        else:
            st.info("填写上方参数后点击「识别风格」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 肆 修复决策
elif view == "restore":
    back_button()
    banner("potala.jpg", "肆 · 修复决策",
           "察其材、审其病、度其境，而后出修复之策")
    st.markdown(card_start(
        "肆 · 修复决策",
        "察颜料之性、病害之由、环境之宜，出修复之策，守最小干预之则。",
        icon="scroll",
    ), unsafe_allow_html=True)
    _in_left, col1, _in_right = st.columns([1, 2, 1])
    with col1:
        pigment = st.selectbox("颜料", ["", *kb.PIGMENTS.keys()], key="pig")
        damage = st.selectbox("病害", list(kb.DAMAGE_RULES.keys()), key="dmg")
        hum = st.text_input("当前湿度", "75% RH")
        lux = st.text_input("当前照度", "")
        run4 = st.button("生成方案", type="primary", key="run4")
    with st.container():
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
                sections = []
                sections.append(("方案概要",
                                 badge(f"紧迫度 {r.urgency}", "red")
                                 + note(_esc(str(r.summary)))))
                steps = "".join(
                    f'<div class="gf-step-line"><span class="gf-step-no">{i}</span>'
                    f'{_esc(str(s))}</div>' for i, s in enumerate(r.steps, 1))
                sections.append(("建议工艺步骤", steps))
                sections.append(("建议材料", note(_esc("、".join(r.materials)))))
                env_tbl = html_table(r.environment)
                if env_tbl:
                    sections.append(("环境控制", env_tbl))
                if r.risks:
                    sections.append((
                        "风险提示",
                        f'<div class="gf-risk">{_esc("；".join(r.risks))}</div>',
                    ))
                st.markdown(result_panel(sections), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"计算失败：{e}")
        else:
            st.info("填写上方参数后点击「生成方案」")
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================ 伍 材质辨识与配材
elif view == "material":
    back_button()
    banner("foguang_temple.jpg", "伍 · 材质辨识与配材",
           "辨木石金彩之质，定修复配材之方")
    st.markdown(card_start(
        "伍 · 材质辨识与配材",
        "上传文物照片辨识其材质，再据病害给出修复所需材料与工艺要点。",
        icon="rock",
    ), unsafe_allow_html=True)
    _in_left, col1, _in_right = st.columns([1, 2, 1])

    with col1:
        st.markdown("**一、上传照片识别材质**")
        up_mat = st.file_uploader(
            "上传木构 / 石刻 / 金属 / 彩画 / 地仗等照片（JPG / PNG）",
            type=["jpg", "jpeg", "png"], key="upload_material",
        )
        detected: List[str] = []
        if up_mat is not None:
            st.image(up_mat, caption="已上传图像", width="stretch")
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

        # 识别结果自动填入下拉框（带 key 的组件会忽略 index，须写入 session_state）
        if detected and st.session_state.get("mat_sel", "") in ("", None):
            st.session_state["mat_sel"] = detected[0]
            st.session_state["mat_dis"] = [
                d for d in kb.MATERIALS[detected[0]].common_diseases[:2]
                if d in kb.DAMAGE_RULES
            ]
            st.rerun()

        meander()
        st.markdown("**二、选择材质与病害**")
        mat_options = ["", *kb.MATERIALS.keys()]
        mat_name = st.selectbox("材质", mat_options, key="mat_sel")
        diseases = st.multiselect(
            "病害（可多选）", list(kb.DAMAGE_RULES.keys()), key="mat_dis",
        )
        hum2 = st.text_input("当前湿度", "75% RH", key="mat_hum")
        lux2 = st.text_input("当前照度", "", key="mat_lux")
        run5 = st.button("生成修复配材方案", type="primary", key="run5")

    with st.container():
        st.markdown('<div class="gf-result-label">识别与配材结果</div>',
                    unsafe_allow_html=True)
        if run5:
            if not mat_name:
                st.warning("请先上传照片识别材质，或在上方下拉框选择材质。")
            else:
                try:
                    env = {}
                    if hum2:
                        env["湿度"] = hum2
                    if lux2:
                        env["照度"] = lux2
                    plan = recommend_repair_materials(mat_name, diseases=diseases,
                                                      environment=env or None)
                    sections = []
                    sections.append((
                        "辨识材质",
                        badge(_esc(str(plan.material)), "red")
                        + badge(f"紧迫度 {plan.urgency}", "gold"),
                    ))
                    sections.append(("修复所需材料", note(_esc("、".join(plan.materials)))))
                    sections.append(("工艺要点", note(_esc(str(plan.craft)))))
                    sections.append((
                        "修复禁忌",
                        f'<div class="gf-risk">{_esc(str(plan.taboo))}</div>',
                    ))
                    env_tbl = html_table(plan.environment)
                    if env_tbl:
                        sections.append(("环境建议", env_tbl))
                    if plan.reasoning:
                        sections.append(("推断说明", note(_esc(str(plan.reasoning)))))
                    st.markdown(result_panel(sections), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"计算失败：{e}")
        elif detected:
            st.markdown(
                result_panel([(
                    "图像辨识结论",
                    badge(_esc(str(detected[0])), "teal")
                    + note("照片最可能为上述材质；材质与病害已自动填入左侧，"
                           "可直接生成配材方案。如需调整，可在上方重新选择后生成。"),
                )]),
                unsafe_allow_html=True,
            )
        else:
            st.info("上传照片或在上方选定材质与病害后点击「生成修复配材方案」")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- 全局企业页脚
# 放在路由链之后：首页、各功能模块、技术页与案例详情页统一带上品牌与合规信息。
if _BIZ_OK:
    st.markdown(biz.footer(), unsafe_allow_html=True)
