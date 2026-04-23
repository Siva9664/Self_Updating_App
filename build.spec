# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for SelfUpdatingApp
# Uses only standard library - minimal dependencies

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'ssl', 'urllib', 'json', 'zipfile', 'subprocess', 'pathlib', 'threading',
        'webview', 'uvicorn', 'fastapi', 'starlette', 'pydantic', 'anyio', 'sniffio',
        'click', 'h11', 'certifi', 'idna', 'charset_normalizer', 'urllib3',
        'typing', 'math', 'random', 'uuid', 'datetime'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy', 'pandas', 'matplotlib', 'PIL', 'tkinter', 
        'PyQt5', 'PyQt6', 'wx', 'PySide2', 'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SelfUpdatingApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
