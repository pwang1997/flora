from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sources import SourceCreate, SourceRecord


async def list_sources(db: AsyncSession) -> list[SourceRecord]:
    result = await db.execute(select(SourceRecord).order_by(SourceRecord.name))
    return list(result.scalars().all())


async def get_source(db: AsyncSession, source_id: str) -> SourceRecord | None:
    result = await db.execute(select(SourceRecord).where(SourceRecord.id == source_id))
    return result.scalar_one_or_none()


async def get_source_by_path(db: AsyncSession, source_path: str) -> SourceRecord | None:
    result = await db.execute(
        select(SourceRecord).where(SourceRecord.config["source_path"].as_string() == source_path)
    )
    return result.scalar_one_or_none()


async def create_source(db: AsyncSession, payload: SourceCreate) -> SourceRecord:
    record = SourceRecord(
        id=f"src_{uuid4().hex[:12]}",
        name=payload.name,
        provider_type=payload.provider_type,
        config=payload.config,
    )
    db.add(record)
    await db.flush()
    return record


async def update_source(db: AsyncSession, source_id: str, updates: dict[str, Any]) -> SourceRecord | None:
    record = await get_source(db, source_id)
    if record is None:
        return None
    for field, value in updates.items():
        setattr(record, field, value)
    await db.flush()
    return record


async def delete_source(db: AsyncSession, source_id: str) -> bool:
    result = await db.execute(delete(SourceRecord).where(SourceRecord.id == source_id))
    return result.rowcount > 0
