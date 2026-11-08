# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Leave Planner — folder-based distribution (onedir).

Build command:
    .venv\Scripts\pyinstaller.exe leave_planner.spec
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(SPECPATH)

# ── Data files ────────────────────────────────────────────────────────────────
# Streamlit ships static web assets and its own config that must travel
# alongside the binary.
datas = []
datas += collect_data_files("streamlit")
datas += collect_data_files("holidays")
datas += collect_data_files("altair")
datas += collect_data_files("pyarrow")

# Package metadata (.dist-info) required by importlib.metadata at runtime.
# Without these, streamlit/__init__.py raises PackageNotFoundError on startup.
import site
site_packages = Path(site.getsitepackages()[0])
for pkg in ("streamlit-1.66.1", "holidays-0.107", "pandas-3.0.6",
            "altair-6.3.0", "pyarrow-26.0.0"):
    dist_info = site_packages / f"{pkg}.dist-info"
    if dist_info.exists():
        datas.append((str(dist_info), f"{pkg}.dist-info"))

# Bundle the app source files so launcher.py can locate them at runtime
datas += [
    (str(ROOT / "app.py"),           "."),
    (str(ROOT / "leave-planner.py"), "."),
    (str(ROOT / "version.py"),       "."),
]

# ── Hidden imports ────────────────────────────────────────────────────────────
# Streamlit and its dependencies use dynamic imports that PyInstaller
# cannot detect statically.
hiddenimports = []
hiddenimports += collect_submodules("streamlit")
hiddenimports += collect_submodules("holidays")
hiddenimports += [
    "pandas",
    "pyarrow",
    "altair",
    "importlib.util",
    "importlib.metadata",
    "pkg_resources",
    "charset_normalizer",
    "uvicorn",
    "uvicorn.lifespan.on",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "starlette",
    "click",
    "click.testing",
    "streamlit.web.cli",
    "streamlit.web.bootstrap",
]

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "scipy", "IPython", "notebook"],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── Executable ────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,       # folder mode — binaries go into COLLECT
    name="LeavePlanner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               # no console window — browser only
    icon=None,                   # add an .ico file path here if you have one
)

# ── Folder bundle ─────────────────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LeavePlanner",         # output folder: dist/LeavePlanner/
)
