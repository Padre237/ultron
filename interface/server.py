"""
Serveur HTTP léger pour l'interface Jarvis Orb.

Routes :
  GET /          → sert jarvis_orb.html
  GET /events    → flux SSE, pousse les changements d'état
  POST /state    → reçoit { "state": "listening" } depuis main.py
"""

import threading
import queue
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# ── État partagé ──────────────────────────────────────────────────────────────
_current_state = "rest"
_clients: list[queue.Queue] = []
_clients_lock = threading.Lock()

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_orb.html")
PORT = 8765


def set_state(new_state: str):
    """Appelé par main.py pour changer l'état et notifier tous les clients SSE."""
    global _current_state
    _current_state = new_state
    _push_event(new_state)


def _push_event(state: str):
    """Envoie un événement SSE à tous les clients connectés."""
    msg = f"event: state\ndata: {state}\n\n".encode()
    with _clients_lock:
        dead = []
        for q in _clients:
            try:
                q.put_nowait(msg)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _clients.remove(q)


# ── Gestionnaire HTTP ─────────────────────────────────────────────────────────
class JarvisHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Silencieux — ne pas polluer la console de Jarvis
        pass

    # ── GET ───────────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html()
        elif self.path == "/events":
            self._serve_sse()
        else:
            self.send_error(404)

    # ── POST ──────────────────────────────────────────────────────────────────
    def do_POST(self):
        if self.path == "/state":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                state = data.get("state", "rest")
                set_state(state)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception:
                self.send_error(400)
        else:
            self.send_error(404)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _serve_html(self):
        try:
            with open(HTML_PATH, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "jarvis_orb.html introuvable")

    def _serve_sse(self):
        self.send_response(200)
        self.send_header("Content-Type",  "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection",    "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Envoyer l'état courant immédiatement à la connexion
        try:
            init = f"event: state\ndata: {_current_state}\n\n".encode()
            self.wfile.write(init)
            self.wfile.flush()
        except Exception:
            return

        # Inscrire ce client
        client_q: queue.Queue = queue.Queue(maxsize=20)
        with _clients_lock:
            _clients.append(client_q)

        try:
            while True:
                try:
                    msg = client_q.get(timeout=15)  # timeout = heartbeat
                    self.wfile.write(msg)
                    self.wfile.flush()
                except queue.Empty:
                    # Heartbeat keep-alive
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except Exception:
            pass
        finally:
            with _clients_lock:
                if client_q in _clients:
                    _clients.remove(client_q)


# ── Démarrage du serveur dans un thread daemon ────────────────────────────────
def start(port: int = PORT):
    server = HTTPServer(("127.0.0.1", port), JarvisHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True, name="jarvis-ui-server")
    t.start()
    return server
