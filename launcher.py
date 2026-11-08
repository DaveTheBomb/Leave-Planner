"""
Launcher for the Leave Planner exe bundle.

Starts the Streamlit server in-process and opens the browser once ready.
No console window appears.
"""

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


PORT = 8501


def _find_free_port(default: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", default)) != 0:
            return default
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: int = 60) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                return True
        time.sleep(0.25)
    return False


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def _open_browser(port: int) -> None:
    if _wait_for_server(port):
        webbrowser.open(f"http://localhost:{port}")


def _patch_metadata() -> None:
    """
    Patch importlib.metadata so that packages can find their version strings
    inside a PyInstaller bundle where .dist-info folders are embedded in
    _MEIPASS rather than a real site-packages directory.
    """
    import importlib.metadata as _imeta

    # Map of package name -> version for every package that calls
    # importlib.metadata.version() at import time.
    _VERSIONS = {
        "streamlit":  "1.66.1",
        "holidays":   "0.107",
        "pandas":     "3.0.6",
        "altair":     "6.3.0",
        "pyarrow":    "26.0.0",
        "click":      "8.5.0",
        "packaging":  "26.3",
        "protobuf":   "7.36.2",
        "pydeck":     "0.9.3",
        "toml":       "0.10.2",
        "tornado":    "6.5.0",
        "watchdog":   "6.0.0",
    }

    _original_version = _imeta.version

    def _patched_version(package_name: str) -> str:
        key = package_name.lower().replace("-", "_")
        if key in _VERSIONS:
            return _VERSIONS[key]
        # Also check with original name
        if package_name.lower() in _VERSIONS:
            return _VERSIONS[package_name.lower()]
        return _original_version(package_name)

    _imeta.version = _patched_version

    # Also patch importlib.metadata.distribution for packages that call it
    _original_distribution = _imeta.distribution

    class _FakeDist:
        def __init__(self, name: str, ver: str):
            self.metadata = {"Name": name, "Version": ver}
            self._ver = ver

        @property
        def version(self):
            return self._ver

        def read_text(self, filename):
            return None

    def _patched_distribution(package_name: str):
        key = package_name.lower().replace("-", "_")
        ver = _VERSIONS.get(key) or _VERSIONS.get(package_name.lower())
        if ver:
            return _FakeDist(package_name, ver)
        return _original_distribution(package_name)

    _imeta.distribution = _patched_distribution


def main() -> None:
    base = _base_dir()
    app_path = str(base / "app.py")
    port = _find_free_port(PORT)

    # Patch metadata BEFORE importing streamlit
    if getattr(sys, "frozen", False):
        _patch_metadata()

    # Open browser in background once server is up
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()

    # Run Streamlit in-process
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        f"--server.port={port}",
        "--server.headless=true",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
    ]

    from streamlit.web import cli as st_cli
    sys.exit(st_cli.main())


if __name__ == "__main__":
    main()
