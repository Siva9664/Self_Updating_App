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
import threading
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
                return data.get("app", "0.0.0")
    except:
        pass
    return "0.0.0"

def get_latest_version():
    """Fetch latest version from GitHub API with SSL protection"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        # Use proper SSL verification for security
        ctx = ssl.create_default_context()
        
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

def validate_version(version):
    """Validate version string format (e.g., 1.0.0) for security"""
    import re
    if not version:
        return False
    # Only allow valid semver format: x.y.z
    pattern = r'^[0-9]+\.[0-9]+\.[0-9]+$'
    return bool(re.match(pattern, version))

def download_and_install(version):
    """Download app.zip and extract it with backup protection"""
    # Validate version before download
    if not validate_version(version):
        print(f"Error: Invalid version format: {version}")
        return False
    
    zip_path = LOCAL_DIR / "app.zip"
    backup_dir = LOCAL_DIR / "app_backup"
    
    try:
        print(f"Downloading version {version}...")
        
        # Download URL
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{version}/app.zip"
        
        # Use proper SSL verification
        ctx = ssl.create_default_context()
        
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
        
        print("\nValidating download...")
        # Validate zip file
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Downloaded file is not a valid zip file")
        
        # Create backup of existing app
        if APP_DIR.exists():
            print("Creating backup...")
            if backup_dir.exists():
                import shutil
                shutil.rmtree(backup_dir)
            import shutil
            shutil.copytree(APP_DIR, backup_dir)
        
        print("Extracting files...")
        
        # Remove old app
        if APP_DIR.exists():
            import shutil
            shutil.rmtree(APP_DIR)
        
        APP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(APP_DIR)
        
        # Clean up zip
        zip_path.unlink()
        
        # Clean up backup on success
        if backup_dir.exists():
            import shutil
            shutil.rmtree(backup_dir)
        
        # Save version
        with open(VERSION_FILE, 'w') as f:
            json.dump({"app": version}, f)
        
        print("Installation complete!")
        return True
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        if zip_path.exists():
            zip_path.unlink()
        # Restore from backup on failure
        if backup_dir.exists():
            print("Restoring from backup...")
            if APP_DIR.exists():
                import shutil
                shutil.rmtree(APP_DIR)
            import shutil
            shutil.copytree(backup_dir, APP_DIR)
            shutil.rmtree(backup_dir)
            print("Restored previous version.")
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
    """Run the main application in a desktop window"""
    print("\nStarting application...")
    print("=" * 50)
    
    try:
        # Change to app directory
        os.chdir(APP_DIR)
        
        # Add local packages and app to path
        local_packages = APP_DIR / "local_packages"
        if local_packages.exists():
            sys.path.insert(0, str(local_packages))
        sys.path.insert(0, str(APP_DIR))
        
        # Now import dependencies
        import fastapi
        import uvicorn
        import webview
        
        # Import app
        from api import app
        
        # Start server in background thread
        server_url = "http://127.0.0.1:8000"
        
        def start_server():
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning", access_log=False)
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        print("Waiting for server to start...")
        
        # Wait for server to be ready
        if wait_for_server(server_url):
            print("Server ready!")
            print("Opening application window...")
            print("=" * 50)
            
            # Create desktop window with the app
            window = webview.create_window(
                'Self-Updating App',
                server_url,
                width=1200,
                height=800,
                min_size=(800, 600)
            )
            
            # Start the webview (this blocks until window is closed)
            webview.start()
            
        else:
            print("Error: Server failed to start")
            print("Please check that the app was downloaded correctly.")
            input("\nPress Enter to exit...")
            
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nDependencies should be bundled with the app.")
        print("Try deleting the app folder and restarting:")
        print(f"  {APP_DIR}")
        input("\nPress Enter to exit...")
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
