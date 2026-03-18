from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
from updater import check_updates, update_modules, get_local_versions

app = FastAPI()

# Serve static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Load configuration
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "auto_update": {
                "enabled": True,
                "check_interval_minutes": 5,
                "auto_install": True,
                "show_notification": True
            }
        }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.get("/")
def home():
    return FileResponse("app/templates/index.html", media_type="text/html")

@app.get("/version")
def get_version():
    """Get current local app version"""
    versions = get_local_versions()
    return {
        "current_version": versions.get("module1", "1.0"),
        "all_versions": versions
    }

@app.get("/check")
def check():
    return check_updates()

@app.get("/update")
def update():
    return update_modules()

@app.get("/settings")
def get_settings():
    config = load_config()
    return {
        "auto_update": config.get("auto_update", {})
    }

@app.post("/settings")
def update_settings(settings: dict):
    config = load_config()
    if "auto_update" in settings:
        config["auto_update"] = settings["auto_update"]
    save_config(config)
    return {"status": "Settings updated", "settings": config}
