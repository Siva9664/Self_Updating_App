#!/usr/bin/env python3
"""
Layer 1: Simple App Loader
Downloads app from GitHub if needed, then runs it
"""

import os
import sys
import json
import zipfile
import urllib.request
from pathlib import Path

# Config
APP_NAME = "SelfUpdatingApp"
GITHUB_USER = "Siva9664"
GITHUB_REPO = "Self_Updating_App"
LOCAL_DIR = Path.home() / "AppData" / "Local" / APP_NAME
VERSION_FILE = LOCAL_DIR / "version.json"
APP_DIR = LOCAL_DIR / "app"

def get_local_version():
    """Get installed version"""
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE) as f:
                return json.load(f).get("version", "0.0.0")
        except:
            pass
    return "0.0.0"

def get_remote_version():
    """Get latest version from GitHub"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            version = data.get("tag_name", "1.0.0")
            return version[1:] if version.startswith('v') else version
    except Exception as e:
        print(f"Could not check for updates: {e}")
        return None

def download_app(version):
    """Download and extract app"""
    print(f"Downloading version {version}...")
    
    try:
        # Download
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{version}/app.zip"
        zip_path = LOCAL_DIR / "app.zip"
        
        urllib.request.urlretrieve(url, zip_path)
        
        # Extract
        print("Extracting...")
        if APP_DIR.exists():
            import shutil
            shutil.rmtree(APP_DIR)
        APP_DIR.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(APP_DIR)
        
        zip_path.unlink()
        
        # Save version
        with open(VERSION_FILE, 'w') as f:
            json.dump({"version": version}, f)
        
        print("Download complete!")
        return True
        
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def run_app():
    """Run the main application"""
    # Add app to path
    sys.path.insert(0, str(APP_DIR))
    
    # Change to app directory
    os.chdir(APP_DIR)
    
    # Run the app
    try:
        import subprocess
        subprocess.run([sys.executable, "-c", "
import sys
sys.path.insert(0, '.')
from api import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000)
"], check=True)
    except Exception as e:
        print(f"Error running app: {e}")
        input("Press Enter to exit...")

def main():
    """Main entry point"""
    print("=" * 50)
    print("Self-Updating App Loader")
    print("=" * 50)
    
    # Ensure directory exists
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check versions
    local_ver = get_local_version()
    remote_ver = get_remote_version()
    
    print(f"Local version: {local_ver}")
    if remote_ver:
        print(f"Remote version: {remote_ver}")
    
    # Decide if we need to download
    needs_download = not APP_DIR.exists()
    
    if remote_ver and remote_ver != local_ver:
        print(f"Update available: {local_ver} → {remote_ver}")
        needs_download = True
    
    # Download if needed
    if needs_download:
        if remote_ver:
            if not download_app(remote_ver):
                if not APP_DIR.exists():
                    print("Failed to download and no local version found.")
                    print("Please check your internet connection.")
                    input("Press Enter to exit...")
                    return
                print("Using existing local version.")
        else:
            if not APP_DIR.exists():
                print("No internet and no local app found.")
                input("Press Enter to exit...")
                return
            print("No internet - using local version.")
    else:
        print("App is up to date!")
    
    # Run the app
    print("\nStarting application...")
    run_app()

if __name__ == "__main__":
    main()
