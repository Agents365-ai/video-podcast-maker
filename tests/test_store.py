import sqlite3

import pytest

from video_production.domain import (
    DeliverableSpec,
    ProcessingBoundary,
    ProductionSpecification,
)
from video_production.store import ProductionStore


def make_specification() -> ProductionSpecification:
    return ProductionSpecification(
        source_snapshot_hash="a" * 64,
        deliverables=(DeliverableSpec(kind="youtube_long_16x9"),),
        processing_boundary=ProcessingBoundary(),
    )


def test_create_is_idempotent_and_survives_reopen(tmp_path):
    path = tmp_path / "state.sqlite3"
    store = ProductionStore(path)
    first = store.create_production(
        "cmd-1",
        make_specification(),
        actor_id="discord:123",
    )
    second = store.create_production(
        "cmd-1",
        make_specification(),
        actor_id="discord:123",
    )
    assert first == second
    store.close()

    reopened = ProductionStore(path)
    state = reopened.get_production(first)
    assert state["source_snapshot_hash"] == "a" * 64
    assert [item["kind"] for item in state["deliverables"]] == [
        "youtube_long_16x9"
    ]
    reopened.close()


def test_same_idempotency_key_rejects_different_payload(tmp_path):
    store = ProductionStore(tmp_path / "state.sqlite3")
    store.create_production(
        "cmd-1",
        make_specification(),
        actor_id="telegram:123",
    )
    changed = ProductionSpecification(
        source_snapshot_hash="b" * 64,
        deliverables=(DeliverableSpec(kind="short_9x16"),),
        processing_boundary=ProcessingBoundary(),
    )

    with pytest.raises(ValueError, match="idempotency"):
        store.create_production(
            "cmd-1",
            changed,
            actor_id="telegram:123",
        )
    store.close()


def test_audit_event_records_actor_and_command(tmp_path):
    store = ProductionStore(tmp_path / "state.sqlite3")
    production_id = store.create_production(
        "cmd-1",
        make_specification(),
        actor_id="discord:123",
    )
    events = store.list_audit_events(production_id)
    assert events[0]["actor_id"] == "discord:123"
    assert events[0]["idempotency_key"] == "cmd-1"
    store.close()


def test_unknown_schema_version_fails_safely(tmp_path):
    path = tmp_path / "state.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE schema_version (
            singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
            version INTEGER NOT NULL
        );
        INSERT INTO schema_version(singleton, version) VALUES (1, 999);
        """
    )
    connection.close()

    with pytest.raises(RuntimeError, match="schema version 999"):
        ProductionStore(path)
