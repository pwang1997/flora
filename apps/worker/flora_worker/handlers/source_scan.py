from sqlalchemy.orm import Session

from flora_core.services import AuditService, OutboxService
from flora_shared.enums import EventType, JobStatus
from flora_shared.models import JobModel, OutboxEventModel, SourceModel
from flora_worker.handlers.connectors import connector_for

audit = AuditService()
outbox = OutboxService()


async def handle_source_scan(db: Session, event: OutboxEventModel) -> None:
    source_id = event.payload["source_id"]
    job_id = event.payload.get("job_id")
    source = db.get(SourceModel, source_id)
    if not source:
        raise ValueError(f"Source not found: {source_id}")
    if job_id and (job := db.get(JobModel, job_id)):
        job.status = JobStatus.RUNNING
    connector = connector_for(source.provider_type)
    refs = await connector.list_documents(source.id, source.config)
    for ref in refs:
        outbox.enqueue(
            db,
            EventType.DOCUMENT_SYNC_REQUESTED,
            "document_ref",
            ref.provider_document_id,
            {"source_id": source.id, "document_ref": ref.model_dump(), "job_id": job_id},
        )
    audit.record(db, "SOURCE_SCAN_ENQUEUED_DOCUMENTS", "source", source.id, {"document_count": len(refs)})
