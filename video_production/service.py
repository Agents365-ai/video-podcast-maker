from __future__ import annotations

from collections.abc import Mapping, Sequence

from .domain import (
    DeliverableSpec,
    ProcessingBoundary,
    ProductionSpecification,
    ValidationError,
)
from .store import ProductionStore
from .workers import WorkerGateway


class ProductionCoordinator:
    """Application facade and sole owner of Production State mutations."""

    def __init__(
        self,
        store: ProductionStore,
        worker_gateway: WorkerGateway,
    ) -> None:
        self._store = store
        self._worker_gateway = worker_gateway

    def create_production(
        self,
        *,
        idempotency_key: str,
        actor_id: str,
        source_snapshot_hash: str,
        deliverables: Sequence[Mapping[str, object]],
        processing_boundary: Mapping[str, object],
        supersedes_production_id: str | None = None,
    ) -> dict[str, str]:
        deliverable_specs = []
        for deliverable in deliverables:
            kind = deliverable["kind"]
            targets = deliverable.get("publication_targets", ())
            if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
                raise ValidationError(
                    "publication_targets must be a list of target names"
                )
            deliverable_specs.append(
                DeliverableSpec(
                    kind=kind,
                    publication_targets=tuple(targets),
                )
            )

        local_only = processing_boundary.get("local_only", True)
        sensitive = processing_boundary.get("sensitive", False)
        cloud_providers = processing_boundary.get("cloud_providers", ())
        spending_limit_cents = processing_boundary.get("spending_limit_cents", 0)
        if not isinstance(cloud_providers, Sequence) or isinstance(
            cloud_providers,
            (str, bytes),
        ):
            raise ValidationError("cloud_providers must be a list of provider names")
        boundary = ProcessingBoundary(
            local_only=local_only,
            sensitive=sensitive,
            cloud_providers=tuple(cloud_providers),
            spending_limit_cents=spending_limit_cents,
        )
        specification = ProductionSpecification(
            source_snapshot_hash=source_snapshot_hash,
            deliverables=tuple(deliverable_specs),
            processing_boundary=boundary,
            supersedes_production_id=supersedes_production_id,
        )
        production_id = self._store.create_production(
            idempotency_key,
            specification,
            actor_id=actor_id,
        )
        return {"production_id": production_id}

    def get_production(self, production_id: str) -> dict[str, object]:
        return self._store.get_production(production_id)
