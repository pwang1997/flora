from models.document_versions import DocumentVersionCreate, DocumentVersionRecord
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4


async def list_document_versions(db: AsyncSession, document_id: str) -> list[DocumentVersionRecord]:
    result = await db.execute(
        select(DocumentVersionRecord)
        .where(DocumentVersionRecord.document_id == document_id, DocumentVersionRecord.change_type != "deleted")
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


async def get_latest_document_version(db: AsyncSession, document_id: str) -> DocumentVersionRecord | None:
    result = await db.execute(
        select(DocumentVersionRecord)
        .where(DocumentVersionRecord.document_id == document_id, DocumentVersionRecord.change_type != "deleted")
        .order_by(desc(DocumentVersionRecord.version_number))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_version_number(db: AsyncSession, document_id: str) -> int:
    result = await db.execute(
        select(func.max(DocumentVersionRecord.version_number)).where(
            DocumentVersionRecord.document_id == document_id,
            DocumentVersionRecord.change_type != "deleted"
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
