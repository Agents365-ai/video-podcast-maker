from __future__ import annotations

from enum import Enum


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewScope(str, Enum):
    PRODUCTION = "production"
    DELIVERABLE = "deliverable"
    PUBLICATION = "publication"


class InvalidTransition(ValueError):
    """Raised when a stage command is invalid for its current state."""


_TRANSITIONS = {
    (StageStatus.PENDING, "start"): StageStatus.RUNNING,
    (StageStatus.RUNNING, "succeed"): StageStatus.SUCCEEDED,
    (StageStatus.RUNNING, "fail"): StageStatus.FAILED,
    (StageStatus.PENDING, "cancel"): StageStatus.CANCELLED,
    (StageStatus.RUNNING, "cancel"): StageStatus.CANCELLED,
    (StageStatus.FAILED, "retry"): StageStatus.PENDING,
}


def transition_stage(current: StageStatus, command: str) -> StageStatus:
    try:
        return _TRANSITIONS[(current, command)]
    except KeyError as error:
        raise InvalidTransition(
            f"cannot {command} stage from {current.value}"
        ) from error


def approvals_invalidated_by_change(scope: ReviewScope) -> set[ReviewScope]:
    if scope is ReviewScope.PRODUCTION:
        return {
            ReviewScope.PRODUCTION,
            ReviewScope.DELIVERABLE,
            ReviewScope.PUBLICATION,
        }
    if scope is ReviewScope.DELIVERABLE:
        return {
            ReviewScope.DELIVERABLE,
            ReviewScope.PUBLICATION,
        }
    return {ReviewScope.PUBLICATION}
