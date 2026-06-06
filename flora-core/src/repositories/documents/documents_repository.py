from uuid import uuid4

from sqlalchemy import func, select
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
        content_hash=payload.content_hash,
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


async def list_document_versions(db: AsyncSession, document_id: str) -> list[DocumentVersionRecord]:
    result = await db.execute(
        select(DocumentVersionRecord)
        .where(DocumentVersionRecord.document_id == document_id)
        .order_by(DocumentVersionRecord.version_number)
    )
    return list(result.scalars().all())


async def get_document_version(db: AsyncSession, version_id: str) -> DocumentVersionRecord | None:
    result = await db.execute(select(DocumentVersionRecord).where(DocumentVersionRecord.id == version_id))
    return result.scalar_one_or_none()


async def get_document_version_by_number(
    db: AsyncSession, document_id: str, version_number: int
) -> DocumentVersionRecord | None:
    result = await db.execute(
        select(DocumentVersionRecord).where(
            DocumentVersionRecord.document_id == document_id,
            DocumentVersionRecord.version_number == version_number,
        )
    )
    return result.scalar_one_or_none()


async def get_latest_version_number(db: AsyncSession, document_id: str) -> int:
    result = await db.execute(
        select(func.max(DocumentVersionRecord.version_number)).where(
            DocumentVersionRecord.document_id == document_id
        )
    )
    return result.scalar_one() or 0


async def create_document_version(
    db: AsyncSession, payload: DocumentVersionCreate, version_number: int
) -> DocumentVersionRecord:
    record = DocumentVersionRecord(
        id=f"ver_{uuid4().hex[:12]}",
        document_id=payload.document_id,
        content_hash=payload.content_hash,
        content=payload.content,
        version_number=version_number,
        change_type=payload.change_type,
    )
    db.add(record)
    await db.flush()
    return record
