from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from flora_api.database import get_db
from flora_core.services import AuditService, OutboxService, new_id
from flora_shared.enums import EventType, JobStatus
from flora_shared.models import JobModel, SourceModel
from flora_shared.schemas import Job, Source, SourceCreate

router = APIRouter(tags=["sources"])
audit = AuditService()
outbox = OutboxService()


@router.post("/sources", response_model=Source)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> SourceModel:
    source = SourceModel(
        id=new_id(),
        name=payload.name,
        provider_type=payload.provider_type,
        config=payload.config,
        status="active",
    )
    db.add(source)
    audit.record(db, "SOURCE_CREATED", "source", source.id, {"name": source.name})
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources", response_model=list[Source])
def list_sources(db: Session = Depends(get_db)) -> list[SourceModel]:
    return db.query(SourceModel).order_by(SourceModel.created_at.desc()).all()


@router.post("/sources/{source_id}/scan", response_model=Job)
def scan_source(source_id: str, db: Session = Depends(get_db)) -> JobModel:
    source = db.get(SourceModel, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    job = JobModel(id=new_id(), source_id=source.id, job_type="source_scan", status=JobStatus.PENDING)
    db.add(job)
    outbox.enqueue(
        db,
        EventType.SOURCE_SCAN_REQUESTED,
        "source",
        source.id,
        {"source_id": source.id, "job_id": job.id},
    )
    audit.record(db, "SOURCE_SCAN_REQUESTED", "source", source.id, {"job_id": job.id})
    db.commit()
    db.refresh(job)
    return job
