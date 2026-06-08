import repositories.documents.document_versions_repository as document_versions_repository
import repositories.documents.documents_repository as documents_repository
import services.outbox.outbox_service as outbox_service
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate, DocumentVersionRecord


async def list_document_versions(db: AsyncSession, document_id: str) -> list[DocumentVersionRecord]:
    return await document_versions_repository.list_document_versions(db, document_id)


async def get_document_version(db: AsyncSession, version_id: str) -> DocumentVersionRecord | None:
    return await document_versions_repository.get_document_version(db, version_id)


async def get_document_version_by_number(
    db: AsyncSession, document_id: str, version_number: int
) -> DocumentVersionRecord | None:
    return await documents_repository.get_document_version_by_number(db, document_id, version_number)


async def create_document_version(db: AsyncSession, payload: DocumentVersionCreate) -> DocumentVersionRecord:
    document = await documents_repository.get_source_document(db, payload.document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source document not found")

    next_version_number = await documents_repository.get_latest_version_number(db, payload.document_id) + 1
    record = await documents_repository.create_document_version(db, payload, next_version_number)
    await outbox_service.create_document_ingestion_event(
        db,
        document=document,
        version=record,
    )
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="document version content_hash must be unique within a document",
        ) from exc
    await db.refresh(record)
    return record
