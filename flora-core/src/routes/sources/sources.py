import services.sources.sources_service as sources_service
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from decorators import logging_wrapper
from models.sources import Source, SourceCreate, SourceDelete, serialize_source

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/v1/sources", tags=["sources"])


@router.get("/list", response_model=list[Source])
@logging_wrapper
def list_sources(db: Session = Depends(get_db)) -> list[Source]:
    return sources_service.list_sources(db)


@router.post("/create", response_model=Source, status_code=status.HTTP_201_CREATED)
@logging_wrapper
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> Source:
    record = sources_service.create_source(db, payload)
    return serialize_source(record)


@router.delete("/delete", response_model=bool)
@logging_wrapper
def delete_source(payload: SourceDelete, db: Session = Depends(get_db)) -> bool:
    return sources_service.delete_source(db, payload.id)
