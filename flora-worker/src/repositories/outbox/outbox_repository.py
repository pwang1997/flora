from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, String, Table, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

metadata = MetaData()

outbox_events = Table(
    "outbox_events",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("event_type", String(64), nullable=False),
    Column("source_document_id", String, nullable=False),
    Column("document_version_id", String, nullable=False),
    Column("topic", String(255), nullable=False),
    Column("key", String(255), nullable=False),
    Column("idempotency_key", String(255), nullable=False, unique=True),
    Column("payload", JSON, nullable=False),
    Column("status", String(32), nullable=False, default="pending"),
    Column("retries", Integer, nullable=False, default=0),
    Column("last_error", String, nullable=True),
    Column("last_attempt_at", DateTime(timezone=True), nullable=True),
    Column("next_attempt_at", DateTime(timezone=True), nullable=False),
    Column("claimed_at", DateTime(timezone=True), nullable=True),
    Column("claimed_by", String(255), nullable=True),
    Column("published_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class OutboxEvent:
    id: str
    event_type: str
    source_document_id: str
    document_version_id: str
    topic: str
    key: str
    idempotency_key: str
    payload: dict[str, Any]
    status: str
    retries: int
    last_error: str | None
    last_attempt_at: datetime | None
    next_attempt_at: datetime
    claimed_at: datetime | None
    claimed_by: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def _event_from_row(row) -> OutboxEvent:
    mapping = row._mapping
    return OutboxEvent(**{column.name: mapping[column.name] for column in outbox_events.columns})


async def list_outbox_events(db: AsyncSession) -> list[OutboxEvent]:
    result = await db.execute(select(outbox_events).order_by(outbox_events.c.created_at))
    return [_event_from_row(row) for row in result.all()]


async def release_stale_claims(db: AsyncSession, claimed_before: datetime) -> list[OutboxEvent]:
    result = await db.execute(
        select(outbox_events).where(
            outbox_events.c.status == "publishing",
            outbox_events.c.claimed_at.is_not(None),
            outbox_events.c.claimed_at < claimed_before,
        )
    )
    records = [_event_from_row(row) for row in result.all()]
    if records:
        await db.execute(
            update(outbox_events)
            .where(outbox_events.c.id.in_([record.id for record in records]))
            .values(status="pending", claimed_at=None, claimed_by=None, updated_at=utc_now())
        )
        await db.flush()
    return records


async def claim_due_events(
    db: AsyncSession,
    *,
    now: datetime,
    claimed_by: str,
    limit: int,
) -> list[OutboxEvent]:
    result = await db.execute(
        select(outbox_events)
        .where(
            outbox_events.c.status.in_(("pending", "failed")),
            outbox_events.c.next_attempt_at <= now,
            or_(outbox_events.c.claimed_at.is_(None), outbox_events.c.claimed_by == claimed_by),
        )
        .order_by(outbox_events.c.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    records = [_event_from_row(row) for row in result.all()]
    if records:
        await db.execute(
            update(outbox_events)
            .where(outbox_events.c.id.in_([record.id for record in records]))
            .values(
                status="publishing",
                claimed_at=now,
                claimed_by=claimed_by,
                last_attempt_at=now,
                updated_at=now,
            )
        )
        await db.flush()
    return [
        replace(
            record,
            status="publishing",
            claimed_at=now,
            claimed_by=claimed_by,
            last_attempt_at=now,
            updated_at=now,
        )
        for record in records
    ]


async def mark_outbox_event_published(
    db: AsyncSession,
    event_id: str,
    *,
    published_at: datetime,
) -> OutboxEvent | None:
    await db.execute(
        update(outbox_events)
        .where(outbox_events.c.id == event_id)
        .values(
            status="published",
            published_at=published_at,
            claimed_at=None,
            claimed_by=None,
            last_error=None,
            updated_at=published_at,
        )
    )
    await db.flush()
    return await get_outbox_event(db, event_id)


async def mark_outbox_event_failed(
    db: AsyncSession,
    event_id: str,
    *,
    failed_at: datetime,
    last_error: str,
    next_attempt_at: datetime,
) -> OutboxEvent | None:
    current = await get_outbox_event(db, event_id)
    if current is None:
        return None
    await db.execute(
        update(outbox_events)
        .where(outbox_events.c.id == event_id)
        .values(
            status="failed",
            retries=current.retries + 1,
            last_error=last_error,
            last_attempt_at=failed_at,
            next_attempt_at=next_attempt_at,
            claimed_at=None,
            claimed_by=None,
            updated_at=failed_at,
        )
    )
    await db.flush()
    return await get_outbox_event(db, event_id)


async def get_outbox_event(db: AsyncSession, event_id: str) -> OutboxEvent | None:
    result = await db.execute(select(outbox_events).where(outbox_events.c.id == event_id))
    row = result.first()
    return _event_from_row(row) if row is not None else None
