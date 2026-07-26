import pytest

from video_production.workers import FakeWorker, WorkerGateway, WorkerRequest


def test_gateway_dispatches_to_named_worker():
    gateway = WorkerGateway()
    gateway.register("fake", FakeWorker(result={"artifact_hash": "abc"}))
    result = gateway.dispatch(
        WorkerRequest(
            run_id="run-1",
            worker_name="fake",
            production_id="prod-1",
            deliverable_id=None,
            stage="script",
            inputs={"source_hash": "a" * 64},
        )
    )
    assert result.run_id == "run-1"
    assert result.status == "succeeded"
    assert result.outputs == {"artifact_hash": "abc"}


def test_duplicate_run_returns_same_result():
    worker = FakeWorker(result={"artifact_hash": "abc"})
    gateway = WorkerGateway()
    gateway.register("fake", worker)
    request = WorkerRequest(
        run_id="run-1",
        worker_name="fake",
        production_id="prod-1",
        deliverable_id=None,
        stage="script",
        inputs={},
    )

    assert gateway.dispatch(request) == gateway.dispatch(request)
    assert worker.calls == 1


def test_duplicate_run_rejects_different_request():
    gateway = WorkerGateway()
    gateway.register("fake", FakeWorker(result={}))
    gateway.dispatch(
        WorkerRequest("run-1", "fake", "prod-1", None, "script", {})
    )

    with pytest.raises(ValueError, match="different worker request"):
        gateway.dispatch(
            WorkerRequest("run-1", "fake", "prod-2", None, "script", {})
        )
