import asyncio
from typing import Literal

from flora_worker.config import settings
from flora_worker.consumers.source_document_consumer import SourceDocumentConsumer
from flora_worker.embeddings import EmbeddingService
from flora_worker.models import DocumentIngestionEventPayload
from flora_worker.publishers.outbox_publisher import OutboxPublisher
from flora_worker.vector_store import QdrantVectorStore

WorkerRole = Literal["publisher", "ingester", "all"]


class IngestionWorker:
    def __init__(
        self,
        consumer: SourceDocumentConsumer | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: QdrantVectorStore | None = None,
        poll_interval_seconds: float = 2.0,
    ) -> None:
        self.consumer = consumer or SourceDocumentConsumer()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or QdrantVectorStore()
        self.poll_interval_seconds = poll_interval_seconds

    async def run_forever(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(self.poll_interval_seconds)

    async def run_once(self) -> int:
        events = await self.consumer.poll()
        processed = 0
        for event in events:
            await self._process_payload(event.payload)
            await self.consumer.commit(event)
            processed += 1
        return processed

    async def _process_payload(self, payload: DocumentIngestionEventPayload) -> None:
        if payload.change_type == "deleted":
            await self.vector_store.delete_document_version(payload.document_version_id)
            return

        vector = await self.embedding_service.embed(payload.content)
        await self.vector_store.upsert_document_version(
            document_version_id=payload.document_version_id,
            vector=vector,
            payload={
                "source_document_id": payload.source_document_id,
                "document_version_id": payload.document_version_id,
                "source_id": payload.source_id,
                "version_number": payload.version_number,
                "change_type": payload.change_type,
                "content_hash": payload.content_hash,
                "title": payload.title,
                "uri": payload.uri,
                "metadata": payload.metadata,
            },
        )


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
        processed = 0
        if self.publisher is not None:
            processed += await self.publisher.run_once()
        if self.ingester is not None:
            processed += await self.ingester.run_once()
        return processed
