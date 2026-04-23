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
        'ssl', 'urllib', 'json', 'zipfile', 'subprocess', 'pathlib', 'threading', 'webview',
        'uvicorn', 'uvicorn.config', 'uvicorn.main', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.websockets',
        'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.logging',
        'fastapi', 'fastapi.routing', 'fastapi.middleware', 'fastapi.middleware.cors', 'fastapi.middleware.httpsredirect',
        'fastapi.openapi', 'fastapi.openapi.docs', 'fastapi.openapi.models', 'fastapi.openapi.utils',
        'fastapi.params', 'fastapi.requests', 'fastapi.responses', 'fastapi.staticfiles', 'fastapi.templating',
        'fastapi.utils', 'fastapi.websockets', 'fastapi.dependencies', 'fastapi.dependencies.utils',
        'starlette', 'starlette.applications', 'starlette.requests', 'starlette.responses', 'starlette.routing',
        'starlette.middleware', 'starlette.middleware.base', 'starlette.middleware.errors',
        'starlette.templating', 'starlette.staticfiles', 'starlette.websockets', 'starlette.datastructures',
        'pydantic', 'pydantic.fields', 'pydantic.main', 'pydantic.models', 'pydantic.types', 'pydantic.schema',
        'pydantic.json', 'pydantic.typing', 'pydantic.utils', 'pydantic.validators',
        'anyio', 'anyio._core', 'anyio.abc', 'anyio.streams', 'anyio.streams.memory', 'anyio.streams.tls',
        'sniffio', 'click', 'h11', 'h11._connection', 'h11._events', 'h11._headers', 'h11._readers', 'h11._writers',
        'certifi', 'idna', 'charset_normalizer', 'urllib3', 'urllib3.util', 'urllib3.connection', 'urllib3.response',
        'typing', 'math', 'random', 'uuid', 'datetime', 'logging', 'warnings', 'traceback', 'inspect'
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
