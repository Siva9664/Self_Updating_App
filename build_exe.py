#!/usr/bin/env python3
"""
Build script for creating a single executable of the Self-Updating App
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the single executable using PyInstaller"""
    print("Building SelfUpdatingApp.exe...")

    # PyInstaller command with optimized options
    cmd = [
        r"C:\Users\sivar\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (app has its own window)
        "--name=SelfUpdatingApp",      # Output name
        "--clean",                      # Clean cache before building
        "--noconfirm",                  # Don't ask for confirmation
        "launcher.py"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print("Executable created: dist/SelfUpdatingApp.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("launcher.py").exists():
        print("Error: launcher.py not found in current directory")
        sys.exit(1)

    # Build the executable
    if build_executable():
        print("\nTo test the executable:")
        print("  cd dist")
        print("  ./SelfUpdatingApp.exe")
    else:
        sys.exit(1)
