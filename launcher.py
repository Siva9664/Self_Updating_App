#!/usr/bin/env python3
"""
Self-Updating App Launcher
Uses only standard library - no external dependencies
"""

import os
import sys
import json
import zipfile
import urllib.request
import ssl
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "SelfUpdatingApp"
GITHUB_USER = "Siva9664"
GITHUB_REPO = "Self_Updating_App"
LOCAL_DIR = Path.home() / "AppData" / "Local" / APP_NAME
VERSION_FILE = LOCAL_DIR / "version.json"
APP_DIR = LOCAL_DIR / "app"

def get_installed_version():
    """Read installed version from file"""
    try:
        if VERSION_FILE.exists():
            with open(VERSION_FILE, 'r') as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
    except:
        pass
    return "0.0.0"

def get_latest_version():
    """Fetch latest version from GitHub API"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        # Create SSL context that works on all systems
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            tag = data.get("tag_name", "1.0.0")
            # Remove 'v' prefix if present
            return tag[1:] if tag.startswith('v') else tag
    except Exception as e:
        print(f"Warning: Could not check for updates ({e})")
        return None

def download_and_install(version):
    """Download app.zip and extract it"""
    zip_path = LOCAL_DIR / "app.zip"
    
    try:
        print(f"Downloading version {version}...")
        
        # Download URL
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{version}/app.zip"
        
        # Create SSL context
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Download with progress
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(zip_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}%", end='\r')
        
        print("\nExtracting files...")
        
        # Remove old app if exists
        if APP_DIR.exists():
            import shutil
            shutil.rmtree(APP_DIR)
        
        APP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(APP_DIR)
        
        # Clean up zip
        zip_path.unlink()
        
        # Save version
        with open(VERSION_FILE, 'w') as f:
            json.dump({"version": version}, f)
        
        print("Installation complete!")
        return True
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False

def wait_for_server(url, max_retries=30):
    """Wait for server to be ready"""
    import time
    for i in range(max_retries):
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    return True
        except:
            time.sleep(0.5)
    return False

def run_application():
    """Run the main application server"""
    print("\nStarting application server...")
    print("=" * 50)
    
    try:
        # Change to app directory
        os.chdir(APP_DIR)
        
        # Create startup script (quiet mode)
        startup_script = """
import sys
import warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')
from api import app
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning", access_log=False)
"""
        
        # Platform-specific startup info to hide window
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
        
        # Run the server (hidden, no console window)
        process = subprocess.Popen(
            [sys.executable, '-c', startup_script],
            cwd=str(APP_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        print("Waiting for server to start...")
        
        # Wait for server to be ready
        server_url = "http://127.0.0.1:8000"
        if wait_for_server(server_url):
            print(f"Server ready!")
            
            # Open browser automatically
            import webbrowser
            print(f"Opening browser: {server_url}")
            webbrowser.open(server_url)
            
            print("=" * 50)
            print("App is running in your browser!")
            print("Close this window to stop the server")
            print("=" * 50)
        else:
            print("Warning: Server may not have started properly")
        
        # Keep launcher running to monitor server
        try:
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    print("Server stopped unexpectedly")
                    break
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            process.terminate()
            
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

def main():
    """Main entry point"""
    print("=" * 50)
    print("Self-Updating Application")
    print("=" * 50)
    
    # Ensure local directory exists
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get versions
    installed_version = get_installed_version()
    latest_version = get_latest_version()
    
    print(f"Installed: v{installed_version}")
    
    # Determine if we need to download
    need_download = False
    
    if latest_version:
        print(f"Latest: v{latest_version}")
        if latest_version != installed_version:
            print(f"Update available: v{installed_version} -> v{latest_version}")
            need_download = True
        else:
            print("You have the latest version!")
    else:
        print("Could not check for updates (no internet)")
        if not APP_DIR.exists():
            print("ERROR: No local app found and no internet connection!")
            print("Please connect to the internet and try again.")
            input("\nPress Enter to exit...")
            return
    
    # Check if app exists
    if not APP_DIR.exists() or not any(APP_DIR.iterdir()):
        print("App not found locally.")
        need_download = True
    
    # Download if needed
    if need_download:
        if not latest_version:
            print("Cannot download - no internet connection.")
            if APP_DIR.exists():
                print("Using existing local version...")
            else:
                print("No app available. Exiting.")
                input("\nPress Enter to exit...")
                return
        else:
            if not download_and_install(latest_version):
                if APP_DIR.exists():
                    print("Using existing version...")
                else:
                    print("Failed to download and no local version available.")
                    input("\nPress Enter to exit...")
                    return
    
    # Run the app
    run_application()

if __name__ == "__main__":
    main()
