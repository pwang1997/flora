from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager, suppress

import uvicorn
from fastapi import FastAPI
from kafka import KafkaAdminClient
from qdrant_client import QdrantClient

from config import settings
from polling import Worker

WorkerFactory = Callable[[], Worker]
PreflightCheck = Callable[[], None]
logger = logging.getLogger(__name__)


def _check_kafka_connection_sync() -> None:
    admin = KafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=f"{settings.kafka_consumer_client_id}-startup-check",
        security_protocol="SSL",
        ssl_cafile=settings.kafka_ssl_cafile,
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
        request_timeout_ms=3000,
        api_version_auto_timeout_ms=3000,
    )
    try:
        print("Checking Kafka connection...")
        admin.describe_cluster()
        print("Successfully connected to Kafka cluster!")
    except Exception as exc:
        raise RuntimeError(f"Failed to connect to Kafka cluster: {exc}") from exc
    finally:
        admin.close()


def _check_qdrant_connection_sync() -> None:
    client = QdrantClient(
        url=settings.qdrant_host,
        port=settings.qdrant_port,
        api_key=settings.qdrant_api_key or None,
        cloud_inference=True,
        timeout=5,
        check_compatibility=False,
    )
    try:
        print("Checking Qdrant connection...")
        client.get_collections()
        print("Successfully connected to Qdrant!")
    except Exception as exc:
        raise RuntimeError(f"Failed to connect to Qdrant: {exc}") from exc
    finally:
        close = getattr(client, "close", None)
        if close is not None:
            close()

def _preflight_sanity_check() -> None:
    _check_kafka_connection_sync()
    if settings.worker_role is not "publisher":
        _check_qdrant_connection_sync()

async def _run_worker(app: FastAPI, worker_factory: WorkerFactory) -> None:
    worker = worker_factory()
    app.state.worker = worker
    await worker.run_forever()


def create_app(
    *,
    worker_factory: WorkerFactory = Worker,
    dependency_connection_check: PreflightCheck = _preflight_sanity_check,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        dependency_connection_check()

        app.state.worker = None

        task = asyncio.create_task(_run_worker(app, worker_factory), name="flora-worker")
        app.state.worker_task = task
        await asyncio.sleep(0)

        try:
            yield
        finally:
            if not task.done():
                task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task

            worker = getattr(app.state, "worker", None)
            if worker is not None:
                await worker.close()

    app = FastAPI(title="Flora Worker", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "flora-worker",
        }

    return app


app = create_app()


def run() -> None:
    uvicorn.run(app, host=settings.worker_api_host, port=settings.worker_api_port)


if __name__ == "__main__":
    run()
