import threading
import webbrowser
import uvicorn
import time
from api import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == '__main__':
    # Start FastAPI in background
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Small delay to ensure server starts
    time.sleep(2)

    # Open in system default browser
    webbrowser.open("http://127.0.0.1:8000")

    # Keep the main thread alive so the daemon server keeps running
    t.join()