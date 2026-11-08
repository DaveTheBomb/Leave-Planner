"""
Launcher for the Leave Planner exe bundle.

Starts the Streamlit server in a background thread (in-process) and opens
the browser once the server is ready. No console window appears.
"""

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


PORT = 8501


def _find_free_port(default: int) -> int:
    """Return default if free, otherwise find a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", default)) != 0:
            return default
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: int = 60) -> bool:
    """Block until the server accepts connections or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                return True
        time.sleep(0.25)
    return False


def _base_dir() -> Path:
    """Return the directory containing app.py.

    PyInstaller extracts bundled files to sys._MEIPASS at runtime.
    When running from source it is the directory of this file.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def _open_browser(port: int) -> None:
    """Wait for the server then open the browser."""
    if _wait_for_server(port):
        webbrowser.open(f"http://localhost:{port}")


def main() -> None:
    base = _base_dir()
    app_path = str(base / "app.py")
    port = _find_free_port(PORT)

    # Open browser in a background thread once the server is up
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()

    # Run Streamlit in-process using its internal CLI bootstrap.
    # This is the same code path as `streamlit run app.py`.
    from streamlit.web import cli as st_cli
    from click.testing import CliRunner

    # Build the argv that streamlit's CLI expects
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        f"--server.port={port}",
        "--server.headless=true",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
    ]

    sys.exit(st_cli.main())


if __name__ == "__main__":
    main()
