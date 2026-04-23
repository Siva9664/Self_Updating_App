# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['webview_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('api.py', '.'),
        ('updater.py', '.'),
        ('version.json', '.'),
        ('config.json', '.'),
        ('requirements.txt', '.'),
        ('app', 'app'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.responses',
        'requests',
        'webview',
        'api',
        'updater',
        'jinja2',
        'jinja2.ext',
        'starlette',
        'starlette.staticfiles',
        'starlette.responses',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=True,  # Keep True to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
