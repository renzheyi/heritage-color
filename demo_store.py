"""预约商业演示需求的本地持久化（应用服务器内）。

三层兜底：SQLite → JSON 文件 → 进程内存，与 payments.py 同款策略，
保证任何只读/受限环境下提交都不会静默丢失或让页面报错。

注意：Sites 沙箱没有持久卷，重新发布应用会清空 data/ 下的历史记录，
因此站内在「需求记录」页提供 CSV 导出，请及时留存。
"""
import csv
import io
import json
import os
import secrets
import sqlite3
import threading
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "demo_requests.db")
JSON_PATH = os.path.join(DATA_DIR, "demo_requests.json")

_LOCK = threading.Lock()
_MEMORY = {}
_SQLITE_OK = None

_FIELDS = ("id", "org", "contact_person", "contact_method",
           "org_type", "directions", "message", "created_at")


def _load_json() -> dict:
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(store: dict) -> bool:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


def _conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS demo_requests (
            id TEXT PRIMARY KEY, org TEXT, contact_person TEXT,
            contact_method TEXT, org_type TEXT, directions TEXT,
            message TEXT, created_at TEXT)"""
    )
    conn.commit()
    return conn


def _store_kind() -> str:
    global _SQLITE_OK
    if _SQLITE_OK is None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            _conn().close()
            _SQLITE_OK = True
        except Exception:
            _SQLITE_OK = False
    return "sqlite" if _SQLITE_OK else "json"


def save_request(rec: dict) -> dict:
    """写入一条预约，返回带编号的完整记录。"""
    row = {
        "id": "KR" + datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(2).upper(),
        "org": rec.get("机构", ""),
        "contact_person": rec.get("联系人", ""),
        "contact_method": rec.get("联系方式", ""),
        "org_type": rec.get("机构类型", ""),
        "directions": rec.get("关注方向", ""),
        "message": rec.get("需求描述", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with _LOCK:
        if _store_kind() == "sqlite":
            try:
                conn = _conn()
                conn.execute(
                    "INSERT INTO demo_requests VALUES (?,?,?,?,?,?,?,?)",
                    tuple(row[k] for k in _FIELDS))
                conn.commit()
                conn.close()
                return row
            except Exception:
                pass
        store = _load_json()
        store[row["id"]] = row
        if not _save_json(store):
            _MEMORY[row["id"]] = row
    return row


def list_requests(limit: int = 50):
    with _LOCK:
        rows = []
        if _store_kind() == "sqlite":
            try:
                conn = _conn()
                got = conn.execute(
                    "SELECT * FROM demo_requests ORDER BY created_at DESC LIMIT ?",
                    (limit,)).fetchall()
                conn.close()
                rows = [dict(zip(_FIELDS, r)) for r in got]
            except Exception:
                rows = []
        if not rows:
            rows = list(_load_json().values()) + list(_MEMORY.values())
            rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
            rows = rows[:limit]
        return rows


def storage_kind() -> str:
    return {"sqlite": "本地 SQLite 需求库", "json": "本地 JSON 文件"}[_store_kind()]


def csv_bytes() -> bytes:
    """导出全部预约记录为 UTF-8 BOM 的 CSV（Excel 可直接打开）。"""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["需求编号", "机构 / 单位", "联系人", "联系方式",
                "机构类型", "关注方向", "需求描述", "提交时间"])
    for r in list_requests(1000):
        w.writerow([r.get(k, "") for k in
                    ("id", "org", "contact_person", "contact_method",
                     "org_type", "directions", "message", "created_at")])
    return buf.getvalue().encode("utf-8-sig")
