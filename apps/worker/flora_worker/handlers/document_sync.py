from sqlalchemy.orm import Session

from flora_core.services import AuditService, DocumentService, OutboxService
from flora_shared.enums import EventType
from flora_shared.models import OutboxEventModel, SourceModel
from flora_shared.schemas import DocumentRef
from flora_worker.handlers.connectors import connector_for

audit = AuditService()
documents = DocumentService()
outbox = OutboxService()


async def handle_document_sync(db: Session, event: OutboxEventModel) -> None:
    source = db.get(SourceModel, event.payload["source_id"])
    if not source:
        raise ValueError(f"Source not found: {event.payload['source_id']}")
    ref = DocumentRef(**event.payload["document_ref"])
    connector = connector_for(source.provider_type)
    flora_document = await connector.read_document(ref)
    document, snapshot = documents.upsert_snapshot(db, flora_document)
    outbox.enqueue(
        db,
        EventType.CLAIM_EXTRACTION_REQUESTED,
        "document_snapshot",
        snapshot.id,
        {"document_id": document.id, "snapshot_id": snapshot.id},
    )
    audit.record(
        db,
        "DOCUMENT_SYNCED",
        "document",
        document.id,
        {"snapshot_id": snapshot.id, "content_hash": snapshot.content_hash},
    )
