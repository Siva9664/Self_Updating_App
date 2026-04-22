#!/usr/bin/env python3
"""
Self-Updating Webview App Loader
Downloads and runs the latest app version from GitHub releases
"""

import os
import sys
import json
import zipfile
import requests
import threading
import time
import shutil
from pathlib import Path

# PyWebView for desktop window
import webview

# App configuration
APP_NAME = "SelfUpdatingApp"
GITHUB_REPO = "Siva9664/Self_Updating_App"
LOCAL_APP_DIR = Path.home() / "AppData" / "Local" / APP_NAME
VERSION_FILE = LOCAL_APP_DIR / "version.json"
APP_ZIP_URL = f"https://github.com/{GITHUB_REPO}/releases/download/{{version}}/app.zip"
API_VERSION_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def get_local_version():
    """Get locally installed app version"""
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE) as f:
                data = json.load(f)
                return data.get("app", "0.0.0")
        except:
            return "0.0.0"
    return "0.0.0"

def get_remote_version():
    """Get latest version from GitHub releases"""
    try:
        response = requests.get(API_VERSION_URL, timeout=10)
        response.raise_for_status()
        release = response.json()
        version = release.get("tag_name", "1.0.0")
        if version.startswith('v'):
            version = version[1:]
        return version
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None

def compare_versions(local, remote):
    """Check if remote version is newer"""
    try:
        local_parts = [int(x) for x in local.split('.')]
        remote_parts = [int(x) for x in remote.split('.')]
        return remote_parts > local_parts
    except:
        return False

def download_and_extract(version, window):
    """Download and extract the app"""
    try:
        window.evaluate_js(f'document.getElementById("status").innerText = "Downloading version {version}..."')
        
        url = APP_ZIP_URL.format(version=version)
        zip_path = LOCAL_APP_DIR / "app.zip"
        
        # Download
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        window.evaluate_js(f'document.getElementById("progress").style.width = "{percent}%"')
        
        window.evaluate_js('document.getElementById("status").innerText = "Extracting..."')
        
        # Extract
        app_code_dir = LOCAL_APP_DIR / "app_code"
        if app_code_dir.exists():
            shutil.rmtree(app_code_dir)
        app_code_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(app_code_dir)
        
        # Cleanup
        zip_path.unlink()
        
        # Save version
        with open(VERSION_FILE, 'w') as f:
            json.dump({"app": version}, f)
        
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def run_app():
    """Run the downloaded FastAPI app"""
    app_code_dir = LOCAL_APP_DIR / "app_code"
    
    # Add app_code to path
    sys.path.insert(0, str(app_code_dir))
    
    # Import and run
    from api import app
    import uvicorn
    
    # Start server in thread
    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    return "http://127.0.0.1:8000"

def create_loading_html():
    """Create loading screen HTML"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 { margin-bottom: 20px; }
        .progress-bar {
            width: 300px;
            height: 20px;
            background: rgba(255,255,255,0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress {
            height: 100%;
            background: white;
            width: 0%;
            transition: width 0.3s;
        }
        #status { margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Self-Updating App</h1>
        <div class="progress-bar">
            <div id="progress" class="progress"></div>
        </div>
        <div id="status">Checking for updates...</div>
    </div>
</body>
</html>
    """
    return html

def main():
    """Main entry point"""
    # Ensure local app directory exists
    LOCAL_APP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if we should show loading window
    needs_update = False
    local_ver = get_local_version()
    remote_ver = get_remote_version()
    
    if remote_ver and compare_versions(local_ver, remote_ver):
        needs_update = True
    
    if needs_update or not (LOCAL_APP_DIR / "app_code").exists():
        # Show loading window
        loading_html = create_loading_html()
        
        window = webview.create_window(
            'Updating...',
            html=loading_html,
            width=400,
            height=300,
            resizable=False
        )
        
        def update_and_run():
            if remote_ver:
                success = download_and_extract(remote_ver, window)
                if success:
                    window.destroy()
                    run_main_app()
                else:
                    window.evaluate_js('document.getElementById("status").innerText = "Update failed. Using local version..."')
                    time.sleep(2)
                    window.destroy()
                    run_main_app()
            else:
                window.evaluate_js('document.getElementById("status").innerText = "No internet. Using local version..."')
                time.sleep(2)
                window.destroy()
                run_main_app()
        
        webview.start(update_and_run, window)
    else:
        run_main_app()

def run_main_app():
    """Run the main application"""
    if not (LOCAL_APP_DIR / "app_code").exists():
        print("No app code found. Please connect to internet.")
        sys.exit(1)
    
    # Start the server
    url = run_app()
    
    # Create main window
    webview.create_window(
        'Self-Updating App',
        url,
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    
    webview.start()

if __name__ == '__main__':
    main()
