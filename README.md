# 🚀 Self-Updating App

A modern, self-updating application built with FastAPI that automatically checks for and installs module updates. Features a beautiful, responsive web interface with real-time status updates.

## ✨ Features

- **🔄 Auto-Update System**: Automatically check for and install module updates - no manual clicks needed!
- **⚙️ Configurable**: Full control over update frequency and behavior
- **🔕 Smart Notifications**: Get notified when updates are being installed
- **Beautiful UI**: Modern, gradient-based interface with smooth animations
- **Real-Time Status**: Live feedback on update checks and installations
- **Error Handling**: Comprehensive error reporting and recovery
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Version Management**: Track module versions and update history

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

### 1. Clone or navigate to the project directory

```bash
cd self_updating_app
```

### 2. Create a virtual environment (recommended)

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

### Quick Start (All-in-One)

```bash
python run.py
```

This will:
- Start the FastAPI server on `http://127.0.0.1:8000`
- Automatically open the app in your default browser
- Keep the server running until you press `CTRL+C`

### Advanced Setup

**Terminal 1: Start the Update Server** (serves update files)
```bash
cd updates
python -m http.server 9000
```

This serves the module files and version information to the app.

**Terminal 2: Start the Main App**
```bash
python run.py
```

## 📁 Project Structure

```
self_updating_app/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── version.json              # Current module versions
├── run.py                    # Entry point (starts server & opens browser)
├── api.py                    # FastAPI application
├── updater.py                # Update logic
│
├── app/
│   ├── templates/
│   │   └── index.html        # Main web interface
│   ├── static/               # Static assets (CSS, JS, images)
│   └── modules/              # Installed modules
│       └── module1/
│
└── updates/                  # Update distribution folder
    ├── version.json          # Available module versions
    └── module1/              # Module files to distribute
        └── file.txt
```

## 🎮 How to Use

1. **Open the App**: Navigate to `http://127.0.0.1:8000` in your browser
2. **Automatic Updates**: The app checks for updates every 5 minutes by default
   - Updates are installed automatically
   - You'll see notifications about what's being updated
3. **Manual Check**: Click the "🔍 Check Updates" button to check manually
4. **View Details**: Expand the status section to see detailed information
5. **Customize Settings**: 
   - Click the ⚙️ Settings icon in the top-right
   - Enable/disable auto-updates
   - Set check frequency (1-60 minutes)
   - Toggle auto-install and notifications

### Auto-Update Features
- ✅ Runs in background automatically
- ✅ Configurable check intervals (1-60 minutes)
- ✅ Optional auto-install when updates found
- ✅ Smart notifications
- ✅ Works silently or with notifications

See [AUTO_UPDATE_GUIDE.md](AUTO_UPDATE_GUIDE.md) for detailed configuration options.

## 🔄 Update Server Files

To add or update a module:

1. Add/modify files in `updates/module_name/`
2. Update version number in `updates/version.json`:
   ```json
   {
     "module1": "1.2",
     "module2": "1.0"
   }
   ```
3. Module will be automatically detected and offered for update

### Creating a Module Update

```bash
# 1. Create module directory
mkdir -p updates/my_module

# 2. Add your module files
touch updates/my_module/file.txt

# 3. Update version.json
# Change updates/version.json to add:
# "my_module": "1.0"

# 4. The app will automatically detect it!
```

## 🛠️ Configuration

### Auto-Update Settings

**Via UI**: Click the ⚙️ Settings icon to configure:
- 🔄 Enable/disable auto-updates
- ⏱️ Check interval (1-60 minutes)
- 📦 Auto-install updates
- 🔔 Show notifications

**Via config.json**:
```json
{
  "auto_update": {
    "enabled": true,
    "check_interval_minutes": 5,
    "auto_install": true,
    "show_notification": true
  }
}
```

### Change Update Server Address

Edit `updater.py` and modify these lines:

```python
REMOTE_VERSION_URL = "http://127.0.0.1:9000/version.json"
REMOTE_BASE_URL = "http://127.0.0.1:9000"
```

### Change App Port

Edit `run.py` to modify the port:

```python
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8001)  # Change 8000 to 8001
```

## 🐛 Troubleshooting

### "Connection refused" error

**Problem**: Can't connect to update server or main app

**Solution**:
- Make sure update server is running in another terminal: `python -m http.server 9000` (from `updates/` folder)
- Check that port 8000 is not already in use
- Try changing the port in `run.py`

### "No module named" error

**Problem**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

### Updates not detected

**Problem**: App doesn't find available updates

**Solution**:
- Verify `updates/version.json` exists and has correct format
- Check that update server is running on port 9000
- Make sure local `version.json` has lower version numbers
- Check browser console for errors (F12 Dev Tools)

### Module download fails

**Problem**: Module files aren't downloading correctly

**Solution**:
- Verify module files exist in `updates/module_name/`
- Check that they're zipped correctly if stored as `.zip` files
- Ensure file paths don't contain special characters

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/check` | GET | Check for available updates |
| `/update` | GET | Install all available updates |

### Response Format

**GET /check**
```json
{
  "updates_available": true,
  "available_modules": ["module1"],
  "current_version": "1.1"
}
```

**GET /update**
```json
{
  "status": "Updated",
  "modules": ["module1"],
  "timestamp": "2026-03-18T14:30:00"
}
```

## 🎨 UI Features

- **Gradient Background**: Modern purple-to-violet gradient
- **Smooth Animations**: Floating icons and smooth transitions
- **Status Indicators**: 
  - 🔍 Checking state
  - 📦 Updates available
  - ✨ Up to date
  - ✅ Installation complete
- **Progress Bar**: Visual feedback during operations
- **Error Messages**: Clear, red-highlighted error notifications
- **Success Messages**: Green confirmations for successful operations
- **Responsive Design**: Adapts to all screen sizes

## 🚀 Building an Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed run.py
```

The executable will be in the `dist/` folder.

## 📝 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt pytest pytest-asyncio

# Run tests (if added)
pytest

# Run with auto-reload
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

### Adding New Endpoints

Edit `api.py`:

```python
@app.get("/your-endpoint")
def your_function():
    return {"message": "Hello"}
```

## 🤝 Contributing

To improve the project:

1. Modify modules in `app/modules/`
2. Update `app/templates/index.html` for UI changes
3. Modify `updater.py` for update logic changes
4. Edit `api.py` for API changes

## 📄 License

Open source - feel free to use and modify!

## 💡 Tips & Tricks

- **File Organization**: Keep module files organized in subdirectories
- **Version Numbers**: Use semantic versioning (1.0, 1.1, 2.0, etc.)
- **Testing Updates**: Test locally before distributing
- **Backup**: Keep backups of important module versions
- **Logging**: Check console output for detailed information about updates

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Server](https://www.uvicorn.org/)
- [Python Requests Library](https://requests.readthedocs.io/)

---

**Last Updated**: March 18, 2026  
**Version**: 1.0
