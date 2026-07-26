from dataclasses import FrozenInstanceError

import pytest

from video_production.domain import (
    DeliverableSpec,
    ProcessingBoundary,
    ProductionSpecification,
    ValidationError,
    canonical_hash,
)


def test_canonical_hash_ignores_mapping_order():
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})


def test_specification_is_immutable_and_requires_deliverables():
    boundary = ProcessingBoundary(local_only=True, sensitive=False)
    specification = ProductionSpecification(
        source_snapshot_hash="a" * 64,
        deliverables=(DeliverableSpec(kind="youtube_long_16x9"),),
        processing_boundary=boundary,
    )

    with pytest.raises(FrozenInstanceError):
        specification.source_snapshot_hash = "b" * 64

    with pytest.raises(ValidationError, match="at least one Deliverable"):
        ProductionSpecification(
            source_snapshot_hash="a" * 64,
            deliverables=(),
            processing_boundary=boundary,
        )


def test_sensitive_boundary_rejects_cloud_providers():
    with pytest.raises(ValidationError, match="sensitive"):
        ProcessingBoundary(
            local_only=False,
            sensitive=True,
            cloud_providers=("example-cloud",),
            spending_limit_cents=100,
        )


def test_domain_rejects_non_hex_source_hash_and_non_boolean_boundary():
    with pytest.raises(ValidationError, match="SHA-256"):
        ProductionSpecification(
            source_snapshot_hash="z" * 64,
            deliverables=(DeliverableSpec(kind="youtube_long_16x9"),),
            processing_boundary=ProcessingBoundary(),
        )

    with pytest.raises(ValidationError, match="boolean"):
        ProcessingBoundary(local_only="false")
