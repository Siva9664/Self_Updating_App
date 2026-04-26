import os
import sys
import time
import json
import threading
import subprocess
import urllib.request
import ssl
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import webview

APP_NAME = "SelfUpdatingApp"
GITHUB_USER = "Siva9664"
GITHUB_REPO = "Self_Updating_App"
CURRENT_VERSION = "1.0.0"

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Updating App</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1e1e2f, #2a2a40);
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        .container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 400px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        h1 {
            margin-top: 0;
            font-size: 28px;
            background: -webkit-linear-gradient(45deg, #ff6b6b, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        p {
            color: #b0b0c0;
            font-size: 16px;
        }

        .version-badge {
            display: inline-block;
            background: #4facfe;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .status {
            margin-top: 30px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(0,0,0,0.2);
            font-size: 14px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        button {
            margin-top: 20px;
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-size: 14px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Self-Updating App</h1>
        <div class="version-badge">Version {CURRENT_VERSION}</div>
        <p>This is a modern, single-file application that updates itself automatically from GitHub Releases.</p>
        
        <div class="status" id="status-box">
            System running smoothly.
        </div>
        
        <button onclick="checkUpdate()">Check for Updates</button>
    </div>

    <script>
        async function checkUpdate() {
            const statusBox = document.getElementById('status-box');
            statusBox.innerHTML = '<div class="loading"></div><br><br>Checking for updates...';
            
            try {
                const response = await fetch('/api/check-update');
                const data = await response.json();
                
                if(data.update_available) {
                    statusBox.innerHTML = `Update found: v${data.latest_version}<br>Downloading and installing...`;
                    fetch('/api/trigger-update'); 
                } else {
                    statusBox.innerHTML = `You are on the latest version!`;
                    setTimeout(() => {
                        statusBox.innerHTML = 'System running smoothly.';
                    }, 3000);
                }
            } catch (err) {
                statusBox.innerHTML = 'Error checking for updates.';
            }
        }
        
        setTimeout(checkUpdate, 2000);
    </script>
</body>
</html>
"""

@app.get("/")
def home():
    return HTMLResponse(HTML_CONTENT.replace("{CURRENT_VERSION}", CURRENT_VERSION))

def get_latest_release():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            tag = data.get("tag_name", CURRENT_VERSION)
            if tag.startswith('v'):
                tag = tag[1:]
            
            assets = data.get("assets", [])
            download_url = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    break
                    
            return tag, download_url
    except Exception as e:
        print(f"Error fetching release: {e}")
        return None, None

@app.get("/api/check-update")
def check_update_api():
    latest_version, download_url = get_latest_release()
    if latest_version and latest_version != CURRENT_VERSION and download_url:
        return {"update_available": True, "latest_version": latest_version}
    return {"update_available": False}

@app.get("/api/trigger-update")
def trigger_update_api():
    threading.Thread(target=perform_update).start()
    return {"status": "started"}

def perform_update():
    latest_version, download_url = get_latest_release()
    if not download_url:
        return
        
    print(f"Downloading update from {download_url}...")
    
    current_exe = sys.executable
    if not getattr(sys, 'frozen', False):
        print("Running from script. Update only supported when compiled to .exe")
        return

    exe_dir = os.path.dirname(current_exe)
    new_exe_path = os.path.join(exe_dir, "SelfUpdatingApp_New.exe")
    
    ctx = ssl.create_default_context()
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response, open(new_exe_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            
        print("Download complete. Generating update script...")
        
        bat_path = os.path.join(exe_dir, "update.bat")
        current_exe_name = os.path.basename(current_exe)
        
        bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
del "{current_exe_name}"
ren "SelfUpdatingApp_New.exe" "{current_exe_name}"
start "" "{current_exe_name}"
del "%~f0"
"""
        with open(bat_path, "w") as f:
            f.write(bat_content)
            
        print("Restarting application...")
        subprocess.Popen([bat_path], cwd=exe_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        os._exit(0)
        
    except Exception as e:
        print(f"Update failed: {e}")
        if os.path.exists(new_exe_path):
            os.remove(new_exe_path)

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    webview.create_window(
        title="Self-Updating App",
        url="http://127.0.0.1:8000",
        width=1000,
        height=700,
        min_size=(800, 600)
    )
    
    webview.start()
