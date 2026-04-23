#!/usr/bin/env python3
"""Test if all imports work before building EXE"""

import sys
import traceback

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False

modules = [
    'fastapi',
    'fastapi.staticfiles',
    'fastapi.responses',
    'uvicorn',
    'requests',
    'webview',
    'jinja2',
    'api',
    'updater',
]

print("Testing all imports...\n")
all_ok = True
for mod in modules:
    if not test_import(mod):
        all_ok = False

print("\n" + "="*40)
if all_ok:
    print("All imports OK - ready to build EXE")
else:
    print("Some imports failed - fix before building")
    sys.exit(1)
