import pytest

from video_production.domain import ValidationError
from video_production.service import ProductionCoordinator
from video_production.store import ProductionStore
from video_production.workers import FakeWorker, WorkerGateway


def test_coordinator_creates_and_queries_production(tmp_path):
    store = ProductionStore(tmp_path / "state.sqlite3")
    gateway = WorkerGateway()
    gateway.register("fake", FakeWorker(result={}))
    coordinator = ProductionCoordinator(store, gateway)

    created = coordinator.create_production(
        idempotency_key="cmd-1",
        actor_id="discord:123",
        source_snapshot_hash="a" * 64,
        deliverables=[{"kind": "youtube_long_16x9"}],
        processing_boundary={"local_only": True, "sensitive": False},
    )

    state = coordinator.get_production(created["production_id"])
    assert state["id"] == created["production_id"]
    store.close()


def test_coordinator_rejects_string_boolean_boundary(tmp_path):
    store = ProductionStore(tmp_path / "state.sqlite3")
    coordinator = ProductionCoordinator(store, WorkerGateway())

    with pytest.raises(ValidationError, match="boolean"):
        coordinator.create_production(
            idempotency_key="cmd-1",
            actor_id="discord:123",
            source_snapshot_hash="a" * 64,
            deliverables=[{"kind": "youtube_long_16x9"}],
            processing_boundary={
                "local_only": "false",
                "sensitive": False,
            },
        )
    store.close()
