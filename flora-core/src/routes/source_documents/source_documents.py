import logging

import services.documents.documents_service as documents_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from decorators import logging_wrapper
from models.documents import (
    SourceDocument,
    SourceDocumentCreate,
    SourceDocumentUpdate,
    serialize_source_document,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/source-documents", tags=["source-documents"])


@router.get("/list", response_model=list[SourceDocument])
@logging_wrapper
async def list_source_documents(source_id: str, db: AsyncSession = Depends(get_db)) -> list[SourceDocument]:
    records = await documents_service.list_source_documents(db, source_id)
    return [serialize_source_document(record) for record in records]


@router.get("/get/{document_id}", response_model=SourceDocument)
@logging_wrapper
async def get_source_document(document_id: str, db: AsyncSession = Depends(get_db)) -> SourceDocument:
    record = await documents_service.get_source_document(db, document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="source document not found")
    return serialize_source_document(record)


@router.post("/create", response_model=SourceDocument, status_code=status.HTTP_201_CREATED)
@logging_wrapper
async def create_source_document(
    payload: SourceDocumentCreate,
    db: AsyncSession = Depends(get_db),
) -> SourceDocument:
    record = await documents_service.create_source_document(db, payload)
    return serialize_source_document(record)


@router.patch("/update/{document_id}", response_model=SourceDocument)
@logging_wrapper
async def update_source_document(
    document_id: str,
    payload: SourceDocumentUpdate,
    db: AsyncSession = Depends(get_db),
) -> SourceDocument:
    record = await documents_service.update_source_document(db, document_id, payload)
    return serialize_source_document(record)


@router.delete("/delete/{document_id}", response_model=SourceDocument)
@logging_wrapper
async def delete_source_document(document_id: str, db: AsyncSession = Depends(get_db)) -> SourceDocument:
    record = await documents_service.soft_delete_source_document(db, document_id)
    return serialize_source_document(record)
