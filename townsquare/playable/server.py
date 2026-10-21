#!/usr/bin/env python3
import http.server
import json
import socketserver
from pathlib import Path

PORT = 8080
DIR = Path(__file__).resolve().parent
STATE_JSON = DIR.parent / "evidence" / "validation" / "playable_state.json"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/playable"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = STATE_JSON.read_text(encoding="utf-8") if STATE_JSON.exists() else "{}"
            self.wfile.write(data.encode("utf-8"))
            return
        return super().do_GET()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Playable 3D City Server listening on http://0.0.0.0:{PORT}", flush=True)
        httpd.serve_forever()
