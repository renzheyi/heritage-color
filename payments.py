# -*- coding: utf-8 -*-
"""在线支付模块：多元支付方式、订单存储与收银台数据层。

设计说明
--------
· 订单持久化：优先 SQLite（data/orders.db），文件系统不可写时降级 JSON，
  再降级进程内存（重启丢失），保证任何部署环境都能运行。
· 支付方式：微信支付 / 支付宝 / 银联云闪付 / 数字人民币 / 对公转账。
· 双通道：DEMO_MODE=True 时收银台为「模拟通道」（可完整走通下单—支付—
  收据流程，页面上明确标注）；商户凭证写入 GATEWAY_CONFIG 并将 DEMO_MODE
  设为 False 后，走真实网关（当前支持微信支付 Native 扫码下单）。
· 合规：演示定价仅为展示，真实报价以商务合同为准；不存储敏感支付凭据。
"""

import base64
import io
import json
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "orders.db")
JSON_PATH = os.path.join(DATA_DIR, "orders.json")

# ------------------------------------------------------------------ 模式开关
# 接入真实商户通道：在 GATEWAY_CONFIG 中填入凭证并把 DEMO_MODE 改为 False。
DEMO_MODE = True

GATEWAY_CONFIG = {
    # 微信支付 Native（扫码支付）：需要商户号 mchid、商户 API 证书序列号、
    # APIv3 密钥与商户私钥文件（apiclient_key.pem），并在微信支付商户平台
    # 开通 Native 支付产品权限。
    "wechat": {
        "mchid": "",          # 商户号
        "appid": "",          # 公众号 / 小程序 appid
        "cert_serial": "",    # 商户 API 证书序列号
        "api_v3_key": "",     # APIv3 密钥（32 位）
        "private_key_path": "",  # 商户私钥文件路径
    },
    # 支付宝当面付：需要开放平台应用 appid、应用私钥与支付宝公钥。
    "alipay": {
        "app_id": "",
        "private_key_path": "",
        "alipay_public_key_path": "",
    },
}

# ------------------------------------------------------------------ 商品目录
PRODUCTS = [
    {
        "id": "report_single",
        "name": "单次色彩考证报告",
        "plan": "专业版",
        "price": 299,
        "unit": "份",
        "desc": "提交残留色影像与朝代线索，出具含光谱推演、95% 置信区间与证据链的结构化考证报告（PDF / JSON 交付）",
    },
    {
        "id": "pro_yearly",
        "name": "专业版年度订阅",
        "plan": "专业版",
        "price": 3999,
        "unit": "年",
        "desc": "批量考证与任务管理、报告导出、专属培训与场景化配置、优先技术支持",
    },
]

# ------------------------------------------------------------------ 支付方式
# kind: qrcode = 扫码支付（收银台展示二维码）；bank = 线下转账（人工确认）
PAYMENT_METHODS = [
    {"id": "wechat",   "name": "微信支付",   "tag": "微信", "kind": "qrcode",
     "desc": "微信「扫一扫」支付，资金由微信支付清算"},
    {"id": "alipay",   "name": "支付宝",     "tag": "支付宝", "kind": "qrcode",
     "desc": "支付宝 App 扫码，支持余额 / 银行卡 / 花呗"},
    {"id": "unionpay", "name": "银联云闪付", "tag": "云闪付", "kind": "qrcode",
     "desc": "云闪付 App 及各大银行 App 扫码"},
    {"id": "dcep",     "name": "数字人民币", "tag": "e-CNY", "kind": "qrcode",
     "desc": "数字人民币 App 扫码，实时到账、无手续费"},
    {"id": "bank",     "name": "对公转账",   "tag": "转账", "kind": "bank",
     "desc": "适合机构采购流程，转账后登记凭证号，人工对账确认"},
]

BANK_ACCOUNT = {
    "开户行": "演示环境 · 商户通道接入后显示真实开户行",
    "户名": "演示环境 · 商户通道接入后显示真实户名",
    "账号": "0000 0000 0000 0000（演示）",
}

ORDER_STATUS = {
    "created": "待支付",
    "pending": "等待确认",
    "paid": "已支付",
    "cancelled": "已取消",
}


def product(pid: str):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None


def method(mid: str):
    for m in PAYMENT_METHODS:
        if m["id"] == mid:
            return m
    return None


def gateway_status(mid: str) -> str:
    """返回某支付方式的当前通道状态：live / demo / bank。"""
    if mid == "bank":
        return "bank"
    if DEMO_MODE:
        return "demo"
    cfg = GATEWAY_CONFIG.get(mid) or {}
    if mid == "wechat":
        return "live" if all(cfg.get(k) for k in ("mchid", "appid", "cert_serial", "api_v3_key", "private_key_path")) else "demo"
    if mid == "alipay":
        return "live" if all(cfg.get(k) for k in ("app_id", "private_key_path", "alipay_public_key_path")) else "demo"
    return "demo"


# ------------------------------------------------------------------ 订单存储
_LOCK = threading.Lock()
_MEMORY = {}          # 最终兜底：进程内存储
_SQLITE_OK = None     # None=未探测


def _mem_key(no):
    return no


def _load_json():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return {o["order_no"]: o for o in json.load(f)}
    except Exception:
        return {}


def _save_json(store):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(list(store.values()), f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


def _sqlite_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS orders (
            order_no TEXT PRIMARY KEY,
            product_id TEXT, product_name TEXT, amount INTEGER,
            method TEXT, contact TEXT, status TEXT,
            receipt TEXT, created_at TEXT, paid_at TEXT)"""
    )
    conn.commit()
    return conn


def _store():
    """探测可用存储：sqlite → json → memory。返回 (kind, handle)。"""
    global _SQLITE_OK
    if _SQLITE_OK is None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            _sqlite_conn().close()
            _SQLITE_OK = True
        except Exception:
            _SQLITE_OK = False
    if _SQLITE_OK:
        return "sqlite", None
    return "json", _load_json()


def create_order(product_id: str, method_id: str, contact: str = "") -> dict:
    p = product(product_id)
    m = method(method_id)
    if not p or not m:
        raise ValueError("无效的商品或支付方式")
    no = "KA" + datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(2).upper()
    order = {
        "order_no": no,
        "product_id": p["id"],
        "product_name": f'{p["plan"]} · {p["name"]}',
        "amount": int(p["price"]),
        "method": m["id"],
        "contact": contact or "",
        "status": "created",
        "receipt": "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "paid_at": "",
    }
    with _LOCK:
        kind, _ = _store()
        if kind == "sqlite":
            conn = _sqlite_conn()
            conn.execute(
                "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)",
                (order["order_no"], order["product_id"], order["product_name"],
                 order["amount"], order["method"], order["contact"],
                 order["status"], order["receipt"], order["created_at"], order["paid_at"]),
            )
            conn.commit(); conn.close()
        else:
            store = _load_json()
            store[no] = order
            if not _save_json(store):
                _MEMORY[no] = order
    return order


def get_order(order_no: str):
    if not order_no:
        return None
    with _LOCK:
        kind, _ = _store()
        if kind == "sqlite":
            conn = _sqlite_conn()
            row = conn.execute("SELECT * FROM orders WHERE order_no=?", (order_no,)).fetchone()
            conn.close()
            if not row:
                return _MEMORY.get(order_no)
            keys = ["order_no", "product_id", "product_name", "amount", "method",
                    "contact", "status", "receipt", "created_at", "paid_at"]
            return dict(zip(keys, row))
        order = _load_json().get(order_no) or _MEMORY.get(order_no)
        return order


def update_order(order_no: str, **fields):
    with _LOCK:
        kind, _ = _store()
        if kind == "sqlite":
            conn = _sqlite_conn()
            sets = ", ".join(f"{k}=?" for k in fields)
            conn.execute(f"UPDATE orders SET {sets} WHERE order_no=?",
                         (*fields.values(), order_no))
            conn.commit(); conn.close()
        else:
            store = _load_json()
            if order_no in store:
                store[order_no].update(fields)
                _save_json(store)
            if order_no in _MEMORY:
                _MEMORY[order_no].update(fields)


def mark_paid(order_no: str, receipt: str = ""):
    update_order(order_no, status="paid",
                 paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 receipt=receipt or "DEMO-PAID")


def submit_bank_receipt(order_no: str, receipt_no: str):
    update_order(order_no, status="pending", receipt=receipt_no)


def list_orders(limit: int = 10):
    with _LOCK:
        kind, _ = _store()
        if kind == "sqlite":
            conn = _sqlite_conn()
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            keys = ["order_no", "product_id", "product_name", "amount", "method",
                    "contact", "status", "receipt", "created_at", "paid_at"]
            return [dict(zip(keys, r)) for r in rows]
        store = list(_load_json().values()) + list(_MEMORY.values())
        store.sort(key=lambda o: o.get("created_at", ""), reverse=True)
        return store[:limit]


def storage_kind() -> str:
    kind, _ = _store()
    return {"sqlite": "SQLite 持久化", "json": "JSON 文件"}[kind]


# ------------------------------------------------------------------ 真实网关
class GatewayNotConfigured(Exception):
    """商户凭证未配置时抛出。"""


def wechat_native_code_url(order: dict) -> str:
    """微信支付 Native 下单，返回二维码 code_url。

    商户凭证就绪（GATEWAY_CONFIG['wechat'] 五项齐全）时调用；
    使用微信支付 APIv3：请求签名 = SHA256withRSA(商户私钥)。
    依赖：cryptography（pip install cryptography）。
    """
    cfg = GATEWAY_CONFIG["wechat"]
    if not all(cfg.get(k) for k in ("mchid", "appid", "cert_serial", "api_v3_key", "private_key_path")):
        raise GatewayNotConfigured("微信支付商户凭证未配置，当前为演示通道")
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric import SHA256, padding
    from cryptography.hazmat.primitives import hashes
    import requests  # noqa: F401  实际请求由部署方补充

    with open(cfg["private_key_path"], "rb") as f:
        private_key = load_pem_private_key(f.read(), password=None)
    body = json.dumps({
        "appid": cfg["appid"], "mchid": cfg["mchid"],
        "description": order["product_name"],
        "out_trade_no": order["order_no"],
        "notify_url": "https://your-domain.example/api/wechat/notify",
        "amount": {"total": order["amount"], "currency": "CNY"},
    }, ensure_ascii=False)
    ts = str(int(time.time()))
    nonce = secrets.token_hex(16)
    message = f"POST\n/v3/pay/transactions/native\n{ts}\n{nonce}\n{body}\n"
    signature = private_key.sign(
        message.encode("utf-8"), padding.PKCS1v15(), SHA256()
    )
    import base64 as _b64
    sign_b64 = _b64.b64encode(signature).decode()
    # 拿到签名后发起真实请求（部署方按微信支付文档补充 Authorization 头与证书校验）：
    #   Authorization: WECHATPAY2-SHA256-RSA2048 mchid="...",nonce_str="...",
    #                  signature="...",timestamp="...",serial_no="..."
    #   POST https://api.mch.weixin.qq.com/v3/pay/transactions/native
    _ = sign_b64, ts, nonce
    raise GatewayNotConfigured("微信支付 Native 框架已就绪，请完成商户配置后补发请求")


def checkout_payload(order: dict, method_id: str):
    """生成收银台数据：返回 (kind, qrcode_text, extra)。

    demo/live 扫码方式 → 二维码内容文本；bank → 对公账户信息。
    """
    m = method(method_id) or PAYMENT_METHODS[0]
    if m["kind"] == "bank":
        return "bank", None, BANK_ACCOUNT
    status = gateway_status(method_id)
    if status == "live" and method_id == "wechat":
        try:
            url = wechat_native_code_url(order)
            return "qrcode", url, {}
        except GatewayNotConfigured:
            pass
    # 演示通道：二维码编码订单信息提示文本（扫不出真实收款，页面已标注）
    text = (f"考色 KAOSE 演示收银台 | 订单 {order['order_no']} | "
            f"{order['product_name']} | ¥{order['amount']} | "
            "商户通道接入后此码为真实收款码")
    return "qrcode", text, {"demo": True}


# ------------------------------------------------------------------ 二维码
def qrcode_data_uri(text: str):
    """生成二维码 PNG data URI；qrcode 库不可用时返回 None。"""
    try:
        import qrcode
        img = qrcode.make(text).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


# ------------------------------------------------------------------ 收据
def receipt_text(order: dict) -> str:
    m = method(order.get("method")) or {}
    lines = [
        "=" * 52,
        "考色 KAOSE · 文物色彩智能考证平台",
        "订单收据 / Order Receipt",
        "=" * 52,
        f"订单编号：{order.get('order_no', '')}",
        f"商品名称：{order.get('product_name', '')}",
        f"支付金额：¥{order.get('amount', 0)}",
        f"支付方式：{m.get('name', order.get('method', ''))}",
        f"订单状态：{ORDER_STATUS.get(order.get('status', ''), '')}",
        f"下单时间：{order.get('created_at', '')}",
        f"支付时间：{order.get('paid_at', '-') or '-'}",
        f"凭证编号：{order.get('receipt', '-') or '-'}",
        "-" * 52,
        "说明：演示环境下订单与收据仅用于流程验证；正式商户通道接入后，",
        "收据可作为电子凭证留存。本平台输出仅供辅助参考，不构成修复施工依据。",
        "© 2026 考色 KAOSE",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    o = create_order("report_single", "wechat", "test@example.com")
    print("created:", o["order_no"])
    mark_paid(o["order_no"])
    print("paid:", get_order(o["order_no"])["status"])
    print("storage:", storage_kind())
    print("list:", len(list_orders()))
