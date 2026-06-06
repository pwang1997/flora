from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.sources import SourceCreate, SourceRecord


def list_sources(db: Session) -> list[SourceRecord]:
    result = db.execute(select(SourceRecord).order_by(SourceRecord.name))
    return list(result.scalars().all())


def get_source(db: Session, source_id: str) -> SourceRecord | None:
    result = db.execute(select(SourceRecord).where(SourceRecord.id == source_id))
    return result.scalar_one_or_none()


def get_source_by_path(db: Session, source_path: str) -> SourceRecord | None:
    result = db.execute(
        select(SourceRecord).where(SourceRecord.config["source_path"].as_string() == source_path)
    )
    return result.scalar_one_or_none()


def create_source(db: Session, payload: SourceCreate) -> SourceRecord:
    record = SourceRecord(
        id=f"src_{uuid4().hex[:12]}",
        name=payload.name,
        provider_type=payload.provider_type,
        config=payload.config,
    )
    db.add(record)
    db.flush()
    return record


def delete_source(db: Session, source_id: str) -> bool:
    stmt = delete(SourceRecord).where(SourceRecord.id == source_id)
    result = db.execute(stmt)
    return (result.rowcount or 0) > 0