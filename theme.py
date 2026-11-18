"""古风主题：宣纸底 + 朱砂 / 黛青 / 鎏金，注入到 Streamlit 页面。

纹饰体系（纯 CSS / SVG data-uri，云端开箱即用）：
  · 古建筑虚化衬底 —— 淡淡故宫剪影，宣纸蒙版压住，绝不喧宾夺主
  · 万字回纹铺底 —— 若隐若现的"万字不到头"
  · 云纹带 / 回纹金线带 / 缠枝角花
  · 瓦当徽记 / 旋转金环中心徽 / 朱印
  · 四角祥云卷草、菱形点缀、冰裂纹结果面板
  · 入场动效 + 按钮按压流光 + 墨晕扩散点击特效

字体分层（楷 / 隶 / 行楷 / 宋 / 西文衬线），全部走系统字体栈，无需联网。
集中放 CSS，保持 app.py 只管业务逻辑。
"""

# 字体栈：整站固定为古风书体，优先中文古风字体，云端 Linux 回退到思源宋体。
# 主标题用行楷飘逸、印章编号用隶书古朴、正文用楷体、数字用西文衬线。
FONT_CSS = """
:root{
  --gf-kai:  "STXingkai","Xingkai SC","华文行楷","STKaiti","KaiTi","Kaiti SC","楷体","Noto Serif CJK SC","Source Han Serif SC",serif;
  --gf-li:   "STLiti","LiSu","隶书","Noto Serif CJK SC","Source Han Serif SC",serif;
  --gf-xing: "STXingkai","Xingkai SC","华文行楷","STKaiti","KaiTi","楷体","Noto Serif CJK SC",serif;
  --gf-song: "KaiTi","STKaiti","Kaiti SC","楷体","Songti SC","SimSun","Noto Serif CJK SC","Source Han Serif SC",serif;
  --gf-num:  "Georgia","Times New Roman",serif;
}
"""

# 注意：:root 字体变量必须放进 <style> 内，否则会以纯文本形式泄漏到页面上。
GUOFENG_CSS = """
<style>
""" + FONT_CSS + """
/* ============ 1. 全局：描边古建筑 + 万字回纹花纹 衬底 ============ */
/* 背景图 bg_arch.jpg 已烘焙：网络古建筑照片描边抠主体 + 虚化 + 方框回纹花纹。
   这里再用一层极淡 SVG 回纹点缀，蒙版压得很低，让描边建筑隐约可见而不喧宾夺主。 */
[data-testid="stAppViewContainer"] {
    background-color: #F7EEDC;
    background-image:
        radial-gradient(circle at 50% 42%, rgba(212,175,55,0.16), transparent 58%),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'><path d='M8 8 H47 V47 H8 V8 M15 15 H40 V40 H15 Z M24 8 V15 M24 40 V47 M8 24 H15 M40 24 H47 M27 27 H33 V33 H27 Z' fill='none' stroke='%23A8801F' stroke-opacity='0.10' stroke-width='1'/></svg>"),
        linear-gradient(rgba(247,238,220,0.26), rgba(228,210,172,0.30)),
        url("data:image/jpeg;base64,__BG_URI__");
    background-size: cover, 56px 56px, cover, cover;
    background-position: center, center, center, center center;
    background-attachment: fixed, fixed, fixed, fixed;
    background-repeat: no-repeat, repeat, no-repeat, no-repeat;
}
[data-testid="stApp"] { color: #2E2A24; font-family: var(--gf-song); font-size: 15px; }
h1, h2, h3, [data-testid="stHeader"] { color: #8E1F1A !important; font-family: var(--gf-kai) !important; }

/* 页首 / 页脚回纹金线带 */
.gf-top-rule, .gf-bottom-rule {
    height: 12px; margin: 0 0 6px;
    background-color: #8E1F1A;
    background-image:
        repeating-linear-gradient(90deg,
            transparent 0, transparent 8px,
            rgba(255,243,220,0.85) 8px, rgba(255,243,220,0.85) 10px,
            transparent 10px, transparent 18px),
        linear-gradient(180deg, transparent 0 4px, rgba(212,175,55,0.9) 4px 6px, transparent 6px);
    border-top: 1px solid #D4AF37; border-bottom: 1px solid #D4AF37;
    border-radius: 2px; opacity: 0.85;
}
.gf-bottom-rule { margin: 16px 0 4px; }

/* ============ 2. 主标题（楷体）+ 云纹双翼 ============ */
.gf-title {
    position: relative;
    font-family: var(--gf-kai);
    font-size: 42px; font-weight: 700; letter-spacing: 10px;
    color: #8E1F1A; text-align: center;
    padding: 16px 0 10px; margin: 0;
    border-bottom: 2px solid #D4AF37;
    text-shadow: 1px 1px 0 rgba(255,255,255,0.75);
}
.gf-title::before, .gf-title::after {
    content: ""; position: absolute; top: 14px; width: 64px; height: 40px;
    background-repeat: no-repeat; background-size: contain; opacity: 0.75;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 50'><path d='M2 40 Q2 18 24 18 Q40 18 40 32 Q40 44 30 44 Q22 44 22 36 M40 40 Q40 22 58 22 Q74 22 74 40' fill='none' stroke='%23C4322B' stroke-width='3'/><circle cx='30' cy='32' r='3' fill='%23D4AF37'/></svg>");
}
.gf-title::before { left: 2%; }
.gf-title::after { right: 2%; transform: scaleX(-1); }

.gf-subtitle {
    font-family: var(--gf-li);
    font-size: 15px; letter-spacing: 3px; color: #7A6A50;
    text-align: center; margin: 10px 0 22px;
}

/* 云纹分隔带（替代原来的"云纹"二字） */
.gf-cloud-band {
    height: 26px; margin: 8px 0 6px; position: relative;
    background: no-repeat center / 120px 26px url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 26'><g fill='none' stroke='%23D4AF37' stroke-width='1.6'><path d='M10 18 Q10 8 22 8 Q30 8 30 14 Q30 19 26 19 Q22 19 22 15 M30 18 Q30 10 42 10 Q54 10 54 17 M60 18 Q60 8 72 8 Q84 8 84 17 M90 18 Q90 10 102 10 Q114 10 114 17'/><circle cx='60' cy='6' r='2.4' fill='%23C4322B' stroke='none'/></g></svg>");
}
.gf-cloud-band::before, .gf-cloud-band::after {
    content: ""; position: absolute; top: 50%; width: 32%; height: 1px;
    background: linear-gradient(90deg, transparent, #D4AF37);
}
.gf-cloud-band::before { left: 4%; }
.gf-cloud-band::after  { right: 4%; transform: scaleX(-1); }

/* ============ 3. 瓦当徽记 / 印章（隶书） ============ */
.gf-wadang {
    display: inline-flex; align-items: center; justify-content: center;
    width: 62px; height: 62px; border-radius: 50%;
    background: #C4322B; color: #FFF3DC;
    border: 3px double #FFF3DC; outline: 2px solid #C4322B;
    font-family: var(--gf-li); font-size: 20px; font-weight: 700;
    box-shadow: 2px 3px 6px rgba(0,0,0,0.18);
    position: relative;
}
.gf-wadang::after {
    content: ""; position: absolute; inset: 6px; border-radius: 50%;
    border: 1px dashed rgba(255,243,220,0.55);
}
.gf-seal {
    display: inline-block; font-family: var(--gf-li);
    background: #C4322B; color: #FFF3DC; font-size: 14px;
    padding: 4px 8px; border-radius: 3px; letter-spacing: 2px;
    margin: 0 4px; box-shadow: 2px 2px 0 rgba(0,0,0,0.12);
    border: 1px solid #8E1F1A;
}

/* ============ 4. 卡片：四角祥云 + 缠枝 + 朱印标题（行楷） ============ */
.gf-ornate-card {
    position: relative;
    background-color: #FDF8EC;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%23C4322B' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23D4AF37'/></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='scale(-1,1) translate(-60,0)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%23C4322B' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23D4AF37'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='scale(1,-1) translate(0,-60)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%23C4322B' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23D4AF37'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><g transform='rotate(180 30 30)'><path d='M4 56 L4 20 Q4 8 16 8 Q28 8 28 20 Q28 30 18 30 Q10 30 10 22 M30 4 L56 4 L56 30' fill='none' stroke='%23C4322B' stroke-width='3'/><circle cx='18' cy='20' r='3' fill='%23D4AF37'/></g></svg>");
    background-repeat: no-repeat;
    background-position: top left, top right, bottom left, bottom right;
    background-size: 46px 46px;
    border: 1px solid #E0CB95;
    border-top: 2px solid #C4322B;
    border-bottom: 2px solid #D4AF37;
    border-radius: 4px;
    padding: 24px 24px 18px; margin: 10px 0 18px;
    box-shadow: 0 2px 8px rgba(90,70,40,0.10);
}
.gf-ornate-card::before {
    content: ""; position: absolute; left: 0; right: 0; top: 0; height: 6px;
    background-image: repeating-linear-gradient(90deg,
        #C4322B 0, #C4322B 6px, transparent 6px, transparent 12px);
    opacity: 0.35;
}
.gf-card-title {
    font-family: var(--gf-xing);
    font-size: 22px; font-weight: 700; color: #8E1F1A;
    letter-spacing: 3px; margin: 0 0 4px;
    padding-left: 32px; position: relative;
}
.gf-card-title::before {
    content: "印"; position: absolute; left: 0; top: 1px;
    width: 22px; height: 22px; line-height: 22px; text-align: center;
    font-size: 12px; color: #FFF3DC; background: #C4322B; border-radius: 2px;
    letter-spacing: 0;
}
.gf-card-desc { font-family: var(--gf-song); font-size: 13px; color: #7A6A50; margin-bottom: 12px; }
/* 模块页卡片上的古风小图标 */
.gf-card-icon {
    float: right; width: 40px; height: 40px; object-fit: contain; margin: -2px 0 0 10px;
    filter: sepia(0.3) saturate(0.8) drop-shadow(0 1px 2px rgba(90,70,40,0.22));
}

/* ============ 5. 门牌方块：四角云纹 + 回纹冠 + 编号印（楷/隶） ============ */
.gf-nav-card {
    position: relative;
    background-color: #FDF8EC;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23D4AF37' stroke-width='2'/></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='scale(-1,1) translate(-40,0)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23D4AF37' stroke-width='2'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='scale(1,-1) translate(0,-40)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23D4AF37' stroke-width='2'/></g></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g transform='rotate(180 20 20)'><path d='M4 36 L4 16 Q4 6 14 6 Q24 6 24 16 Q24 24 16 24' fill='none' stroke='%23D4AF37' stroke-width='2'/></g></svg>");
    background-repeat: no-repeat;
    background-position: top left, top right, bottom left, bottom right;
    background-size: 28px 28px;
    border: 1px solid #E0CB95;
    border-top: 4px solid #C4322B;
    border-radius: 6px 6px 2px 2px;
    padding: 18px 16px 14px; height: 158px;
    box-shadow: 0 3px 10px rgba(90,70,40,0.12);
    display: flex; flex-direction: column; justify-content: center;
}
.gf-nav-card::before {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 5px;
    background-image: repeating-linear-gradient(90deg,
        transparent 0, transparent 6px, #D4AF37 6px, #D4AF37 8px);
    opacity: 0.6;
}
.gf-nav-card::after {
    content: "❖"; position: absolute; top: 6px; right: 10px;
    color: #C4322B; font-size: 14px;
}
.gf-nav-num {
    font-family: var(--gf-li);
    font-size: 26px; line-height: 42px; color: #FFF3DC;
    letter-spacing: 1px; margin-bottom: 8px;
    display: inline-block; width: 42px; height: 42px;
    text-align: center; background: #C4322B;
    border: 1px solid #8E1F1A; border-radius: 3px;
    box-shadow: 2px 2px 0 rgba(0,0,0,0.12);
    flex-shrink: 0;
}
.gf-nav-title {
    font-family: var(--gf-kai);
    font-size: 21px; font-weight: 700; color: #8E1F1A;
    letter-spacing: 3px; margin-bottom: 6px;
}
.gf-nav-desc { font-family: var(--gf-song); font-size: 12.5px; color: #7A6A50; line-height: 1.6; }
/* 门牌上的古风小图像（网络检索的 emoji 图标） */
.gf-nav-icon {
    position: absolute; right: 12px; top: 12px;
    width: 34px; height: 34px; object-fit: contain;
    opacity: 0.92; filter: sepia(0.28) saturate(0.85) drop-shadow(0 1px 2px rgba(90,70,40,0.25));
    transition: transform .3s cubic-bezier(.34,1.56,.64,1), filter .3s;
    pointer-events: none;
}
.gf-nav-card:hover .gf-nav-icon { transform: rotate(-12deg) scale(1.18); filter: sepia(0.12) saturate(1.05) drop-shadow(0 2px 4px rgba(196,50,43,0.35)); }
/* 页眉 / 标题旁的小图标 */
.gf-inline-icon { width: 30px; height: 30px; vertical-align: middle; object-fit: contain; filter: sepia(0.3) saturate(0.8); margin: 0 3px; }
.gf-icon-strip { display: flex; align-items: center; justify-content: center; gap: 10px; margin: 2px 0 6px; }
.gf-icon-strip img { width: 26px; height: 26px; object-fit: contain; opacity: 0.8; filter: sepia(0.35) saturate(0.7); }

/* 鼠标触及门牌：上浮 + 金边发光 + 流光扫过 + 编号/星纹轻转 */
.gf-nav-card { transition: transform .28s cubic-bezier(.34,1.56,.64,1), box-shadow .28s, border-color .28s; }
.gf-nav-card:hover {
    transform: translateY(-9px) scale(1.02);
    box-shadow: 0 14px 28px rgba(142,31,26,0.22), 0 0 0 1px #D4AF37, inset 0 0 22px rgba(212,175,55,0.12);
    border-top-color: #D4AF37; z-index: 2;
}
.gf-nav-card:hover .gf-nav-title { color: #C4322B; letter-spacing: 4px; }
.gf-nav-title { transition: color .25s, letter-spacing .25s; }
.gf-nav-card:hover .gf-nav-num { animation: gfNumTilt .5s cubic-bezier(.34,1.56,.64,1); }
@keyframes gfNumTilt { 40% { transform: rotate(-9deg) scale(1.1); } }
.gf-nav-card:hover::after { animation: gfStarSpin .8s ease-out; }
@keyframes gfStarSpin { to { transform: rotate(200deg) scale(1.3); } }
.gf-card-glow {
    position: absolute; inset: 0; pointer-events: none; border-radius: inherit; overflow: hidden;
}
.gf-card-glow::before {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(115deg, transparent 32%, rgba(255,243,220,0.62) 48%, rgba(212,175,55,0.25) 53%, transparent 70%);
    transform: translateX(-125%);
}
.gf-nav-card:hover .gf-card-glow::before { animation: gfCardSheen .9s ease-out; }
@keyframes gfCardSheen { to { transform: translateX(125%); } }

/* ============ 6. 中心「考色」球体：外部圆圈已去除，只留圆形主标识 ============ */
.gf-ring-stage-marker, .gf-ring-node-marker { display: none; }
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) {
    position: relative;
    flex: 0 0 auto !important;
    --r: clamp(195px, 21vw, 225px);
    --rx: clamp(205px, 24vw, 255px);
    width: 100%; max-width: 1100px;
    height: calc(var(--r) + var(--r) + 290px);
    margin: -100px auto 6px !important;
}
/* 取消舞台内部容器的定位上下文，让圆心与门牌相对舞台绝对定位 */
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stElementContainer"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stMarkdown"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stMarkdownContainer"],
div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) [data-testid="stLayoutWrapper"] { position: static !important; }
.gf-ring-center {
    position: absolute; left: 50%; top: 50%;
    transform: translate(-50%, -50%); z-index: 2;
}
.gf-orbit-ring, .gf-orbit-wrap::before, .gf-orbit-wrap::after,
.gf-ring-track, .gf-ring-track-inner { display: none !important; }
.gf-ring-center .gf-orbit-core {
    position: relative;
    width: 132px; height: 132px; border-radius: 50%;
    background:
        radial-gradient(circle at 32% 26%, rgba(255,244,218,0.65), rgba(255,244,218,0) 44%),
        radial-gradient(circle at 68% 76%, rgba(80,12,10,0.55), rgba(80,12,10,0) 56%),
        radial-gradient(circle at 38% 32%, #E05A4A, #C4322B 58%, #7E1712 100%);
    color: #FFF3DC; display: flex; align-items: center; justify-content: center;
    flex-direction: column; font-family: var(--gf-li); font-size: 26px; font-weight: 700;
    letter-spacing: 3px; line-height: 1.35; text-align: center;
    border: 3px double #F3D98A;
    box-shadow:
        inset -9px -11px 24px rgba(70,10,8,0.55),
        inset 7px 7px 20px rgba(255,238,200,0.30),
        0 0 0 6px rgba(212,175,55,0.18),
        0 10px 30px rgba(142,31,26,0.45);
    text-shadow: 0 2px 3px rgba(50,14,10,0.5);
    transition: transform .3s cubic-bezier(.34,1.56,.64,1);
}
.gf-ring-center .gf-orbit-core:hover { transform: scale(1.07); }
.gf-orbit-core::before {
    content: ""; position: absolute; left: 28px; top: 22px;
    width: 32px; height: 19px; border-radius: 50%;
    background: radial-gradient(ellipse, rgba(255,248,232,0.72), rgba(255,248,232,0) 70%);
    transform: rotate(-28deg); pointer-events: none;
}
.gf-orbit-core small { font-family: var(--gf-song); font-size: 10px; letter-spacing: 2px; opacity: 0.85; color: #F3D98A; }

/* ============ 6b. 五门环形舞台：五门牌均匀绕中心圆摆放 ============ */
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {
    position: absolute; width: 224px; z-index: 3;
    transform: translate(-50%, -50%);
    transition: transform .28s cubic-bezier(.34,1.56,.64,1);
}
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n1):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) { left: 50%; top: calc(50% - var(--r)); }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n2):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) { left: calc(50% + var(--rx) * 0.951); top: calc(50% - var(--r) * 0.309); }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n3):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) { left: calc(50% + var(--rx) * 0.588); top: calc(50% + var(--r) * 0.809); }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n4):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) { left: calc(50% - var(--rx) * 0.588); top: calc(50% + var(--r) * 0.809); }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n5):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) { left: calc(50% - var(--rx) * 0.951); top: calc(50% - var(--r) * 0.309); }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover { z-index: 6; }
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n1):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n2):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n3):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n4):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover,
div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker.n5):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {
    transform: translate(-50%, calc(-50% - 8px)) scale(1.03);
}
/* 窄屏降级：改为纵向卷轴，仍保留中心在上、五门依次排布 */
@media (max-width: 760px) {
    div[data-testid="stVerticalBlock"]:has(.gf-ring-stage-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-stage-marker)) {
        height: auto; margin-top: 0 !important; display: flex; flex-direction: column; align-items: center; gap: 14px;
    }
    .gf-ring-center { position: relative; left: auto; top: auto; transform: none; order: -1; }
    div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)) {
        position: relative; left: auto !important; top: auto !important;
        transform: none !important; width: min(100%, 320px);
    }
    div[data-testid="stVerticalBlock"]:has(.gf-ring-node-marker):not(:has(div[data-testid="stVerticalBlock"] .gf-ring-node-marker)):hover {
        transform: translateY(-6px) scale(1.02) !important;
    }
}

/* ============ 7. 回纹带 / 云纹分隔 ============ */
.gf-meander {
    height: 14px; margin: 14px 0;
    background-color: #C4322B;
    background-image:
        repeating-linear-gradient(90deg,
            transparent 0, transparent 8px,
            rgba(255,243,220,0.85) 8px, rgba(255,243,220,0.85) 10px,
            transparent 10px, transparent 18px),
        linear-gradient(180deg, transparent 0 5px, #D4AF37 5px 9px, transparent 9px);
    opacity: 0.8; border-radius: 2px;
}
.gf-cloud-divider {
    text-align: center; color: #C4322B; font-size: 18px;
    letter-spacing: 14px; margin: 2px 0 14px; opacity: 0.9;
    font-family: var(--gf-kai); position: relative;
}
.gf-cloud-divider::before, .gf-cloud-divider::after {
    content: ""; position: absolute; top: 50%; width: 26%; height: 1px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
}
.gf-cloud-divider::before { left: 4%; }
.gf-cloud-divider::after { right: 4%; transform: scaleX(-1); }

/* ============ 8. 图片横幅：双金线 + 行楷题字 ============ */
.gf-banner {
    position: relative; border-radius: 4px; overflow: hidden;
    border: 1px solid #D4AF37; outline: 1px solid #C4322B;
    outline-offset: 3px; margin: 8px 0 20px;
    box-shadow: 0 3px 12px rgba(90,70,40,0.15);
    background: #8E1F1A;
}
.gf-banner img { display: block; width: 100%; height: 220px; object-fit: cover; }
.gf-banner-cap {
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 26px 20px 10px;
    background: linear-gradient(transparent, rgba(43,38,30,0.82));
    color: #F5EFE1; font-family: var(--gf-xing);
    font-size: 17px; letter-spacing: 4px;
    border-top: 1px solid rgba(212,175,55,0.7);
}
.gf-banner-cap small {
    display: block; font-family: var(--gf-song);
    font-size: 11px; letter-spacing: 1px;
    opacity: 0.85; margin-top: 3px;
}

/* ============ 9. 结果区：整洁排版（分区 / 键值 / 徽章 / 冰裂纹面板） ============ */
.gf-result-label {
    font-family: var(--gf-xing);
    font-size: 18px; font-weight: 700; color: #126A66;
    letter-spacing: 3px; border-bottom: 1px dashed #9CB3AF;
    padding-bottom: 5px; margin: 10px 0 12px;
}
.gf-result-label::before { content: "◆ "; color: #D4AF37; font-size: 12px; }
.gf-result-panel {
    position: relative; background: rgba(251,246,234,0.86);
    border: 1px solid #E0CB95; border-left: 3px solid #C4322B;
    border-radius: 4px; padding: 14px 16px 14px; margin: 8px 0 14px;
    box-shadow: 0 1px 6px rgba(90,70,40,0.08);
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'><path d='M0 12 L12 0 M28 40 L40 28 M0 28 L12 40 M28 0 L40 12' stroke='%23D4AF37' stroke-opacity='0.18' stroke-width='1' fill='none'/></svg>");
    transition: box-shadow .28s, border-left-color .28s, transform .28s;
    /* 横向排列：每个小节成为一张卡片，宽度足够时自动并排 */
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px 16px; align-items: start;
}
.gf-result-panel:hover {
    border-left-color: #D4AF37;
    box-shadow: 0 4px 16px rgba(90,70,40,0.14), inset 0 0 24px rgba(212,175,55,0.08);
    transform: translateX(3px);
}
/* 窄屏或手机端才退回单列，桌面端保持横向并排 */
@media (max-width: 700px) {
    .gf-result-panel { grid-template-columns: 1fr; }
}
.gf-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 2px 0; }
/* 表头是英文/技术字段名，用清晰黑体，避免行楷连笔看不清 */
.gf-table th { font-family: "Noto Sans CJK SC","Microsoft YaHei","PingFang SC",Arial,sans-serif; color: #FFF3DC; background: #C4322B; padding: 7px 9px; text-align: left; font-weight: 700; font-size: 13px; font-style: normal; letter-spacing: 0.5px; }
.gf-table td { padding: 7px 9px; border-bottom: 1px dotted #E6D6A8; color: #3E372D; }
.gf-table tr:nth-child(even) td { background: rgba(212,175,55,0.06); }
.gf-table tr:hover td { background: rgba(196,50,43,0.07); }
.gf-note { font-family: var(--gf-song); font-size: 13px; line-height: 1.8; color: #6E5C42; background: rgba(212,175,55,0.07); border-left: 2px solid #D4AF37; padding: 6px 10px; margin: 4px 0 8px; }
.gf-style-item { padding: 6px 0 10px; border-bottom: 1px dotted #E6D6A8; }
.gf-style-item:last-child { border-bottom: none; }
.gf-step-line { display: flex; gap: 10px; align-items: flex-start; padding: 4px 0; line-height: 1.7; }
.gf-step-no { flex: 0 0 22px; height: 22px; line-height: 22px; text-align: center; background: #C4322B; color: #FFF3DC; border-radius: 2px; font-family: var(--gf-li); font-size: 12px; }
.gf-risk { font-family: var(--gf-song); font-size: 13px; line-height: 1.75; color: #A82821; background: rgba(196,50,43,0.08); border-left: 3px solid #C4322B; padding: 8px 10px; margin: 4px 0 8px; }
/* 结果列整体面板化：整列成为一张古风卷宗 */
[data-testid="stColumn"]:has(.gf-result-label) {
    background: rgba(251,246,234,0.66);
    border: 1px solid #E8D7A8;
    border-top: 3px solid #C4322B;
    border-radius: 5px;
    padding: 16px 18px !important;
    box-shadow: 0 2px 12px rgba(90,70,40,0.09);
}
.gf-sec { margin: 0 0 14px; }
.gf-sec:last-child { margin-bottom: 8px; }
.gf-sec-title {
    font-family: var(--gf-kai); font-size: 15px; color: #8E1F1A;
    letter-spacing: 2px; padding: 0 0 5px 20px; position: relative;
    border-bottom: 1px solid #E6D9B8; margin-bottom: 8px;
}
.gf-sec-title::before { content: "◆"; position: absolute; left: 0; top: 0; color: #D4AF37; font-size: 11px; }
.gf-sec-body { font-size: 14px; line-height: 1.85; color: #3E372D; padding-left: 2px; }
.gf-kv { display: flex; gap: 10px; padding: 2px 0; border-bottom: 1px dotted #E6D6A8; }
.gf-kv:last-child { border-bottom: none; }
.gf-kv-key { font-family: var(--gf-song); color: #6E5C42; flex: 0 0 76px; }
.gf-kv-val { flex: 1; color: #3E372D; }
.gf-badge {
    display: inline-block; font-family: var(--gf-li); font-size: 13px;
    padding: 3px 11px; border-radius: 2px; margin: 0 6px 6px 0; letter-spacing: 1px;
}
.gf-badge-red  { background: #C4322B; color: #FFF3DC; border: 1px solid #8E1F1A; }
.gf-badge-gold { background: #D4AF37; color: #FDF8EC; border: 1px solid #8A6A34; }
.gf-badge-teal { background: #126A66; color: #F1EADB; border: 1px solid #16443F; }
.gf-num { font-family: var(--gf-num); font-size: 21px; color: #C4322B; font-weight: bold; }
.gf-swatch-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.gf-swatch {
    display: inline-block; width: 46px; height: 46px;
    border: 2px solid #FDF8EC; border-radius: 3px;
    box-shadow: 0 0 0 1px #C9B477, 1px 2px 4px rgba(0,0,0,0.2);
    vertical-align: middle; margin-right: 8px;
}
.gf-swatch-label {
    font-family: var(--gf-num); font-size: 15px; color: #4A4034; letter-spacing: 1px;
}

/* ============ 10. 按钮：按压回弹 + 金色流光 + 墨晕扩散点击特效 ============ */
[data-testid="stButton"] button {
    font-family: var(--gf-kai) !important;
    background: linear-gradient(180deg, #D9483B, #A82821) !important; color: #FFF3DC !important;
    border: 1px solid #D4AF37 !important; border-radius: 3px !important;
    letter-spacing: 2px; font-size: 15px !important;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 12px rgba(142,31,26,0.38);
    transition: transform .12s cubic-bezier(.34,1.56,.64,1), box-shadow .2s, background .2s, color .2s;
}
[data-testid="stButton"] button:hover {
    background: linear-gradient(180deg, #C4322B, #8E1F1A) !important; color: #FFF6E6 !important;
    box-shadow: 0 0 0 1px #F3D98A, 0 8px 20px rgba(142,31,26,0.48);
    transform: translateY(-2px);
}
[data-testid="stButton"] button::before {
    content: ""; position: absolute; top: 0; left: -60%; width: 40%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,243,220,0.5), transparent);
    transform: skewX(-25deg); pointer-events: none;
}
[data-testid="stButton"] button:hover::before { animation: gfSheen .75s ease-out; }
@keyframes gfSheen { to { left: 130%; } }
[data-testid="stButton"] button:active {
    transform: translateY(1px) scale(.95);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.35), 0 0 0 2px #D4AF37;
    background: #8E1F1A !important;
}
[data-testid="stButton"] button::after {
    content: ""; position: absolute; left: 50%; top: 50%;
    width: 12px; height: 12px; margin: -6px 0 0 -6px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,243,220,0.6), rgba(212,175,55,0.3) 55%, transparent 72%);
    transform: scale(0); opacity: 0; pointer-events: none;
}
[data-testid="stButton"] button:active::after { animation: gfInkRipple .5s ease-out; }
@keyframes gfInkRipple {
    0%   { transform: scale(0);  opacity: 1; }
    100% { transform: scale(28); opacity: 0; }
}

[data-testid="stAlert"] {
    background: #F7EEDC !important;
    border: 1px solid #E0CB95 !important;
    border-left: 4px solid #C4322B !important;
    border-radius: 3px !important;
}
.stCaption { color: #6E5C42 !important; }
hr { border-color: #E0CB95 !important; }
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid #D4AF37; }
[data-baseweb="tab"] {
    font-family: var(--gf-kai) !important;
    font-size: 16px !important; letter-spacing: 2px;
    color: #6E5C42 !important; background: #E8D9B8 !important;
    border: 1px solid #E0CB95 !important; border-bottom: none !important;
    border-radius: 4px 4px 0 0 !important; padding: 10px 18px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #C4322B !important; color: #FFF3DC !important;
    border-color: #C4322B !important;
}

/* 小标题上的朱砂方印（楷体） */
.gf-step-title {
    font-family: var(--gf-kai); font-size: 16px;
    color: #8E1F1A; letter-spacing: 2px; margin: 6px 0 10px;
    padding-left: 26px; position: relative;
}
.gf-step-title::before {
    content: "壹"; position: absolute; left: 0; top: 0;
    width: 20px; height: 20px; line-height: 20px; text-align: center;
    font-size: 11px; color: #FFF3DC; background: #C4322B;
    border-radius: 2px; letter-spacing: 0;
}

/* ============ 11. 入场动态特效 ============ */
.gf-enter { animation: gfUnfurl 0.62s cubic-bezier(0.22, 0.61, 0.36, 1) both; }
@keyframes gfUnfurl {
    from { opacity: 0; transform: translateY(22px); filter: blur(2px); }
    to   { opacity: 1; transform: translateY(0);    filter: blur(0); }
}
.gf-nav-card { animation: gfCardRise 0.5s ease-out both; }
.gf-nav-card:nth-of-type(1) { animation-delay: 0.05s; }
.gf-nav-card:nth-of-type(2) { animation-delay: 0.13s; }
.gf-nav-card:nth-of-type(3) { animation-delay: 0.21s; }
@keyframes gfCardRise {
    from { opacity: 0; transform: translateY(16px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
.gf-banner img {
    animation: gfReveal 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
    transform-origin: left center;
}
@keyframes gfReveal {
    from { transform: scaleX(0.05); opacity: 0.3; }
    to   { transform: scaleX(1);    opacity: 1; }
}
.gf-meander, .gf-top-rule {
    background-size: 18px 100%, 100% 100%;
    animation: gfFlow 6s linear infinite;
}
@keyframes gfFlow {
    from { background-position: 0 0, 0 0; }
    to   { background-position: 180px 0, 0 0; }
}
.gf-nav-num, .gf-wadang {
    animation: gfStamp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
@keyframes gfStamp {
    from { transform: scale(1.35) rotate(-8deg); opacity: 0; }
    to   { transform: scale(1) rotate(0);        opacity: 1; }
}
/* 揭幕转场层 */
.gf-curtain {
    position: fixed; inset: 0; z-index: 9999; pointer-events: none;
    background: #F7EEDC;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    animation: gfCurtainLift 0.7s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}
.gf-curtain-seal {
    width: 76px; height: 76px; line-height: 76px; text-align: center;
    background: #C4322B; color: #FFF3DC;
    font-family: var(--gf-li); font-size: 30px;
    border: 3px double #FFF3DC; outline: 2px solid #C4322B;
    box-shadow: 3px 4px 10px rgba(0,0,0,0.2);
    animation: gfSealPulse 0.7s ease-out both;
}
.gf-curtain-line {
    margin-top: 18px; width: 160px; height: 3px; background: #D4AF37;
    animation: gfLineGrow 0.7s ease-out both;
}
@keyframes gfCurtainLift {
    0%   { clip-path: inset(0 0 0 0);   opacity: 1; }
    70%  { clip-path: inset(0 0 0 0);   opacity: 1; }
    100% { clip-path: inset(0 0 100% 0); opacity: 0; }
}
@keyframes gfSealPulse {
    0%   { transform: scale(0.6) rotate(-15deg); opacity: 0; }
    45%  { transform: scale(1.1) rotate(3deg);   opacity: 1; }
    100% { transform: scale(1) rotate(0);        opacity: 0.9; }
}
@keyframes gfLineGrow {
    0%   { transform: scaleX(0); opacity: 0; }
    60%  { transform: scaleX(1); opacity: 1; }
    100% { transform: scaleX(1); opacity: 0; }
}
</style>
"""


def apply_theme(background_uri: str = "") -> None:
    """注入古风 CSS。需在 set_page_config 之后、其它组件之前调用。

    background_uri: 虚化古建筑背景图的 data URI（不含则仅宣纸底）。
    """
    import streamlit as st
    css = GUOFENG_CSS.replace("__BG_URI__", background_uri)
    st.markdown(css, unsafe_allow_html=True)

