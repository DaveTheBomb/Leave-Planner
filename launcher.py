"""
Launcher for the Leave Planner exe bundle.

Starts the Streamlit server in a background thread and opens the browser
once the server is ready. No console window is shown when built with
PyInstaller (--noconsole / windowed mode).
"""

import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path


PORT = 8501
URL = f"http://localhost:{PORT}"


def _find_free_port(default: int) -> int:
    """Return default if free, otherwise find the next available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", default)) != 0:
            return default
    # Default is taken — find a free one
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: int = 30) -> bool:
    """Block until the server accepts connections or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                return True
        time.sleep(0.2)
    return False


def _base_dir() -> Path:
    """Return the directory that contains app.py and leave-planner.py.

    When frozen by PyInstaller the bundle is extracted to sys._MEIPASS.
    When running from source it is the directory of this file.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def main() -> None:
    base = _base_dir()
    app_path = base / "app.py"

    port = _find_free_port(PORT)
    url = f"http://localhost:{port}"

    # Locate the streamlit executable bundled alongside the .exe
    if getattr(sys, "frozen", False):
        streamlit_exe = Path(sys.executable).parent / "streamlit.exe"
        cmd = [str(streamlit_exe), "run", str(app_path),
               "--server.port", str(port),
               "--server.headless", "true",
               "--global.developmentMode", "false"]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path),
               "--server.port", str(port),
               "--server.headless", "true"]

    # Start Streamlit in the background (no console window)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    # Open browser once the server is up
    def _open_browser():
        if _wait_for_server(port):
            webbrowser.open(url)

    threading.Thread(target=_open_browser, daemon=True).start()

    # Keep the launcher alive until the server exits
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
