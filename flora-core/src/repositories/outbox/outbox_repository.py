from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.outbox_events import OutboxEventCreate, OutboxEventRecord


async def create_outbox_event(db: AsyncSession, payload: OutboxEventCreate) -> OutboxEventRecord:
    record = OutboxEventRecord(
        id=f"evt_{uuid4().hex[:12]}",
        event_type=payload.event_type,
        source_document_id=payload.source_document_id,
        document_version_id=payload.document_version_id,
        topic=payload.topic,
        key=payload.key,
        idempotency_key=payload.idempotency_key,
        payload=payload.payload.model_dump(mode="json"),
        next_attempt_at=payload.next_attempt_at,
    )
    db.add(record)
    await db.flush()
    return record


async def get_outbox_event(db: AsyncSession, event_id: str) -> OutboxEventRecord | None:
    result = await db.execute(select(OutboxEventRecord).where(OutboxEventRecord.id == event_id))
    return result.scalar_one_or_none()


async def list_outbox_events(db: AsyncSession) -> list[OutboxEventRecord]:
    result = await db.execute(select(OutboxEventRecord).order_by(OutboxEventRecord.created_at))
    return list(result.scalars().all())
