from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flora_worker.config import settings
from flora_worker.database import SessionLocal
from flora_worker.publishers.source_document_producer import SourceDocumentProducer
from flora_worker.repositories.outbox import outbox_repository


class OutboxPublisher:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = SessionLocal,
        producer_factory: Callable[[], SourceDocumentProducer] = SourceDocumentProducer,
    ) -> None:
        self._session_factory = session_factory
        self._producer_factory = producer_factory
        self.claimed_by = settings.kafka_producer_client_id

    async def run_once(self) -> int:
        events = await self._claim_due_events()
        if not events:
            return 0

        producer = self._producer_factory()
        published = 0
        try:
            for event in events:
                try:
                    await asyncio.to_thread(
                        producer.publish,
                        topic=event.topic,
                        key=event.source_document_id,
                        payload=event.payload,
                    )
                except Exception as exc:
                    await self._mark_failed(event.id, exc)
                else:
                    await self._mark_published(event.id)
                    published += 1
        finally:
            producer.close()
        return published

    async def _claim_due_events(self) -> list[outbox_repository.OutboxEvent]:
        now = outbox_repository.utc_now()
        stale_before = now - timedelta(seconds=settings.outbox_claim_timeout_seconds)
        async with self._session_factory() as db:
            await outbox_repository.release_stale_claims(db, stale_before)
            events = await outbox_repository.claim_due_events(
                db,
                now=now,
                claimed_by=self.claimed_by,
                limit=settings.outbox_publish_batch_size,
            )
            await db.commit()
            return events

    async def _mark_published(self, event_id: str) -> None:
        async with self._session_factory() as db:
            await outbox_repository.mark_outbox_event_published(
                db,
                event_id,
                published_at=outbox_repository.utc_now(),
            )
            await db.commit()

    async def _mark_failed(self, event_id: str, error: Exception | str) -> None:
        failed_at = outbox_repository.utc_now()
        next_attempt_at = failed_at + timedelta(seconds=settings.outbox_retry_backoff_seconds)
        async with self._session_factory() as db:
            await outbox_repository.mark_outbox_event_failed(
                db,
                event_id,
                failed_at=failed_at,
                last_error=str(error),
                next_attempt_at=next_attempt_at,
            )
            await db.commit()
