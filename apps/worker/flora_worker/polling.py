from __future__ import annotations

import asyncio
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from flora_api.database import SessionLocal
from flora_core.services import utcnow
from flora_shared.enums import EventType, OutboxStatus
from flora_shared.models import OutboxEventModel
from flora_worker.handlers import (
    handle_claim_extraction,
    handle_claim_verification,
    handle_document_sync,
    handle_patch_application,
    handle_patch_generation,
    handle_source_scan,
)


class Worker:
    def __init__(self, worker_id: str, batch_size: int = 10, poll_interval_seconds: float = 2.0) -> None:
        self.worker_id = worker_id
        self.batch_size = batch_size
        self.poll_interval_seconds = poll_interval_seconds

    async def run_forever(self) -> None:
        while True:
            processed = await self.run_once()
            if processed == 0:
                await asyncio.sleep(self.poll_interval_seconds)

    async def run_once(self) -> int:
        with SessionLocal() as db:
            events = self.claim_events(db)
            for event in events:
                await self.process_event(db, event)
            db.commit()
            return len(events)

    def claim_events(self, db: Session) -> list[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(
                OutboxEventModel.status == OutboxStatus.PENDING,
                OutboxEventModel.available_at <= utcnow(),
            )
            .order_by(OutboxEventModel.created_at)
            .limit(self.batch_size)
        )
        if db.bind and db.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update(skip_locked=True)
        events = list(db.scalars(stmt).all())
        for event in events:
            event.status = OutboxStatus.PROCESSING
            event.locked_at = utcnow()
            event.locked_by = self.worker_id
            event.attempts += 1
        db.flush()
        return events

    async def process_event(self, db: Session, event: OutboxEventModel) -> None:
        try:
            handler = EVENT_HANDLERS[EventType(event.event_type)]
            await handler(db, event)
            event.status = OutboxStatus.PROCESSED
            event.processed_at = utcnow()
            event.error = None
        except Exception as exc:  # noqa: BLE001 - preserve event failure details.
            event.status = OutboxStatus.PENDING if event.attempts < 3 else OutboxStatus.FAILED
            event.available_at = utcnow() + timedelta(seconds=min(60, 2**event.attempts))
            event.error = str(exc)


EVENT_HANDLERS = {
    EventType.SOURCE_SCAN_REQUESTED: handle_source_scan,
    EventType.DOCUMENT_SYNC_REQUESTED: handle_document_sync,
    EventType.CLAIM_EXTRACTION_REQUESTED: handle_claim_extraction,
    EventType.CLAIM_VERIFICATION_REQUESTED: handle_claim_verification,
    EventType.PATCH_GENERATION_REQUESTED: handle_patch_generation,
    EventType.PATCH_APPLICATION_REQUESTED: handle_patch_application,
}
