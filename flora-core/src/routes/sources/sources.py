from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models.sources import Source, SourceCreate, SourceRecord, serialize_source

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/v1/sources", tags=["sources"])


@router.get("/list", response_model=list[Source], include_in_schema=False)
@router.get("", response_model=list[Source])
def list_sources(db: Session = Depends(get_db)) -> list[Source]:
    logger.debug("sources.list.start")
    records = db.scalars(select(SourceRecord).order_by(SourceRecord.name)).all()
    sources = [serialize_source(record) for record in records]
    logger.debug(
        "sources.list.completed",
        extra={
            "data_state": {
                "changed": False,
                "returned_count": len(sources),
            }
        },
    )
    return sources


@router.post("/create", response_model=Source, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("", response_model=Source, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> Source:
    logger.debug(
        "sources.create.start",
        extra={
            "source_request": {
                "name": payload.name,
                "provider_type": payload.provider_type,
            }
        },
    )
    source_path = payload.config["source_path"]
    existing_source_id = db.scalar(
        select(SourceRecord.id)
        .where(SourceRecord.config["source_path"].as_string() == source_path)
        .limit(1)
    )
    if existing_source_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="config.source_path must be unique",
        )

    before_count = db.scalar(select(func.count()).select_from(SourceRecord)) or 0
    record = SourceRecord(id=f"src_{uuid4().hex[:12]}", **payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="config.source_path must be unique",
        ) from exc
    db.refresh(record)
    source = serialize_source(record)
    after_count = db.scalar(select(func.count()).select_from(SourceRecord)) or 0
    logger.debug(
        "sources.create.completed",
        extra={
            "data_state": {
                "changed": True,
                "before_count": before_count,
                "after_count": after_count,
                "created_source_id": source.id,
                "created_source_status": source.status,
            }
        },
    )
    return source
