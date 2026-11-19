# -*- coding: utf-8 -*-
"""商业化展示层：品牌识别、官网落地页板块与商务文案。

纯 HTML 字符串生成，不依赖 Streamlit，便于单独测试与复用。
所有能力指标均取自本仓库真实实现（18+ 朝代知识库、36 通道光谱、
1200 次蒙特卡洛、95% 置信区间、CIEDE2000 / Kubelka-Munk / CIE 1931）。

合规约定：
  · 案例为「依据公开资料整理的研究场景」，绝不冒充商业客户或合作背书；
  · 服务方案为展示示意，不承诺真实报价与在线支付；
  · 演示站表单不落库，输出仅为辅助参考，不构成修复施工依据。
"""

BRAND_NAME = "考色"
BRAND_EN = "KAOSE"
BRAND_FULL = "文物色彩智能考证平台"
BRAND_EN_FULL = "Heritage Color Intelligence Platform"
SLOGAN = "让千年色彩，有据可循"


# ---------------------------------------------------------------- 数据
METRICS = [
    ("18+", "朝代色彩制度", "覆盖历代用色规制与颜料谱系"),
    ("36", "通道光谱建模", "可见光波段反射率与多光源推演"),
    ("1200", "次蒙特卡洛", "测量噪声传播与不确定度量化"),
    ("95%", "置信区间", "贝叶斯后验给出可复核结论"),
]

SOLUTIONS = [
    {
        "no": "01",
        "icon": "档",
        "title": "文博机构 · 色彩数字档案",
        "desc": "把散落在残片、老照片与修缮记录里的色彩信息，沉淀为可检索、可复核的结构化档案。",
        "tags": ["残留色考证", "朝代用色比对", "初色参考色卡"],
        "output": "交付物：色彩考证报告 / 标准色卡 / 溯源证据链",
    },
    {
        "no": "02",
        "icon": "修",
        "title": "保护工程 · 修复方案论证",
        "desc": "在最小干预原则下，为颜料遴选、工艺复原与病害处置提供量化依据，减少反复试错。",
        "tags": ["颜料推演", "材质配材", "最小干预决策"],
        "output": "交付物：颜料配方建议 / 修复决策单 / 风险提示",
    },
    {
        "no": "03",
        "icon": "展",
        "title": "数字展陈与文创 · 复原呈现",
        "desc": "为虚拟复原、数字展陈与文创衍生提供有考证依据的配色，避免「想当然」的历史色。",
        "tags": ["褪色反演", "同色异谱校验", "图像取色"],
        "output": "交付物：复原色板 / 展陈用色规范 / 多光源预览",
    },
    {
        "no": "04",
        "icon": "研",
        "title": "高校与科研 · 教学研究",
        "desc": "开放可解释的推理链路与实验数据，服务于彩画制度、颜料史与保护材料课程教学。",
        "tags": ["朝代知识库", "算法可复现", "SVG 图表导出"],
        "output": "交付物：实验数据集 / 推理过程可视化 / 教学案例",
    },
]

MOATS = [
    ("光谱物理内核", "CIE 1931 2° 标准观察者 · 36 通道反射率 · Kubelka-Munk 混色 · 多光源同色异谱指数",
     "不是「看起来像」，而是从反射率与光源 SPD 出发计算颜色"),
    ("概率推断引擎", "贝叶斯后验 × 朝代先验 × 文献证据 · 1200 次蒙特卡洛 · CIEDE2000 似然",
     "每个结论都附带不确定度，而非单一武断的色值"),
    ("可逆老化动力学", "褪色路径建模 · 时光倒流反演 · 多光源色偏对照",
     "回答「当年是什么颜色」，而不只是「现在是什么颜色」"),
    ("可解释交付", "纯 SVG 色度图 / 光谱曲线 / 置信椭圆 · 结构化考证报告",
     "结论可追溯、可复核、可直接进入项目文档"),
]

PLANS = [
    {
        "name": "体验版", "en": "STARTER", "price": "¥ 0", "unit": "立即体验",
        "featured": False,
        "desc": "面向个人研究者、学生与教学演示",
        "items": ["五大核心模块在线试用", "公开文保场景案例库", "基础色彩考证结论", "社区文档与示例数据"],
        "cta": "免费体验",
    },
    {
        "name": "专业版", "en": "PROFESSIONAL", "price": "¥ 299 起", "unit": "订阅 ¥3,999 / 年",
        "featured": True,
        "desc": "面向修复工作室、项目组与设计机构",
        "items": ["批量考证与任务管理", "光谱分析与置信度报告", "考证报告导出（PDF / 结构化数据）", "专属培训与场景化配置", "优先技术支持"],
        "cta": "立即订购",
        "href": "?view=pay&product=report_single",
    },
    {
        "name": "机构版", "en": "ENTERPRISE", "price": "定制方案", "unit": "私有化部署",
        "featured": False,
        "desc": "面向文博单位、科研院所与大型工程",
        "items": ["私有化 / 内网部署，数据不出域", "专属知识库与颜料谱定制", "业务系统对接与 API", "驻场支持与服务等级协议", "定制算法与联合课题"],
        "cta": "洽谈方案",
        "href": "?view=demo",
    },
]

PROCESS = [
    ("壹", "需求沟通", "明确文保对象、现存资料与期望产出，1 个工作日内响应"),
    ("贰", "场景评估", "基于样例数据评估可行性，确认考证口径与验收标准"),
    ("叁", "方案与试用", "给出配置方案与试用环境，验证结论与业务链路"),
    ("肆", "交付与持续服务", "部署交付、人员培训、知识库迭代与长期技术支持"),
]

FAQS = [
    ("平台结论可以直接作为修复施工依据吗？",
     "不可以。本平台输出属于辅助参考，用于缩小考证范围、提供配色与工艺线索；实际修复须由具备资质的专业人员依据现场勘察与实验室检测报告裁定，并遵守「不改变文物原状」等法定原则。"),
    ("需要上传文物影像吗？数据如何保管？",
     "在线演示站的图片取色在当前会话内完成处理，不会写入服务器数据库，也不会用于模型训练。机构版支持完全私有化部署，影像与知识库均留在客户内网，满足文博单位的数据合规要求。"),
    ("支持与现有系统对接或二次开发吗？",
     "机构版提供 API 与数据接口，可对接藏品管理、病害档案与数字展陈系统；朝代知识库、颜料谱与报告模板均支持按项目定制。"),
    ("不确定度和置信区间有什么实际意义？",
     "文物残留色往往存在测量噪声与信息缺失。平台用蒙特卡洛传播测量误差、以贝叶斯后验融合朝代先验与文献证据，给出 95% 置信区域，让决策者知道「这个结论有多可靠」，而不是只拿到一个色值。"),
    ("如何开始合作？",
     "点击页面右上角「预约商业演示」，填写机构与需求信息即可。我们会在演示中按您的真实场景走一遍完整考证链路，并提供试用环境。"),
]


# ---------------------------------------------------------------- 组件
def nav(active: str = "home") -> str:
    """官网顶部导航条（同页锚点滚动，右侧由 app.py 放真实 CTA 按钮）。"""
    items = [
        ("#biz-capability", "核心能力"),
        ("#biz-solution", "解决方案"),
        ("#biz-tech", "技术壁垒"),
        ("#biz-pricing", "服务方案"),
        ("#biz-process", "合作流程"),
        ("#biz-faq", "常见问题"),
    ]
    links = "".join(
        f'<a class="biz-nav-link{" is-active" if active == "home" and i == 0 else ""}" '
        f'href="{href}" target="_self">{_esc_text(label)}</a>'
        for i, (href, label) in enumerate(items)
    )
    return (
        '<div class="biz-nav" id="biz-top">'
        '<div class="biz-nav-inner">'
        '<div class="biz-nav-brand">'
        '<span class="biz-seal">考</span>'
        '<span class="biz-nav-name">考色 <b>KAOSE</b></span>'
        '<span class="biz-nav-tag">数字文保 · 智能决策</span>'
        '</div>'
        f'<nav class="biz-nav-links">{links}</nav>'
        '</div></div>'
    )


def hero() -> str:
    """首屏左侧：品牌徽标、价值主张、能力要点（右侧指标与按钮由 app.py 渲染）。"""
    return (
        '<section class="biz-hero" id="biz-hero">'
        '<div class="biz-hero-left">'
        '<div class="biz-eyebrow"><i></i> DIGITAL HERITAGE · COLOR INTELLIGENCE</div>'
        f'<h1 class="biz-h1">{SLOGAN}</h1>'
        '<div class="biz-hero-en">KAOSE · Heritage Color Intelligence Platform</div>'
        '<p class="biz-lead">'
        '面向<strong>文博机构、保护工程、数字展陈与高校科研</strong>的文物色彩智能考证与修复辅助决策平台。'
        '把「凭经验判断」变成<strong>可量化、可复核、可交付</strong>的证据链。'
        '</p>'
        '<ul class="biz-hero-points">'
        '<li><span>01</span> 光谱级色彩复原，从反射率与光源出发推求初色</li>'
        '<li><span>02</span> 贝叶斯 + 蒙特卡洛，结论附带 95% 置信区间</li>'
        '<li><span>03</span> 考证—推演—辨识—决策—配材，全链路一键成文</li>'
        '</ul>'
        '<div class="biz-hero-note">适用场景：官式建筑彩画 · 石窟壁画 · 彩塑与装饰构件 · 可移动文物</div>'
        '</div></section>'
    )


def metrics() -> str:
    """首屏右侧：真实能力指标卡。"""
    cards = "".join(
        f'<div class="biz-metric"><b>{n}</b><span class="biz-metric-label">{t}</span>'
        f'<span class="biz-metric-sub">{d}</span></div>'
        for n, t, d in METRICS
    )
    return (
        '<div class="biz-metrics-wrap">'
        '<div class="biz-metrics-head"><span>PLATFORM CAPABILITY</span><b>平台能力速览</b></div>'
        f'<div class="biz-metrics">{cards}</div>'
        '<div class="biz-metrics-foot">CIEDE2000 · Kubelka-Munk · CIE 1931 · 贝叶斯后验</div>'
        '<div class="biz-metrics-disclaimer">指标取自本平台已实现的算法与知识库配置</div>'
        '</div>'
    )


def trust_bar() -> str:
    return (
        '<div class="biz-trust">'
        '<span class="biz-trust-label">服务对象</span>'
        '<span>文博单位</span><i></i><span>文物保护工程机构</span><i></i>'
        '<span>数字展陈与文创</span><i></i><span>高校与科研院所</span>'
        '<span class="biz-trust-badge">辅助决策 · 不替代专业检测</span>'
        '</div>'
    )


def section_head(no: str, en: str, title: str, desc: str, anchor: str) -> str:
    return (
        f'<div class="biz-section-head" id="{anchor}">'
        f'<div class="biz-section-no">{no} / {en}</div>'
        f'<h2 class="biz-h2">{_esc_text(title)}</h2>'
        f'<p class="biz-section-desc">{_esc_text(desc)}</p>'
        '<div class="biz-section-line"></div>'
        '</div>'
    )


def solutions() -> str:
    cards = ""
    for s in SOLUTIONS:
        tags = "".join(f'<span class="biz-tag">{_esc_text(t)}</span>' for t in s["tags"])
        cards += (
            '<article class="biz-card biz-solution">'
            f'<div class="biz-card-top"><span class="biz-card-icon">{s["icon"]}</span>'
            f'<span class="biz-card-no">{s["no"]}</span></div>'
            f'<h3>{_esc_text(s["title"])}</h3>'
            f'<p>{_esc_text(s["desc"])}</p>'
            f'<div class="biz-tags">{tags}</div>'
            f'<div class="biz-card-output">{_esc_text(s["output"])}</div>'
            '</article>'
        )
    return f'<div class="biz-grid-4">{cards}</div>'


def tech_moat() -> str:
    rows = ""
    for i, (title, spec, value) in enumerate(MOATS, 1):
        rows += (
            '<div class="biz-moat">'
            f'<div class="biz-moat-no">0{i}</div>'
            '<div class="biz-moat-body">'
            f'<h4>{_esc_text(title)}</h4>'
            f'<div class="biz-moat-spec">{_esc_text(spec)}</div>'
            f'<div class="biz-moat-value">{_esc_text(value)}</div>'
            '</div></div>'
        )
    return (
        '<div class="biz-moat-wrap">'
        '<div class="biz-moat-intro">'
        '<span>TECHNOLOGY MOAT</span>'
        '<p>不做「滤镜式」上色。考色以色彩科学、概率推断与可解释可视化为内核，'
        '让每一条结论都能回到物理与文献证据。</p>'
        '</div>'
        f'<div class="biz-moat-list">{rows}</div>'
        '</div>'
    )


def pricing() -> str:
    cards = ""
    for p in PLANS:
        items = "".join(f'<li><span>✓</span>{_esc_text(x)}</li>' for x in p["items"])
        badge = '<div class="biz-plan-badge">推荐方案</div>' if p["featured"] else ""
        href = p.get("href", "?view=home")
        cards += (
            f'<article class="biz-plan{" is-featured" if p["featured"] else ""}">'
            f'{badge}'
            f'<div class="biz-plan-en">{p["en"]}</div>'
            f'<h3>{_esc_text(p["name"])}</h3>'
            f'<div class="biz-plan-desc">{_esc_text(p["desc"])}</div>'
            f'<div class="biz-plan-price">{p["price"]}<small>{p["unit"]}</small></div>'
            f'<ul class="biz-plan-list">{items}</ul>'
            f'<a class="biz-plan-cta" href="{href}" target="_self">{_esc_text(p["cta"])}</a>'
            '</article>'
        )
    return (
        f'<div class="biz-grid-3">{cards}</div>'
        '<div class="biz-plan-note">※ 在线支付支持<b>微信支付、支付宝、银联云闪付、数字人民币、对公转账</b>五种方式；'
        '当前商户通道接入前为演示收银台（不产生真实扣款），接入后自动切换真实收款。'
        '报价以商务合同为准，不构成要约。</div>'
    )


def process() -> str:
    steps = "".join(
        f'<div class="biz-step"><div class="biz-step-no">{n}</div>'
        f'<h4>{_esc_text(t)}</h4><p>{_esc_text(d)}</p></div>'
        for n, t, d in PROCESS
    )
    return f'<div class="biz-process">{steps}</div>'


def faq() -> str:
    rows = "".join(
        f'<details class="biz-faq-item"{" open" if i == 0 else ""}>'
        f'<summary>{_esc_text(q)}<span class="biz-faq-plus">＋</span></summary>'
        f'<div class="biz-faq-body">{_esc_text(a)}</div></details>'
        for i, (q, a) in enumerate(FAQS)
    )
    return f'<div class="biz-faq">{rows}</div>'


def cta_band() -> str:
    return (
        '<div class="biz-cta" id="biz-cta">'
        '<div class="biz-cta-inner">'
        '<div class="biz-cta-text">'
        '<div class="biz-cta-en">READY TO START</div>'
        '<h2>把色彩考证，交给可量化的方法</h2>'
        '<p>一次 20 分钟的演示，走完从残留色到修复决策的完整链路。</p>'
        '<div class="biz-cta-sub">免费体验 · 无需注册 · 演示站数据不落库</div>'
        '</div></div></div>'
    )


def footer() -> str:
    caps = " / ".join(["色彩考证", "颜料推演", "建筑风格识别", "修复决策", "材质辨识与配材"])
    return (
        '<footer class="biz-footer">'
        '<div class="biz-footer-inner">'
        '<div class="biz-footer-col">'
        '<div class="biz-footer-brand"><span class="biz-seal">考</span>'
        f'<span>考色 <b>KAOSE</b></span></div>'
        f'<div class="biz-footer-full">{BRAND_FULL}</div>'
        f'<div class="biz-footer-slogan">{SLOGAN}</div>'
        '</div>'
        '<div class="biz-footer-col">'
        '<h5>产品能力</h5>'
        f'<div class="biz-footer-line">{caps}</div>'
        '<div class="biz-footer-line">数智中枢 · 光谱引擎 / 贝叶斯推断 / 蒙特卡洛</div>'
        '<div class="biz-footer-line">文保场景库 · 古建数字化修复案例</div>'
        '</div>'
        '<div class="biz-footer-col">'
        '<h5>商务合作</h5>'
        '<div class="biz-footer-line">预约演示 · 服务方案 · 私有化部署</div>'
        '<div class="biz-footer-line">在线支付 · 微信 / 支付宝 / 云闪付 / 数字人民币 / 对公</div>'
        '<div class="biz-footer-line">机构版支持内网部署与系统对接</div>'
        '<div class="biz-footer-line">演示站表单仅存于当前会话，不会发送至服务器</div>'
        '</div>'
        '</div>'
        '<div class="biz-footer-bottom">'
        '<span>© 2026 考色 KAOSE · 文物色彩智能考证平台</span>'
        '<span>本平台输出仅供辅助参考，不构成修复施工依据；案例资料依据公开报道整理，非商业合作背书。</span>'
        '</div>'
        '</footer>'
    )


def rail_slogan() -> str:
    """内页返回条中间的品牌标语。"""
    return (
        '<div class="biz-rail-slogan">'
        f'<b>考色 KAOSE</b><span>{SLOGAN}</span>'
        '<em>数字文保 · 智能决策</em>'
        '</div>'
    )


def pay_head() -> str:
    """在线订购收银台页标题与说明。"""
    return (
        '<div class="biz-demo-head">'
        '<div class="biz-eyebrow"><i></i> SECURE CHECKOUT / 在线支付</div>'
        '<h2 class="biz-h2">在线订购</h2>'
        '<p class="biz-section-desc">支持微信支付、支付宝、银联云闪付、数字人民币与对公转账。'
        '商户通道接入前为<b>演示收银台</b>：下单、支付、收据全流程可完整体验，不产生真实扣款。</p>'
        '</div>'
    )


def pay_safety() -> str:
    """收银台页安全提示条。"""
    return (
        '<div class="biz-pay-safety">'
        '<span class="biz-pay-safety-item">✓ 订单全程可查询</span>'
        '<span class="biz-pay-safety-item">✓ 电子收据可下载留存</span>'
        '<span class="biz-pay-safety-item">✓ 不存储任何银行卡 / 密码信息</span>'
        '<span class="biz-pay-safety-item">✓ 对公转账支持人工对账确认</span>'
        '</div>'
    )


def demo_head() -> str:
    """商务演示页左侧标题与说明。"""
    return (
        '<div class="biz-demo-head">'
        '<div class="biz-eyebrow"><i></i> BUSINESS INQUIRY / 商务合作</div>'
        '<h2 class="biz-h2">预约商业演示</h2>'
        '<p class="biz-section-desc">留下机构与需求信息，我们会按您的真实文保场景准备演示内容。'
        '当前为在线演示站，表单仅保存在本次会话中。</p>'
        '</div>'
    )


def demo_aside() -> str:
    """商务演示页右侧「演示内容」清单。"""
    return (
        '<div class="biz-demo-aside">'
        '<h4>演示中将为您展示</h4>'
        '<ul>'
        '<li>残留色 → 初色考证的完整推理链路</li>'
        '<li>光谱反射率、置信椭圆与不确定性解读</li>'
        '<li>考证报告的结构化输出与交付形式</li>'
        '<li>私有化部署、知识库定制与 API 对接方案</li>'
        '</ul>'
        '<div class="biz-demo-aside-note">资料保密：可在签署保密协议后提供样例影像与检测数据。</div>'
        '</div>'
    )


def demo_success(org: str, name: str) -> str:
    return (
        '<div class="biz-success">'
        '<div class="biz-success-mark">✓</div>'
        '<h3>需求已记录（演示环境）</h3>'
        f'<p>感谢 {_esc_text(org or "您")}{("，") if org else ""}{_esc_text(name or "")} 的关注。'
        '我们已按本次填写的内容生成一份需求确认单，可点击下方按钮下载留存。</p>'
        '<div class="biz-success-warn">注意：本演示站未接入后端，信息不会发送给我们，也不会存入数据库。'
        '正式商务对接请通过应用发布方提供的联系方式，或在部署正式版后启用 CRM / 邮件通知。</div>'
        '</div>'
    )


def _esc_text(s: str) -> str:
    """静态文案的轻量转义（表单用户输入由 app.py 用 html.escape 处理）。"""
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )
