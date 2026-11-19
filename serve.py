"""Sites 部署启动器：从 PORT 环境变量取端口并拉起 Streamlit。

部署沙箱通过 PORT 注入唯一对外端口，但执行 startCmd 时不经过 shell，
所以 "$PORT" 不会被展开成实际端口。这里改用 Python 直接读环境变量，
彻底绕开 shell 变量展开的差异；本地与云端行为一致。
"""
import os
import subprocess
import sys


def main() -> int:
    port = str(os.environ.get("PORT") or "3000")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        # 让 /app/static/* 可访问：PWA 的 manifest / service worker / 图标都从这里加载
        "--server.enableStaticServing", "true",
        "--browser.gatherUsageStats", "false",
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    return subprocess.call(cmd, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
