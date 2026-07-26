from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass


class ValidationError(ValueError):
    """Raised when a production domain value violates its contract."""


def canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class DeliverableSpec:
    kind: str
    publication_targets: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValidationError("Deliverable kind is required")
        if any(
            not isinstance(target, str) or not target.strip()
            for target in self.publication_targets
        ):
            raise ValidationError("Publication Target names must be non-empty strings")


@dataclass(frozen=True)
class ProcessingBoundary:
    local_only: bool = True
    sensitive: bool = False
    cloud_providers: tuple[str, ...] = ()
    spending_limit_cents: int = 0

    def __post_init__(self) -> None:
        if type(self.local_only) is not bool or type(self.sensitive) is not bool:
            raise ValidationError("processing boundary flags must be boolean")
        if type(self.spending_limit_cents) is not int:
            raise ValidationError("spending limit must be an integer")
        if self.spending_limit_cents < 0:
            raise ValidationError("spending limit cannot be negative")
        if self.sensitive and self.cloud_providers:
            raise ValidationError("sensitive productions cannot use cloud providers")
        if self.local_only and self.cloud_providers:
            raise ValidationError("local-only boundary cannot name cloud providers")


@dataclass(frozen=True)
class ProductionSpecification:
    source_snapshot_hash: str
    deliverables: tuple[DeliverableSpec, ...]
    processing_boundary: ProcessingBoundary
    supersedes_production_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_snapshot_hash, str) or re.fullmatch(
            r"[0-9a-fA-F]{64}",
            self.source_snapshot_hash,
        ) is None:
            raise ValidationError("Source Snapshot hash must be SHA-256")
        if not self.deliverables:
            raise ValidationError("at least one Deliverable is required")
