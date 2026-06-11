import asyncio
from datetime import UTC, datetime

import pytest

from consumers.source_document_consumer import ConsumedDocumentEvent
from models import DocumentIngestionEventPayload
from polling import IngestionWorker, Worker


class FakeConsumer:
    def __init__(self, events):
        self._events = events
        self.committed_offsets: list[int] = []

    async def poll(self):
        return list(self._events)

    async def commit(self, event):
        self.committed_offsets.append(event.offset)


class FakeEmbeddingService:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.inputs: list[str] = []

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self.should_fail:
            raise RuntimeError("embedding failed")
        self.inputs.extend(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeVectorStore:
    def __init__(self) -> None:
        self.upserts: list[tuple[str, list[float], dict]] = []
        self.deletes: list[str] = []

    def create_collection_if_not_exists(self, collection_name: str) -> None:
        return None

    async def upsert_document_version(
        self,
        *,
        collection_name: str,
        document_version_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        self.upserts.append((document_version_id, vector, payload))

    async def delete_document_version(self, *, collection_name: str, document_version_id: str) -> None:
        self.deletes.append(document_version_id)


def _event(change_type: str = "created", offset: int = 0) -> ConsumedDocumentEvent:
    return ConsumedDocumentEvent(
        payload=DocumentIngestionEventPayload(
            event_type=f"document.version.{change_type}",
            source_document_id="doc_1",
            document_version_id=f"ver_{offset + 1}",
            source_id="src_1",
            version_number=offset + 1,
            change_type=change_type,
            content_hash=f"hash_{offset + 1}",
            content=f"content {offset + 1}",
            title="Readme",
            uri="file:///README.md",
            metadata={"folder": "docs"},
            occurred_at=datetime.now(UTC),
        ),
        topic="flora.documents.created",
        partition=0,
        offset=offset,
    )


def test_worker_processes_create_and_update_events() -> None:
    consumer = FakeConsumer([_event("created", 0), _event("updated", 1)])
    embeddings = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    processed = asyncio.run(
        Worker(
            role="ingester",
            ingester=IngestionWorker(
                consumer=consumer,
                embedding_service=embeddings,
                vector_store=vector_store,
            ),
        ).run_once()
    )

    assert processed == 2
    assert embeddings.inputs == ["content 1", "content 2"]
    assert consumer.committed_offsets == [0, 1]
    assert len(vector_store.upserts) == 2
    assert vector_store.upserts[0][0] == "ver_1"
    assert vector_store.upserts[0][2]["source_document_id"] == "doc_1"


def test_worker_deletes_qdrant_point_for_deleted_events() -> None:
    consumer = FakeConsumer([_event("deleted", 0)])
    embeddings = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    processed = asyncio.run(
        Worker(
            role="ingester",
            ingester=IngestionWorker(
                consumer=consumer,
                embedding_service=embeddings,
                vector_store=vector_store,
            ),
        ).run_once()
    )

    assert processed == 1
    assert embeddings.inputs == []
    assert vector_store.deletes == ["ver_1"]
    assert consumer.committed_offsets == [0]


def test_worker_does_not_commit_offset_when_handler_fails() -> None:
    consumer = FakeConsumer([_event("created", 0)])
    embeddings = FakeEmbeddingService(should_fail=True)
    vector_store = FakeVectorStore()

    with pytest.raises(RuntimeError, match="embedding failed"):
        asyncio.run(
            Worker(
                role="ingester",
                ingester=IngestionWorker(
                    consumer=consumer,
                    embedding_service=embeddings,
                    vector_store=vector_store,
                ),
            ).run_once()
        )

    assert consumer.committed_offsets == []
    assert vector_store.upserts == []


class FakePublisher:
    def __init__(self, processed: int) -> None:
        self.processed = processed
        self.calls = 0

    async def run_once(self) -> int:
        self.calls += 1
        return self.processed


class FakeIngester:
    def __init__(self, processed: int) -> None:
        self.processed = processed
        self.calls = 0

    async def run_once(self) -> int:
        self.calls += 1
        return self.processed


def test_worker_role_publisher_runs_only_publisher() -> None:
    publisher = FakePublisher(2)
    ingester = FakeIngester(3)

    processed = asyncio.run(Worker(role="publisher", publisher=publisher, ingester=ingester).run_once())

    assert processed == 2
    assert publisher.calls == 1
    assert ingester.calls == 0


def test_worker_role_ingester_runs_only_ingester() -> None:
    publisher = FakePublisher(2)
    ingester = FakeIngester(3)

    processed = asyncio.run(Worker(role="ingester", publisher=publisher, ingester=ingester).run_once())

    assert processed == 3
    assert publisher.calls == 0
    assert ingester.calls == 1


def test_worker_role_all_runs_publisher_and_ingester() -> None:
    publisher = FakePublisher(2)
    ingester = FakeIngester(3)

    processed = asyncio.run(Worker(role="all", publisher=publisher, ingester=ingester).run_once())

    assert processed == 5
    assert publisher.calls == 1
    assert ingester.calls == 1
