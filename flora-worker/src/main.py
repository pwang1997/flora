from __future__ import annotations
import sys

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

if "pytest" not in sys.modules:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

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
        logger.info("Checking Kafka connection")
        admin.describe_cluster()
        logger.info("Kafka connection ok")
    except Exception as exc:
        logger.exception("Kafka connection failed")
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
        logger.info("Checking Qdrant connection")
        client.get_collections()
        logger.info("Qdrant connection ok")
    except Exception as exc:
        logger.exception("Qdrant connection failed")
        raise RuntimeError(f"Failed to connect to Qdrant: {exc}") from exc
    finally:
        close = getattr(client, "close", None)
        if close is not None:
            close()


def _preflight_sanity_check() -> None:
    _check_kafka_connection_sync()
    if settings.worker_role != "publisher":
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
        logger.info("Running worker dependency preflight")
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
