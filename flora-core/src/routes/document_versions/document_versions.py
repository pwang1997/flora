import logging

import services.documents.document_versions_service as document_versions_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from decorators import logging_wrapper
from models.document_versions import DocumentVersion, DocumentVersionCreate, serialize_document_version

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/document-versions", tags=["document-versions"])


@router.get("/list", response_model=list[DocumentVersion])
@logging_wrapper
async def list_document_versions(document_id: str, db: AsyncSession = Depends(get_db)) -> list[DocumentVersion]:
    records = await document_versions_service.list_document_versions(db, document_id)
    return [serialize_document_version(record) for record in records]


@router.get("/get/{version_id}", response_model=DocumentVersion)
@logging_wrapper
async def get_document_version(version_id: str, db: AsyncSession = Depends(get_db)) -> DocumentVersion:
    record = await document_versions_service.get_document_version(db, version_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document version not found")
    return serialize_document_version(record)


@router.get("/latest/{document_id}", response_model=DocumentVersion)
@logging_wrapper
async def get_latest_document_version(document_id: str, db: AsyncSession = Depends(get_db)) -> DocumentVersion:
    record = await document_versions_service.get_latest_document_version(db, document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document version not found")
    return serialize_document_version(record)


@router.post("/create", response_model=DocumentVersion, status_code=status.HTTP_201_CREATED)
@logging_wrapper
async def create_document_version(
    payload: DocumentVersionCreate,
    db: AsyncSession = Depends(get_db),
) -> DocumentVersion:
    record = await document_versions_service.create_document_version(db, payload)
    return serialize_document_version(record)
