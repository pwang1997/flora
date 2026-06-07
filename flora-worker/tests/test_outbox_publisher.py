from datetime import timedelta

import pytest
from sqlalchemy import insert

from flora_worker.publishers.outbox_publisher import OutboxPublisher
from flora_worker.repositories.outbox.outbox_repository import (
    claim_due_events,
    list_outbox_events,
    mark_outbox_event_failed,
    outbox_events,
    release_stale_claims,
    utc_now,
)


class FakeProducer:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.published: list[tuple[str, str, dict]] = []
        self.closed = False

    def publish(self, *, topic: str, key: str, payload: dict) -> None:
        if self.should_fail:
            raise RuntimeError("publish failed")
        self.published.append((topic, key, payload))

    def close(self) -> None:
        self.closed = True


async def _seed_event(async_session_factory, *, status: str = "pending", retries: int = 0) -> None:
    now = utc_now()
    async with async_session_factory() as db:
        await db.execute(
            insert(outbox_events).values(
                id="evt_1",
                event_type="document.version.created",
                source_document_id="doc_1",
                document_version_id="ver_1",
                topic="flora.documents.created",
                key="doc_1",
                idempotency_key="doc_1:ver_1:created",
                payload={
                    "event_type": "document.version.created",
                    "source_document_id": "doc_1",
                    "document_version_id": "ver_1",
                    "source_id": "src_1",
                    "version_number": 1,
                    "change_type": "created",
                    "content_hash": "hash_1",
                    "content": "content",
                    "title": "Readme",
                    "uri": "file:///README.md",
                    "metadata": {},
                    "occurred_at": now.isoformat(),
                },
                status=status,
                retries=retries,
                last_error=None,
                last_attempt_at=None,
                next_attempt_at=now,
                claimed_at=None,
                claimed_by=None,
                published_at=None,
                created_at=now,
                updated_at=now,
            )
        )
        await db.commit()


@pytest.mark.anyio
async def test_outbox_repository_claim_publish_fail_and_release(async_session_factory) -> None:
    await _seed_event(async_session_factory)

    async with async_session_factory() as db:
        claimed = await claim_due_events(db, now=utc_now(), claimed_by="worker-1", limit=10)
        await db.commit()
        assert [event.id for event in claimed] == ["evt_1"]
        assert claimed[0].status == "publishing"

    async with async_session_factory() as db:
        released = await release_stale_claims(db, utc_now() + timedelta(seconds=1))
        await db.commit()
        assert [event.id for event in released] == ["evt_1"]

    async with async_session_factory() as db:
        claimed = await claim_due_events(db, now=utc_now(), claimed_by="worker-1", limit=10)
        failed = await mark_outbox_event_failed(
            db,
            claimed[0].id,
            failed_at=utc_now(),
            last_error="boom",
            next_attempt_at=utc_now() + timedelta(seconds=30),
        )
        await db.commit()
        assert failed is not None
        assert failed.status == "failed"
        assert failed.retries == 1
        assert failed.last_error == "boom"


@pytest.mark.anyio
async def test_outbox_publisher_marks_published(async_session_factory) -> None:
    await _seed_event(async_session_factory)
    fake = FakeProducer()
    publisher = OutboxPublisher(
        session_factory=async_session_factory,
        producer_factory=lambda: fake,
    )

    processed = await publisher.run_once()

    assert processed == 1
    assert len(fake.published) == 1
    topic, key, payload = fake.published[0]
    assert topic == "flora.documents.created"
    assert key == "doc_1"
    assert payload["source_document_id"] == "doc_1"
    assert payload["document_version_id"] == "ver_1"
    assert payload["content"] == "content"
    assert fake.closed is True

    async with async_session_factory() as db:
        events = await list_outbox_events(db)
        assert events[0].status == "published"
        assert events[0].published_at is not None


@pytest.mark.anyio
async def test_outbox_publisher_marks_failed(async_session_factory) -> None:
    await _seed_event(async_session_factory)
    fake = FakeProducer(should_fail=True)
    publisher = OutboxPublisher(
        session_factory=async_session_factory,
        producer_factory=lambda: fake,
    )

    processed = await publisher.run_once()

    assert processed == 0
    assert fake.closed is True
    async with async_session_factory() as db:
        events = await list_outbox_events(db)
        assert events[0].status == "failed"
        assert events[0].retries == 1
        assert events[0].last_error == "publish failed"
        assert events[0].claimed_at is None
        assert events[0].claimed_by is None
