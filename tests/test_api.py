import json
import threading
import urllib.request

from video_production.api import create_server
from video_production.service import ProductionCoordinator
from video_production.store import ProductionStore
from video_production.workers import WorkerGateway


def request_json(url, method="GET", payload=None, headers=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers or {},
    )
    with urllib.request.urlopen(request, timeout=2) as response:
        return response.status, json.load(response)


def test_health_and_idempotent_create(tmp_path):
    store = ProductionStore(tmp_path / "state.sqlite3")
    coordinator = ProductionCoordinator(store, WorkerGateway())
    server = create_server("127.0.0.1", 0, coordinator)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        assert request_json(f"{base}/health") == (200, {"status": "ok"})
        payload = {
            "source_snapshot_hash": "a" * 64,
            "deliverables": [{"kind": "youtube_long_16x9"}],
            "processing_boundary": {
                "local_only": True,
                "sensitive": False,
            },
        }
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": "cmd-1",
            "X-Actor-Id": "discord:123",
        }
        first = request_json(
            f"{base}/v1/productions",
            "POST",
            payload,
            headers,
        )
        second = request_json(
            f"{base}/v1/productions",
            "POST",
            payload,
            headers,
        )
        assert first == second
        assert first[0] == 201
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        store.close()
