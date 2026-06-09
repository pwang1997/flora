from uuid import uuid4

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate, DocumentVersionRecord
from models.documents import SourceDocumentCreate, SourceDocumentRecord, SourceDocumentUpdate


async def list_source_documents(db: AsyncSession, source_id: str) -> list[SourceDocumentRecord]:
    result = await db.execute(
        select(SourceDocumentRecord)
        .where(SourceDocumentRecord.source_id == source_id)
        .order_by(SourceDocumentRecord.title, SourceDocumentRecord.id)
    )
    return list(result.scalars().all())


async def get_source_document(db: AsyncSession, document_id: str) -> SourceDocumentRecord | None:
    result = await db.execute(select(SourceDocumentRecord).where(SourceDocumentRecord.id == document_id))
    return result.scalar_one_or_none()


async def get_source_document_by_external_id(
    db: AsyncSession, source_id: str, external_id: str
) -> SourceDocumentRecord | None:
    result = await db.execute(
        select(SourceDocumentRecord).where(
            SourceDocumentRecord.source_id == source_id,
            SourceDocumentRecord.external_id == external_id,
        )
    )
    return result.scalar_one_or_none()


async def create_source_document(db: AsyncSession, payload: SourceDocumentCreate) -> SourceDocumentRecord:
    record = SourceDocumentRecord(
        id=f"doc_{uuid4().hex[:12]}",
        source_id=payload.source_id,
        external_id=payload.external_id,
        title=payload.title,
        uri=payload.uri,
        last_modified_at=payload.last_modified_at,
        metadata_=payload.metadata_,
    )
    db.add(record)
    await db.flush()
    return record


async def update_source_document(
    db: AsyncSession, document_id: str, payload: SourceDocumentUpdate
) -> SourceDocumentRecord | None:
    record = await get_source_document(db, document_id)
    if record is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(record, field, value)
    await db.flush()
    return record