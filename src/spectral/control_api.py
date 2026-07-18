"""Thread-safe HTTP control plane shared by the GUI and CLI client."""

from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import queue
import threading
from typing import Any
from urllib import error, request
from urllib.parse import urlparse


@dataclass(slots=True)
class ControlRequest:
    action: str
    payload: dict[str, Any]
    reply: queue.Queue[dict[str, Any]]


class ControlBridge:
    """Move API requests onto the Qt thread without touching widgets remotely."""

    def __init__(self) -> None:
        self._commands: queue.Queue[ControlRequest] = queue.Queue()
        self._state_lock = threading.Lock()
        self._state: dict[str, Any] = {"state": "starting"}

    def request(
        self, action: str, payload: dict[str, Any] | None = None, timeout: float = 3.0
    ) -> dict[str, Any]:
        reply: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)
        self._commands.put(ControlRequest(action, payload or {}, reply))
        try:
            return reply.get(timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError(f"control action timed out: {action}") from exc

    def drain(self, limit: int = 32) -> list[ControlRequest]:
        commands: list[ControlRequest] = []
        for _ in range(limit):
            try:
                commands.append(self._commands.get_nowait())
            except queue.Empty:
                break
        return commands

    def update_state(self, state: dict[str, Any]) -> None:
        with self._state_lock:
            self._state = state.copy()

    def status(self) -> dict[str, Any]:
        with self._state_lock:
            return self._state.copy()


class _ControlHttpServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class ControlApiServer:
    ROUTES = {
        "/api/v1/exposure": "set_exposure",
        "/api/v1/exposure/auto": "set_auto_exposure",
        "/api/v1/exposure/meter": "meter_exposure",
        "/api/v1/y-scale/auto": "set_y_auto",
        "/api/v1/y-scale/fit": "fit_y",
        "/api/v1/y-scale/limits": "set_y_limits",
        "/api/v1/smoothing": "set_smoothing",
    }

    def __init__(self, bridge: ControlBridge, host: str, port: int) -> None:
        self.bridge = bridge
        self.host = host
        self.port = int(port)
        self.httpd: _ControlHttpServer | None = None
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        bridge = self.bridge
        routes = self.ROUTES

        class Handler(BaseHTTPRequestHandler):
            server_version = "AgInTiSpectrumAPI/1.0"

            def _send(self, status: int, payload: dict[str, Any]) -> None:
                encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.end_headers()
                self.wfile.write(encoded)

            def _payload(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0:
                    return {}
                value = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(value, dict):
                    raise ValueError("JSON request body must be an object")
                return value

            def do_OPTIONS(self) -> None:  # noqa: N802
                self._send(HTTPStatus.NO_CONTENT, {})

            def do_GET(self) -> None:  # noqa: N802
                path = urlparse(self.path).path.rstrip("/") or "/"
                if path in ("/health", "/api/v1/status"):
                    self._send(HTTPStatus.OK, {"ok": True, "status": bridge.status()})
                else:
                    self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})

            def do_POST(self) -> None:  # noqa: N802
                path = urlparse(self.path).path.rstrip("/")
                try:
                    payload = self._payload()
                    if path == "/api/v1/command":
                        action = str(payload.pop("action"))
                    else:
                        action = routes[path]
                    response = bridge.request(action, payload)
                    self._send(
                        HTTPStatus.OK if response.get("ok") else HTTPStatus.BAD_REQUEST,
                        response,
                    )
                except KeyError:
                    self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
                except Exception as exc:
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                    )

            def log_message(self, _format: str, *_args: object) -> None:
                return

        self.httpd = _ControlHttpServer((self.host, self.port), Handler)
        self.thread = threading.Thread(
            target=self.httpd.serve_forever,
            kwargs={"poll_interval": 0.2},
            name="spectrum-control-api",
            daemon=True,
        )
        self.thread.start()

    def stop(self) -> None:
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None


def api_request(
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    method = "GET" if payload is None else "POST"
    req = request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=5.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API {exc.code}: {detail}") from exc

