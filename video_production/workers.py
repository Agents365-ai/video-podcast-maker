from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class WorkerRequest:
    run_id: str
    worker_name: str
    production_id: str
    deliverable_id: str | None
    stage: str
    inputs: dict[str, object]


@dataclass(frozen=True)
class WorkerResult:
    run_id: str
    status: str
    outputs: dict[str, object]
    error: str | None = None


class Worker(Protocol):
    def execute(self, request: WorkerRequest) -> WorkerResult:
        """Execute one idempotently identified worker request."""


class FakeWorker:
    def __init__(
        self,
        *,
        result: dict[str, object] | None = None,
        error: str | None = None,
    ) -> None:
        self._result = result or {}
        self._error = error
        self.calls = 0

    def execute(self, request: WorkerRequest) -> WorkerResult:
        self.calls += 1
        if self._error is not None:
            return WorkerResult(
                run_id=request.run_id,
                status="failed",
                outputs={},
                error=self._error,
            )
        return WorkerResult(
            run_id=request.run_id,
            status="succeeded",
            outputs=dict(self._result),
        )


class WorkerGateway:
    def __init__(self) -> None:
        self._workers: dict[str, Worker] = {}
        self._requests: dict[str, WorkerRequest] = {}
        self._results: dict[str, WorkerResult] = {}
        self._lock = threading.RLock()

    def register(self, name: str, worker: Worker) -> None:
        with self._lock:
            self._workers[name] = worker

    def dispatch(self, request: WorkerRequest) -> WorkerResult:
        with self._lock:
            existing_request = self._requests.get(request.run_id)
            if existing_request is not None and existing_request != request:
                raise ValueError(
                    "run ID was already used for a different worker request"
                )
            existing_result = self._results.get(request.run_id)
            if existing_result is not None:
                return existing_result
            self._requests[request.run_id] = request
            result = self._workers[request.worker_name].execute(request)
            self._results[request.run_id] = result
            return result
