import pytest

from video_production.transitions import (
    InvalidTransition,
    ReviewScope,
    StageStatus,
    approvals_invalidated_by_change,
    transition_stage,
)


def test_failed_deliverable_can_retry_without_resetting_sibling():
    assert transition_stage(StageStatus.FAILED, "retry") is StageStatus.PENDING


def test_running_stage_cannot_start_twice():
    with pytest.raises(InvalidTransition):
        transition_stage(StageStatus.RUNNING, "start")


def test_shared_change_invalidates_every_downstream_scope():
    assert approvals_invalidated_by_change(ReviewScope.PRODUCTION) == {
        ReviewScope.PRODUCTION,
        ReviewScope.DELIVERABLE,
        ReviewScope.PUBLICATION,
    }


def test_deliverable_change_does_not_invalidate_production_scope():
    assert approvals_invalidated_by_change(ReviewScope.DELIVERABLE) == {
        ReviewScope.DELIVERABLE,
        ReviewScope.PUBLICATION,
    }
