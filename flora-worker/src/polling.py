import logging
import asyncio
import inspect
from typing import Literal

from config import settings
from consumers.source_document_consumer import SourceDocumentConsumer
from embeddings.factory import create_embedding_provider
from models import DocumentIngestionEventPayload
from publishers.outbox_publisher import OutboxPublisher
from vector_store import QdrantVectorStore

WorkerRole = Literal["publisher", "ingester", "all"]
logger = logging.getLogger(__name__)


class IngestionWorker:
    def __init__(
        self,
        consumer: SourceDocumentConsumer | None = None,
        embedding_service=None,
        vector_store: QdrantVectorStore | None = None,
        poll_interval_seconds: float = 2.0,
    ) -> None:
        self.consumer = consumer or SourceDocumentConsumer()
        self.embedding_service = embedding_service or create_embedding_provider(settings)
        self.vector_store = vector_store or QdrantVectorStore()
        self.poll_interval_seconds = poll_interval_seconds

    async def run_forever(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(self.poll_interval_seconds)

    async def close(self) -> None:
        await self.consumer.close()

    async def run_once(self) -> int:
        logger.info("Ingestion worker polling")
        events = await self.consumer.poll()
        processed = 0
        for event in events:
            await self._process_payload(event.payload)
            await self.consumer.commit(event)
            processed += 1
        logger.info("Ingestion worker processed %s events", processed)
        return processed

    async def _process_payload(self, payload: DocumentIngestionEventPayload) -> None:
        logger.debug("Processing payload for document_version_id=%s", payload.document_version_id)
        collection_name = f"source_{payload.source_id}"

        if payload.change_type == "deleted":
            logger.info("Deleting Qdrant point for document_version_id=%s", payload.document_version_id)
            await self.vector_store.delete_document_version(
                collection_name=collection_name,
                document_version_id=payload.document_version_id,
            )
            return

        logger.debug("Embedding document_version_id=%s", payload.document_version_id)
        vectors = await self.embedding_service.embed_documents([payload.content])
        vector = vectors[0]
        logger.debug("Embedding completed for document_version_id=%s", payload.document_version_id)

        self.vector_store.create_collection_if_not_exists(collection_name)
        logger.info("Upserting vector into Qdrant for document_version_id=%s", payload.document_version_id)
        await self.vector_store.upsert_document_version(
            collection_name=collection_name,
            document_version_id=payload.document_version_id,
            vector=vector,
            payload={
                "source_document_id": payload.source_document_id,
                "document_version_id": payload.document_version_id,
                "source_id": payload.source_id,
                "version_number": payload.version_number,
                "change_type": payload.change_type,
                "content_hash": payload.content_hash,
                "content" : payload.content,
                "title": payload.title,
                "uri": payload.uri,
                "metadata": payload.metadata,
            },
        )
        logger.info("Vector upsert completed for document_version_id=%s", payload.document_version_id)


class Worker:
    def __init__(
        self,
        *,
        role: WorkerRole | None = None,
        publisher: OutboxPublisher | None = None,
        ingester: IngestionWorker | None = None,
        poll_interval_seconds: float = 2.0,
    ) -> None:
        self.role = role or settings.worker_role
        logger.info("Initializing worker role=%s", self.role)
        self.publisher = publisher if self.role in ("publisher", "all") else None
        self.ingester = ingester if self.role in ("ingester", "all") else None
        if self.publisher is None and self.role in ("publisher", "all"):
            self.publisher = OutboxPublisher()
        if self.ingester is None and self.role in ("ingester", "all"):
            self.ingester = IngestionWorker(poll_interval_seconds=poll_interval_seconds)
        self.poll_interval_seconds = poll_interval_seconds

    async def run_forever(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(self.poll_interval_seconds)

    async def run_once(self) -> int:
        logger.info("Worker polling")

        processed = 0
        if self.publisher is not None:
            processed += await self.publisher.run_once()
        if self.ingester is not None:
            processed += await self.ingester.run_once()
        logger.info("Worker processed %s events", processed)
        return processed

    async def close(self) -> None:
        if self.ingester is not None:
            close = getattr(self.ingester, "close", None)
            if close is not None:
                result = close()
                if inspect.isawaitable(result):
                    await result
