import repositories.sources.sources_repository as sources_repository
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.sources import SourceCreate, SourceRecord


async def list_sources(db: AsyncSession) -> list[SourceRecord]:
    return await sources_repository.list_sources(db)


async def create_source(db: AsyncSession, payload: SourceCreate) -> SourceRecord:
    existing_source = await sources_repository.get_source_by_path(db, payload.config["source_path"])
    if existing_source is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="config.source_path must be unique",
        )

    record = await sources_repository.create_source(db, payload)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="config.source_path must be unique",
        ) from exc
    await db.refresh(record)
    return record


async def delete_source(db: AsyncSession, source_id: str) -> bool:
    deleted = await sources_repository.delete_source(db, source_id)
    await db.commit()
    return deleted


async def get_source(db: AsyncSession, source_id: str) -> SourceRecord | None:
    return await sources_repository.get_source(db, source_id)


async def get_source_by_path(db: AsyncSession, source_path: str) -> SourceRecord | None:
    return await sources_repository.get_source_by_path(db, source_path)
