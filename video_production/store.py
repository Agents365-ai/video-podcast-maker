from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .domain import ProductionSpecification, canonical_hash


_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
    version INTEGER NOT NULL
);

INSERT OR IGNORE INTO schema_version(singleton, version) VALUES (1, 1);

CREATE TABLE IF NOT EXISTS productions (
    id TEXT PRIMARY KEY,
    source_snapshot_hash TEXT NOT NULL,
    specification_json TEXT NOT NULL,
    status TEXT NOT NULL,
    supersedes_production_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deliverables (
    id TEXT PRIMARY KEY,
    production_id TEXT NOT NULL REFERENCES productions(id),
    kind TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commands (
    idempotency_key TEXT PRIMARY KEY,
    command_type TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    production_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _specification_dict(specification: ProductionSpecification) -> dict[str, object]:
    boundary = specification.processing_boundary
    return {
        "source_snapshot_hash": specification.source_snapshot_hash,
        "deliverables": [
            {
                "kind": deliverable.kind,
                "publication_targets": list(deliverable.publication_targets),
            }
            for deliverable in specification.deliverables
        ],
        "processing_boundary": {
            "local_only": boundary.local_only,
            "sensitive": boundary.sensitive,
            "cloud_providers": list(boundary.cloud_providers),
            "spending_limit_cents": boundary.spending_limit_cents,
        },
        "supersedes_production_id": specification.supersedes_production_id,
    }


def _existing_schema_version(connection: sqlite3.Connection) -> int | None:
    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'schema_version'
        """
    ).fetchone()
    if table is None:
        return None
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(schema_version)").fetchall()
    }
    if columns != {"singleton", "version"}:
        raise RuntimeError("unsupported schema_version table layout")
    row = connection.execute(
        "SELECT version FROM schema_version WHERE singleton = 1"
    ).fetchone()
    if row is None:
        raise RuntimeError("schema_version row is missing")
    return int(row["version"])


class ProductionStore:
    """SQLite authority for mutable Production State."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            self.path,
            isolation_level=None,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        with self._lock:
            existing_version = _existing_schema_version(self._connection)
            if existing_version not in (None, 1):
                self._connection.close()
                raise RuntimeError(
                    f"unsupported schema version {existing_version}; expected 1"
                )
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.executescript(_SCHEMA)

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                yield self._connection
            except BaseException:
                self._connection.rollback()
                raise
            else:
                self._connection.commit()

    def create_production(
        self,
        idempotency_key: str,
        specification: ProductionSpecification,
        *,
        actor_id: str,
    ) -> str:
        specification_data = _specification_dict(specification)
        request_data = {
            "actor_id": actor_id,
            "specification": specification_data,
        }
        request_hash = canonical_hash(request_data)
        specification_json = json.dumps(
            specification_data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        with self._transaction() as connection:
            existing = connection.execute(
                """
                SELECT request_hash, result_json
                FROM commands
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                if existing["request_hash"] != request_hash:
                    raise ValueError(
                        "idempotency key was already used for a different request"
                    )
                return json.loads(existing["result_json"])["production_id"]

            created_at = _utc_now()
            production_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO productions(
                    id,
                    source_snapshot_hash,
                    specification_json,
                    status,
                    supersedes_production_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    production_id,
                    specification.source_snapshot_hash,
                    specification_json,
                    "draft",
                    specification.supersedes_production_id,
                    created_at,
                ),
            )
            for deliverable in specification.deliverables:
                connection.execute(
                    """
                    INSERT INTO deliverables(id, production_id, kind, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        production_id,
                        deliverable.kind,
                        "pending",
                    ),
                )

            result_json = json.dumps(
                {"production_id": production_id},
                sort_keys=True,
                separators=(",", ":"),
            )
            connection.execute(
                """
                INSERT INTO commands(
                    idempotency_key,
                    command_type,
                    request_hash,
                    result_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    idempotency_key,
                    "create_production",
                    request_hash,
                    result_json,
                    created_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO audit_events(
                    production_id,
                    event_type,
                    actor_id,
                    idempotency_key,
                    payload_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    production_id,
                    "production_created",
                    actor_id,
                    idempotency_key,
                    result_json,
                    created_at,
                ),
            )
            return production_id

    def get_production(self, production_id: str) -> dict[str, object]:
        with self._lock:
            production = self._connection.execute(
                """
                SELECT id, source_snapshot_hash, specification_json, status,
                       supersedes_production_id, created_at
                FROM productions
                WHERE id = ?
                """,
                (production_id,),
            ).fetchone()
            if production is None:
                raise KeyError(production_id)
            deliverables = self._connection.execute(
                """
                SELECT id, kind, status
                FROM deliverables
                WHERE production_id = ?
                ORDER BY rowid
                """,
                (production_id,),
            ).fetchall()

        return {
            "id": production["id"],
            "source_snapshot_hash": production["source_snapshot_hash"],
            "specification": json.loads(production["specification_json"]),
            "status": production["status"],
            "supersedes_production_id": production["supersedes_production_id"],
            "created_at": production["created_at"],
            "deliverables": [dict(deliverable) for deliverable in deliverables],
        }

    def list_audit_events(self, production_id: str) -> list[dict[str, object]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT sequence, event_type, actor_id, idempotency_key,
                       payload_json, created_at
                FROM audit_events
                WHERE production_id = ?
                ORDER BY sequence
                """,
                (production_id,),
            ).fetchall()
        return [
            {
                "sequence": row["sequence"],
                "event_type": row["event_type"],
                "actor_id": row["actor_id"],
                "idempotency_key": row["idempotency_key"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def close(self) -> None:
        with self._lock:
            self._connection.close()
