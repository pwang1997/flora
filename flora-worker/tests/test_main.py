import asyncio

import pytest
from fastapi.testclient import TestClient

from main import create_app


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


def pass_preflight() -> None:
    return None


def fail_preflight() -> None:
    raise RuntimeError("Failed to connect to Kafka cluster")


def test_app_lifespan_fails_when_preflight_fails() -> None:
    worker = FakeWorker()
    app = create_app(
        worker_factory=lambda: worker,
        kafka_check=fail_preflight,
        qdrant_check=pass_preflight,
    )

    with pytest.raises(RuntimeError, match="Failed to connect to Kafka cluster"):
        with TestClient(app):
            pass

    assert worker.started is False


def test_app_lifespan_starts_and_stops_background_worker() -> None:
    worker = FakeWorker()
    app = create_app(
        worker_factory=lambda: worker,
        kafka_check=pass_preflight,
        qdrant_check=pass_preflight,
    )

    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "flora-worker",
        }
        assert worker.started is True

    assert worker.cancelled is True
    assert worker.closed is True
