from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
ADDRESS = "127.0.0.1"
PORT = 8765


class AppFiles(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "dist"), **kwargs)


server = ThreadingHTTPServer((ADDRESS, PORT), AppFiles)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://{ADDRESS}:{PORT}"
print(f"Zbrojni Trainer is open at {url}")
print("Leave this window open while using the app. Press Ctrl+C to stop it.")
webbrowser.open(url)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping Zbrojni Trainer.")
finally:
    server.shutdown()
    server.server_close()
