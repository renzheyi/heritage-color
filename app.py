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
    margin: -100px auto 6px !important;
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
    width: 132px !important; height: 132px !important; font-size: 26px !important;
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
</style>
"""
st.markdown(_CRITICAL_CSS, unsafe_allow_html=True)


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
    body = ""
    for title, content in sections:
        if content is None or content == "":
            continue
        body += (f'<div class="gf-sec">{sec_title(title)}'
                 f'<div class="gf-sec-body">{content}</div></div>')
    return f'<div class="gf-result-panel">{body}</div>'


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
    """程序页顶部的返回按钮。"""
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


# ---------------------------------------------------------------- 页头
enter_animation()
st.markdown('<div class="gf-top-rule"></div>', unsafe_allow_html=True)
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
    '&nbsp;以色彩证源流 · 以颜料推古法 · 以风格辨建制 · 以材质续华章&nbsp;'
    f'{_hdr_icons}'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- 视图路由
# 支持两种导航：① 环形门牌用 ?view=xxx 链接；② 程序页按钮用 session_state。
_VALID_VIEWS = ("home", "auth", "infer", "style", "restore", "material")
_qp_view = st.query_params.get("view")
if _qp_view:
    st.session_state["view"] = _qp_view if _qp_view in _VALID_VIEWS else "home"
if "view" not in st.session_state:
    st.session_state["view"] = "home"
view = st.session_state["view"]


# ================================================================ 门户首页
if view == "home":
    banner("forbidden_city.jpg", "丹宸彩画 · 源远流长",
           "故宫太和殿 —— 和玺彩画之典范，青绿为地，金龙腾跃")
    st.markdown(
        '<div style="text-align:center;color:#7A6A50;font-size:15px;'
        'letter-spacing:2px;margin:6px 0 6px;">择一门而入，探文物色彩之奥</div>',
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
        '<div style="text-align:center;color:#8A7B60;font-size:12px;'
        'font-family:\'Songti SC\',SimSun,serif;letter-spacing:1px;">'
        '本工具所出结果为辅助参考，实际操作须由专业人员依据检测报告裁定。'
        '</div>',
        unsafe_allow_html=True,
    )
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
    col1, col2 = st.columns([0.85, 1.5])
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
    with col2:
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
                    sections.append(("对应建筑风格（据色推求）", items))
                st.markdown(result_panel(sections), unsafe_allow_html=True)
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
        icon="brush",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 1.5])
    with col1:
        target = st.color_picker("目标颜色", "#2E9070", key="target")
        dy_opts2, dy_idx2 = dynasty_options("清")
        dynasty2 = st.selectbox("朝代约束", dy_opts2, index=dy_idx2, key="dyn2")
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
        icon="castle",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 1.5])
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
    with col2:
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
                    result_panel([("风格候选（按匹配度）", items)]),
                    unsafe_allow_html=True,
                )
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
        icon="scroll",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 1.5])
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
        icon="rock",
    ), unsafe_allow_html=True)
    col1, col2 = st.columns([0.85, 1.5])

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

    with col2:
        st.markdown('<div class="gf-result-label">识别与配材结果</div>',
                    unsafe_allow_html=True)
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
                           "可直接生成配材方案。如需调整，可在左侧重新选择后生成。"),
                )]),
                unsafe_allow_html=True,
            )
        else:
            st.info("上传照片或在左侧选定材质与病害后点击「生成修复配材方案」")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="gf-bottom-rule"></div>', unsafe_allow_html=True)
