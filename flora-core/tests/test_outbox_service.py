import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate
from models.sources import SourceCreate
from models.documents import SourceDocumentCreate
from repositories.outbox.outbox_repository import list_outbox_events
from repositories.sources.sources_repository import create_source
from services.documents.documents_service import create_document_version, create_source_document
from services.outbox.outbox_service import build_document_ingestion_event


@pytest.mark.anyio
async def test_build_document_ingestion_event_serializes_expected_payload(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(name="Payload Source", provider_type="github", config={"source_path": "/payload"}),
    )
    await async_db.commit()
    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="README.md",
            title="Readme",
            content_hash="doc-hash",
            metadata={"folder": "docs"},
        ),
    )
    version = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash",
            content="Initial content",
            change_type="created",
        ),
    )

    event = build_document_ingestion_event(document=document, version=version)
    payload = event.payload
    assert payload.source_document_id == document.id
    assert payload.document_version_id == version.id
    assert payload.source_id == source.id
    assert payload.version_number == 1
    assert payload.content == "Initial content"
    assert event.key == document.id


@pytest.mark.anyio
async def test_create_document_version_stages_outbox_event_in_same_transaction(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(name="Version Source", provider_type="github", config={"source_path": "/versions"}),
    )
    await async_db.commit()
    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="guide.md",
            title="Guide",
            content_hash="doc-hash",
            metadata={},
        ),
    )

    version = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash",
            content="Document content",
            change_type="updated",
        ),
    )

    outbox_events = await list_outbox_events(async_db)
    assert len(outbox_events) == 1
    assert outbox_events[0].document_version_id == version.id
    assert outbox_events[0].key == document.id
    assert outbox_events[0].payload["content_hash"] == "version-hash"
    assert outbox_events[0].payload["change_type"] == "updated"
