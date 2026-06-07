from flora_shared import DocumentIngestionEventPayload, document_version_event_type
import repositories.outbox.outbox_repository as outbox_repository
from config import settings
from models.document_versions import DocumentVersionRecord
from models.documents import SourceDocumentRecord
from models.outbox_events import OutboxEventCreate, OutboxEventRecord


def build_document_ingestion_event(
    *,
    document: SourceDocumentRecord,
    version: DocumentVersionRecord,
) -> OutboxEventCreate:
    event_type = document_version_event_type(version.change_type)
    payload = DocumentIngestionEventPayload(
        event_type=event_type,
        source_document_id=document.id,
        document_version_id=version.id,
        source_id=document.source_id,
        version_number=version.version_number,
        change_type=version.change_type,
        content_hash=version.content_hash,
        content=version.content,
        title=document.title,
        uri=document.uri,
        metadata=document.metadata_,
        occurred_at=version.created_at,
    )
    return OutboxEventCreate(
        event_type=event_type,
        source_document_id=document.id,
        document_version_id=version.id,
        topic=settings.kafka_documents_topic,
        key=document.id,
        idempotency_key=f"{document.id}:{version.id}:{version.change_type}",
        payload=payload,
    )


async def create_document_ingestion_event(
    db,
    *,
    document: SourceDocumentRecord,
    version: DocumentVersionRecord,
) -> OutboxEventRecord:
    return await outbox_repository.create_outbox_event(
        db,
        build_document_ingestion_event(document=document, version=version),
    )
