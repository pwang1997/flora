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
        print("IngestionWorker polling")
        events = await self.consumer.poll()
        processed = 0
        for event in events:
            await self._process_payload(event.payload)
            await self.consumer.commit(event)
            processed += 1
        print(f"IngestionWorker polled {processed} events")
        return processed

    async def _process_payload(self, payload: DocumentIngestionEventPayload) -> None:
        print("processing payload", payload)
        collection_name = f"source_{payload.source_id}"

        if payload.change_type == "deleted":
            await self.vector_store.delete_document_version(
                collection_name=collection_name,
                document_version_id=payload.document_version_id,
            )
            return

        print("embedding documents...")
        vectors = await self.embedding_service.embed_documents([payload.content])
        vector = vectors[0]
        print("document embedding completed...")

        self.vector_store.create_collection_if_not_exists(collection_name)
        print("upserting vector into vector store")
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
        print("vector upsert completed")


class Worker:
    def __init__(
        self,
        *,
        poll_interval_seconds: float = 2.0,
    ) -> None:
        self.publisher = OutboxPublisher()
        self.ingester = IngestionWorker(poll_interval_seconds=poll_interval_seconds)
        self.poll_interval_seconds = poll_interval_seconds

    async def run_forever(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(self.poll_interval_seconds)

    async def run_once(self) -> int:
        print("worker polling")

        processed = 0
        if self.publisher is not None:
            processed += await self.publisher.run_once()
        if self.ingester is not None:
            processed += await self.ingester.run_once()
        print(f"worker polled {processed} events")
        return processed

    async def close(self) -> None:
        if self.ingester is not None:
            close = getattr(self.ingester, "close", None)
            if close is not None:
                result = close()
                if inspect.isawaitable(result):
                    await result
