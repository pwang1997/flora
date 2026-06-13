from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate
from models.documents import SourceDocumentCreate, SourceDocumentUpdate
from models.sources import SourceCreate
from repositories.outbox.outbox_repository import list_outbox_events
from repositories.sources.sources_repository import create_source
from services.documents.document_versions_service import (
    create_document_version,
    get_document_version_by_number,
    list_document_versions,
)
from services.documents.documents_service import (
    create_source_document,
    soft_delete_source_document,
    update_source_document,
)


@pytest.mark.anyio
async def test_create_source_document_requires_parent_source(async_db: AsyncSession) -> None:
    with pytest.raises(HTTPException) as exc_info:
        await create_source_document(
            async_db,
            SourceDocumentCreate(
                source_id="missing-source",
                external_id="doc-1",
                title="Document",
                metadata={},
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "source not found"


@pytest.mark.anyio
async def test_create_source_document_rejects_duplicate_external_id(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Docs Service",
            provider_type="obsidian",
            config={"source_path": "/service/docs"},
        ),
    )
    await async_db.commit()

    await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="doc-1",
            title="Document",
            content="Initial content",
            metadata={},
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_source_document(
            async_db,
            SourceDocumentCreate(
                source_id=source.id,
                external_id="doc-1",
                title="Document 2",
                content="Duplicate content",
                metadata={},
            ),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "source document external_id must be unique within a source"


@pytest.mark.anyio
async def test_update_and_soft_delete_source_document(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Soft Delete Service",
            provider_type="notion",
            config={"source_path": "/service/notion"},
        ),
    )
    await async_db.commit()

    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="page-1",
            title="Original title",
            content="Original content",
            metadata={"source": "notion"},
        ),
    )

    updated = await update_source_document(
        async_db,
        document.id,
        SourceDocumentUpdate(
            title="Updated title",
            last_modified_at=datetime.now(UTC),
        ),
    )
    assert updated.title == "Updated title"

    deleted = await soft_delete_source_document(async_db, document.id)
    assert deleted.status == "deleted"
    assert deleted.last_seen_at is not None

    deleted_again = await soft_delete_source_document(async_db, document.id)
    assert deleted_again.status == "deleted"


@pytest.mark.anyio
async def test_create_document_version_assigns_next_version(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Version Service",
            provider_type="github",
            config={"source_path": "/service/github"},
        ),
    )
    await async_db.commit()

    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="README.md",
            title="Readme",
            content="Document shell content",
            metadata={},
        ),
    )

    version_one = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash-1",
            content="Initial content",
            change_type="created",
        ),
    )
    version_two = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash-2",
            content="Updated content",
            change_type="updated",
        ),
    )

    assert version_one.version_number == 2
    assert version_two.version_number == 3

    fetched = await get_document_version_by_number(async_db, document.id, 3)
    assert fetched is not None
    assert fetched.id == version_two.id

    versions = await list_document_versions(async_db, document.id)
    assert [version.version_number for version in versions] == [1, 2, 3]


@pytest.mark.anyio
async def test_create_source_document_stages_initial_outbox_event(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Document Shell Service",
            provider_type="github",
            config={"source_path": "/service/shells"},
        ),
    )
    await async_db.commit()

    await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="README.md",
            title="Readme",
            content="Initial content",
            metadata={},
        ),
    )

    outbox_events = await list_outbox_events(async_db)
    assert len(outbox_events) == 1
    assert outbox_events[0].payload["content"] == "Initial content"
    assert outbox_events[0].payload["change_type"] == "created"


@pytest.mark.anyio
async def test_create_document_version_requires_parent_document(async_db: AsyncSession) -> None:
    with pytest.raises(HTTPException) as exc_info:
        await create_document_version(
            async_db,
            DocumentVersionCreate(
                document_id="missing-document",
                content_hash="hash-1",
                content="Missing doc content",
                change_type="created",
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "source document not found"
