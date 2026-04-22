import requests
import json
import os
import zipfile
import logging
from datetime import datetime
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REMOTE_VERSION_URL = "https://api.github.com/repos/Siva9664/Self_Updating_App/releases/latest"
REMOTE_BASE_URL = "https://github.com/Siva9664/Self_Updating_App/releases/download/"

LOCAL_VERSION_FILE = "version.json"
MODULES_DIR = "app/modules"

# Ensure modules directory exists
os.makedirs(MODULES_DIR, exist_ok=True)


def get_local_versions() -> Dict[str, str]:
    """Get locally installed module versions."""
    if not os.path.exists(LOCAL_VERSION_FILE):
        logger.info("No local version file found, creating new one")
        return {}
    
    try:
        with open(LOCAL_VERSION_FILE) as f:
            versions = json.load(f)
            logger.info(f"Loaded local versions: {versions}")
            return versions
    except json.JSONDecodeError:
        logger.error("Local version file is corrupted")
        return {}
    except Exception as e:
        logger.error(f"Error reading local version file: {e}")
        return {}


def get_remote_versions() -> Dict[str, str]:
    """Get available app version from GitHub releases."""
    try:
        logger.info(f"Fetching remote versions from {REMOTE_VERSION_URL}")
        response = requests.get(REMOTE_VERSION_URL, timeout=5)
        response.raise_for_status()
        release = response.json()
        version = release.get("tag_name", "1.0.0")
        if version.startswith('v'):
            version = version[1:]
        logger.info(f"Remote app version: {version}")
        return {"app": version}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: Cannot reach update server at {REMOTE_VERSION_URL}")
        return {}
    except requests.exceptions.Timeout:
        logger.error("Request timeout: Update server took too long to respond")
        return {}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        return {}
    except json.JSONDecodeError:
        logger.error("Remote response is not valid JSON")
        return {}
    except Exception as e:
        logger.error(f"Error fetching remote versions: {e}")
        return {}


def compare_versions(local_version: str, remote_version: str) -> bool:
    """Check if remote version is newer than local version."""
    try:
        local_parts = [int(x) for x in local_version.split('.')]
        remote_parts = [int(x) for x in remote_version.split('.')]
        
        # Pad with zeros if lengths differ
        max_len = max(len(local_parts), len(remote_parts))
        local_parts.extend([0] * (max_len - len(local_parts)))
        remote_parts.extend([0] * (max_len - len(remote_parts)))
        
        return remote_parts > local_parts
    except (ValueError, AttributeError):
        logger.warning(f"Version comparison failed for {local_version} vs {remote_version}")
        return True  # Consider it an update if comparison fails


def check_updates() -> Dict:
    """Check for available updates."""
    logger.info("Starting update check...")
    
    local = get_local_versions()
    remote = get_remote_versions()
    
    if not remote:
        logger.warning("Could not reach update server")
        return {
            "updates_available": False,
            "available_modules": [],
            "current_version": local.get("module1", "Unknown"),
            "error": "Update server unavailable"
        }
    
    updates = {}
    for module in remote:
        local_ver = local.get(module, "0")
        remote_ver = remote[module]
        
        if compare_versions(local_ver, remote_ver):
            updates[module] = remote_ver
            logger.info(f"Update available for {module}: {local_ver} -> {remote_ver}")
    
    result = {
        "updates_available": len(updates) > 0,
        "available_modules": list(updates.keys()),
        "current_version": local.get("module1", "Unknown")
    }
    
    logger.info(f"Check complete. Updates available: {len(updates)}")
    return result


def download_module(module: str) -> Tuple[bool, str]:
    """Download and extract a module. Returns (success, message)."""
    try:
        logger.info(f"Downloading module: {module}")
        
        # Try downloading as zip first
        url = f"{REMOTE_BASE_URL}/{module}.zip"
        logger.info(f"Attempting to download from {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        zip_path = f"{module}.zip"
        
        # Save zip file
        with open(zip_path, "wb") as f:
            f.write(response.content)
        logger.info(f"Downloaded {module}: {len(response.content)} bytes")
        
        # Extract module
        extract_path = os.path.join(MODULES_DIR, module)
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        logger.info(f"Extracted {module} to {extract_path}")
        
        # Clean up zip
        os.remove(zip_path)
        
        return True, f"Successfully downloaded and extracted {module}"
        
    except requests.exceptions.ConnectionError:
        msg = f"Connection error: Cannot reach {module} download"
        logger.error(msg)
        return False, msg
    except requests.exceptions.Timeout:
        msg = f"Download timeout for {module}"
        logger.error(msg)
        return False, msg
    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error {e.response.status_code} downloading {module}"
        logger.error(msg)
        return False, msg
    except zipfile.BadZipFile:
        msg = f"Downloaded {module} is not a valid zip file"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Error downloading {module}: {str(e)}"
        logger.error(msg)
        return False, msg


def update_modules() -> Dict:
    """Update all available modules."""
    logger.info("=" * 50)
    logger.info("Starting update process...")
    logger.info("=" * 50)
    
    updates = check_updates()
    
    if not updates["updates_available"]:
        logger.info("No updates available")
        return {
            "status": "No updates available",
            "modules": [],
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    
    results = {
        "status": "Update process completed",
        "timestamp": datetime.now().isoformat(),
        "modules": [],
        "failed_modules": [],
        "success": True
    }
    
    # Download each module
    for module in updates["available_modules"]:
        success, message = download_module(module)
        
        if success:
            results["modules"].append({
                "name": module,
                "status": "success",
                "message": message
            })
        else:
            results["modules"].append({
                "name": module,
                "status": "failed",
                "message": message
            })
            results["failed_modules"].append(module)
            results["success"] = False
    
    # Update local version file only if all downloads succeeded
    if not results["failed_modules"]:
        try:
            remote_versions = get_remote_versions()
            with open(LOCAL_VERSION_FILE, "w") as f:
                json.dump(remote_versions, f, indent=2)
            logger.info("Local version file updated successfully")
            results["status"] = f"Successfully updated {len(results['modules'])} module(s)"
        except Exception as e:
            logger.error(f"Error updating version file: {e}")
            results["status"] = "Updates downloaded but version file update failed"
            results["success"] = False
    else:
        results["status"] = f"Update failed for {len(results['failed_modules'])} module(s)"
    
    logger.info("=" * 50)
    logger.info(f"Update process finished: {results['status']}")
    logger.info("=" * 50)
    
    return results
