#!/usr/bin/env python3
"""
Combined server: serves dashboard HTML + API endpoints for save/load
Runs on port 8765 (single port, no CORS issues)
"""
import json, os, http.server, urllib.parse, mimetypes

DASHBOARD_DIR = os.path.expanduser('~/.openclaw/workspace/dashboard')
DATA_FILE = os.path.join(DASHBOARD_DIR, 'dashboard-data.json')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/load':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE) as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b'{}')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            try:
                data = json.loads(body)
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

PORT = 8765
print(f'🚀 Dashboard + API en puerto {PORT} (0.0.0.0)')
server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
