"""WorkBuddy 云服务接入（可选增强）：把预约同步至云端 demo_requests 表。

主存储是 demo_store.py 的本地需求库；本模块仅在拿到 publicConfig 后
额外同步一份到云端。endpoint / publishableKey 留空时云同步关闭，
站点照常把需求保存在本地需求库，不影响任何功能。

表结构（由管理通道创建，RLS 仅允许匿名 INSERT、禁止读取）：
  demo_requests(id, org, contact_person, contact_method,
                org_type, directions JSONB, message, created_at)
"""
import inspect
import json
import os
from functools import lru_cache

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------- 连接配置
# 以下两值取自 activate 结果的 publicConfig，发布前必须填入；
# 留空 = 云同步关闭，页面显示演示环境提示。
CLOUD_PUBLIC_CONFIG = {
    "endpoint": "",          # TODO: 填入 publicConfig.endpoint
    "publishableKey": "",    # TODO: 填入 publicConfig.publishableKey
    "oauthRelayBaseUrl": "", # 无登录页可留空
}

# SDK 全局构建随项目一起发布（assets/），页面直接内嵌，
# 不依赖任何外部 CDN，国内网络与手机端均可稳定加载。
_SDK_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "workbuddy-cloud-sdk.global.js")
_SDK_CDN_FALLBACK = ("https://cdn.jsdelivr.net/npm/"
                     "@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js")


@lru_cache(maxsize=1)
def _sdk_script_tag() -> str:
    """优先内嵌本地 SDK；文件缺失（分片缓存）时回退 CDN。"""
    try:
        with open(_SDK_FILE, "r", encoding="utf-8") as f:
            js = f.read()
        if "createWorkBuddyCloud" in js and "</script" not in js.lower():
            return "<script>\n" + js + "\n</script>"
    except Exception:
        pass
    return f'<script src="{_SDK_CDN_FALLBACK}"></script>'

_STATUS_CSS = (
    "body{margin:0;background:transparent;}"
    "#cs{font-family:'Noto Sans CJK SC','Microsoft YaHei','PingFang SC',Arial,sans-serif;"
    "font-size:13px;line-height:1.6;padding:10px 14px;border-radius:8px;"
    "background:#FBF6EC;border:1px solid #E7D9BC;color:#5A4A2F;}"
    "#cs b{font-weight:800;}"
)


def cloud_ready() -> bool:
    """endpoint 与 publishableKey 均已填入才视为云同步可用。"""
    cfg = CLOUD_PUBLIC_CONFIG
    return bool(cfg.get("endpoint")) and bool(cfg.get("publishableKey"))


def _safe_json(obj) -> str:
    """内嵌 <script> 的 JSON：转义 < > &，杜绝 </script> 注入。"""
    return (json.dumps(obj, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def render_demo_sync_html(rec: dict, ref: str = "") -> str:
    """生成云同步 iframe 的完整 HTML（纯函数，便于离线校验）。

    ref 为本地需求编号，仅用于浏览器端幂等键，避免页面 rerun 重复写入云端。
    """
    if not cloud_ready():
        return ""
    cfg = CLOUD_PUBLIC_CONFIG

    dirs = rec.get("关注方向", "")
    if isinstance(dirs, str):
        dirs = [d for d in dirs.split("、") if d and d != "未填写"]

    payload = {
        "org": rec.get("机构", ""),
        "contact_person": rec.get("联系人", ""),
        "contact_method": rec.get("联系方式", ""),
        "org_type": rec.get("机构类型", ""),
        "directions": dirs,
        "message": rec.get("需求描述", ""),
    }

    relay = cfg.get("oauthRelayBaseUrl") or ""
    init_obj = {"endpoint": cfg["endpoint"], "publishableKey": cfg["publishableKey"]}
    if relay:
        init_obj["oauthRelayBaseUrl"] = relay

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{_STATUS_CSS}</style></head><body>
<div id="cs">⏳ 正在同步至云端需求库…</div>
{_sdk_script_tag()}
<script>
(function () {{
  var el = document.getElementById('cs');
  var payload = {_safe_json(payload)};
  var ref = {_safe_json(ref)};
  function done(ok, msg) {{
    el.innerHTML = ok
      ? '<b style="color:#1E7A46;">✓ 已保存至云端需求库</b>　我们将通过你留下的联系方式跟进。'
      : '<b style="color:#B3261E;">⚠ 云端同步未完成</b>　' + (msg || '') +
        '　需求已保存在本站需求库，可在下方下载确认单留存。';
  }}
  var key = 'kaose_demo_synced_' + ref;
  try {{ if (ref && localStorage.getItem(key)) {{ done(true); return; }} }} catch (e) {{}}
  try {{
    var cloud = WorkBuddyCloud.createWorkBuddyCloud({_safe_json(init_obj)});
    cloud.database.from('demo_requests').insert(payload).then(function (r) {{
      var ok = !(r && r.error);
      if (ok) {{ try {{ if (ref) localStorage.setItem(key, '1'); }} catch (e) {{}} }}
      done(ok, r && r.error ? (r.error.message || '写入被拒绝') : '');
    }}).catch(function (e) {{
      done(false, (e && e.message) || '网络异常');
    }});
  }} catch (e) {{
    done(false, (e && e.message) || '云端组件加载失败');
  }}
}})();
</script></body></html>"""
    return html


def _inject(html: str) -> None:
    """用 iframe(srcdoc) 注入，保证内嵌 <script> 真正执行。

    实测：新版 st.html 是往 DOM 里 innerHTML 插入内容，<script> 被过滤且不执行，
    状态会一直停在「⏳」。components.html 虽标记弃用但会生成 srcdoc iframe，
    脚本正常执行；若未来该 API 被移除，则显示明确降级提示（绝不静默失败）。
    """
    try:
        components.html(html, height=64, scrolling=False)
        return
    except Exception:
        pass
    fn = getattr(st, "html", None)
    if callable(fn):
        try:
            fn('<div style="font:13px/1.6 sans-serif;padding:10px 14px;border-radius:8px;'
               'background:#FBF6EC;border:1px solid #E7D9BC;color:#B3261E;">'
               '⚠ 当前运行环境不支持云端同步组件，本次需求未写入云端。'
               '请下载下方需求确认单留存，或稍后重试提交。</div>',
               **({"unsafe_allow_javascript": False}
                  if "unsafe_allow_javascript" in inspect.signature(fn).parameters else {}))
            return
        except Exception:
            pass
    st.warning("云端同步组件不可用，本次需求未写入云端。请下载需求确认单留存后重试。")


def demo_sync_component(rec: dict, ref: str = "") -> None:
    """提交成功后注入浏览器端组件：用云端 SDK 把预约写入 demo_requests。

    同步结果直接显示在 iframe 内（成功 / 失败均可见，不静默）。
    """
    html = render_demo_sync_html(rec, ref=ref)
    if html:
        _inject(html)
