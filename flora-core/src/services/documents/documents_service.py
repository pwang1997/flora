from datetime import UTC, datetime

import repositories.documents.documents_repository as documents_repository
import repositories.sources.sources_repository as sources_repository
import services.outbox.outbox_service as outbox_service
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate, DocumentVersionRecord
from models.documents import SourceDocumentCreate, SourceDocumentRecord, SourceDocumentUpdate


async def list_source_documents(db: AsyncSession, source_id: str) -> list[SourceDocumentRecord]:
    return await documents_repository.list_source_documents(db, source_id)


async def get_source_document(db: AsyncSession, document_id: str) -> SourceDocumentRecord | None:
    return await documents_repository.get_source_document(db, document_id)


async def get_source_document_by_external_id(
    db: AsyncSession, source_id: str, external_id: str
) -> SourceDocumentRecord | None:
    return await documents_repository.get_source_document_by_external_id(db, source_id, external_id)


async def create_source_document(db: AsyncSession, payload: SourceDocumentCreate) -> SourceDocumentRecord:
    source = await sources_repository.get_source(db, payload.source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source not found")

    existing_document = await documents_repository.get_source_document_by_external_id(
        db, payload.source_id, payload.external_id
    )
    if existing_document is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="source document external_id must be unique within a source",
        )

    record = await documents_repository.create_source_document(db, payload)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="source document external_id must be unique within a source",
        ) from exc
    await db.refresh(record)
    return record


async def update_source_document(
    db: AsyncSession, document_id: str, payload: SourceDocumentUpdate
) -> SourceDocumentRecord:
    record = await documents_repository.update_source_document(db, document_id, payload)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source document not found")
    await db.commit()
    await db.refresh(record)
    return record


async def soft_delete_source_document(db: AsyncSession, document_id: str) -> SourceDocumentRecord:
    record = await documents_repository.get_source_document(db, document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source document not found")

    if record.status != "deleted":
        update_payload = SourceDocumentUpdate(
            status="deleted",
            last_seen_at=datetime.now(UTC),
        )
        record = await documents_repository.update_source_document(db, document_id, update_payload)
    await db.commit()
    await db.refresh(record)
    return record