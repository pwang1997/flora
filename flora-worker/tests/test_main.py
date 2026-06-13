import asyncio

from fastapi.testclient import TestClient

from main import DependencyStatus, create_app


class FakeWorker:
    def __init__(self) -> None:
        self.started = False
        self.closed = False
        self.cancelled = False

    async def run_forever(self) -> None:
        self.started = True
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self.cancelled = True
            raise

    async def close(self) -> None:
        self.closed = True


async def passing_dependencies():
    return {
        "kafka": DependencyStatus(status="ok"),
        "qdrant": DependencyStatus(status="ok"),
    }


async def failing_dependencies():
    return {
        "kafka": DependencyStatus(status="failed", error="NoBrokersAvailable"),
        "qdrant": DependencyStatus(status="ok"),
    }


def test_worker_health_check_blocks_when_dependency_preflight_fails() -> None:
    worker = FakeWorker()
    app = create_app(
        worker_factory=lambda: worker,
        dependency_checker=failing_dependencies,
    )

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "flora-worker",
        "worker": "blocked",
        "dependencies": {
            "kafka": {"status": "failed", "error": "NoBrokersAvailable"},
            "qdrant": {"status": "ok", "error": None},
        },
    }
    assert worker.started is False


def test_app_lifespan_starts_and_stops_background_worker() -> None:
    worker = FakeWorker()
    app = create_app(
        worker_factory=lambda: worker,
        dependency_checker=passing_dependencies,
    )

    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "flora-worker",
            "worker": "running",
            "dependencies": {
                "kafka": {"status": "ok", "error": None},
                "qdrant": {"status": "ok", "error": None},
            },
        }
        assert worker.started is True

    assert worker.cancelled is True
    assert worker.closed is True


def test_app_lifespan_reports_failed_background_worker() -> None:
    def fail_to_create_worker():
        raise RuntimeError("broker unavailable")

    app = create_app(
        worker_factory=fail_to_create_worker,
        dependency_checker=passing_dependencies,
    )

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "flora-worker",
        "worker": "failed",
        "dependencies": {
            "kafka": {"status": "ok", "error": None},
            "qdrant": {"status": "ok", "error": None},
        },
    }
