from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .domain import ValidationError
from .service import ProductionCoordinator


_MAX_REQUEST_BYTES = 1024 * 1024


class CoordinatorHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        coordinator: ProductionCoordinator,
    ) -> None:
        self.coordinator = coordinator
        super().__init__(address, CoordinatorRequestHandler)


class CoordinatorRequestHandler(BaseHTTPRequestHandler):
    server: CoordinatorHTTPServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_json(self, status: int, payload: object) -> None:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            raise ValidationError("JSON request body is required")
        if content_length > _MAX_REQUEST_BYTES:
            raise ValidationError("request body is too large")
        payload = json.loads(self.rfile.read(content_length))
        if not isinstance(payload, dict):
            raise ValidationError("JSON request body must be an object")
        return payload

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(HTTPStatus.OK, {"status": "ok"})
            return
        prefix = "/v1/productions/"
        if self.path.startswith(prefix):
            production_id = self.path[len(prefix) :]
            if not production_id or "/" in production_id:
                self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            try:
                state = self.server.coordinator.get_production(production_id)
            except KeyError:
                self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            self._write_json(HTTPStatus.OK, state)
            return
        self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/productions":
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        idempotency_key = self.headers.get("Idempotency-Key", "").strip()
        actor_id = self.headers.get("X-Actor-Id", "").strip()
        if not idempotency_key or not actor_id:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Idempotency-Key and X-Actor-Id are required"},
            )
            return

        try:
            payload = self._read_json()
            result = self.server.coordinator.create_production(
                idempotency_key=idempotency_key,
                actor_id=actor_id,
                **payload,
            )
        except ValidationError as error:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": str(error)},
            )
            return
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": str(error)},
            )
            return
        except ValueError as error:
            self._write_json(
                HTTPStatus.CONFLICT,
                {"error": str(error)},
            )
            return

        self._write_json(HTTPStatus.CREATED, result)


def create_server(
    host: str,
    port: int,
    coordinator: ProductionCoordinator,
) -> CoordinatorHTTPServer:
    return CoordinatorHTTPServer((host, port), coordinator)
