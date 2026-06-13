from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.document_versions import DocumentVersionCreate
from models.documents import SourceDocumentCreate, SourceDocumentUpdate
from models.sources import SourceCreate
from repositories.documents.document_versions_repository import (
    create_document_version,
    get_document_version,
    get_document_version_by_number,
    get_latest_document_version,
    get_latest_version_number,
    list_document_versions,
)
from repositories.documents.documents_repository import (
    create_source_document,
    get_source_document,
    get_source_document_by_external_id,
    list_source_documents,
    update_source_document,
)
from repositories.sources.sources_repository import create_source


@pytest.mark.anyio
async def test_source_document_repository_crud(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Docs Repo",
            provider_type="obsidian",
            config={"source_path": "/docs/repo"},
        ),
    )
    await async_db.commit()

    created = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="note-1",
            title="Alpha note",
            uri="obsidian://note-1",
            last_modified_at=datetime.now(UTC),
            metadata={"folder": "alpha"},
        ),
    )
    await async_db.commit()

    fetched = await get_source_document(async_db, created.id)
    assert fetched is not None
    assert fetched.external_id == "note-1"

    fetched_by_external = await get_source_document_by_external_id(async_db, source.id, "note-1")
    assert fetched_by_external is not None
    assert fetched_by_external.id == created.id

    updated = await update_source_document(
        async_db,
        created.id,
        SourceDocumentUpdate(title="Updated note"),
    )
    await async_db.commit()
    assert updated is not None
    assert updated.title == "Updated note"

    listed = await list_source_documents(async_db, source.id)
    assert [document.id for document in listed] == [created.id]


@pytest.mark.anyio
async def test_source_document_repository_enforces_unique_external_id(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Duplicate Repo",
            provider_type="obsidian",
            config={"source_path": "/docs/duplicate"},
        ),
    )
    await async_db.commit()

    await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="same-id",
            title="First",
            metadata={},
        ),
    )
    await async_db.commit()

    with pytest.raises(IntegrityError):
        await create_source_document(
            async_db,
            SourceDocumentCreate(
                source_id=source.id,
                external_id="same-id",
                title="Second",
                metadata={},
            ),
        )
    await async_db.rollback()


@pytest.mark.anyio
async def test_document_version_repository_create_and_list(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Version Repo",
            provider_type="github",
            config={"source_path": "/repo/docs"},
        ),
    )
    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="README.md",
            title="Readme",
            metadata={},
        ),
    )
    await async_db.commit()

    version_one = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash-1",
            content="Initial content",
            change_type="created",
        ),
        1,
    )
    version_two = await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="version-hash-2",
            content="Updated content",
            change_type="updated",
        ),
        2,
    )
    await async_db.commit()

    assert await get_latest_version_number(async_db, document.id) == 2

    fetched = await get_document_version(async_db, version_one.id)
    assert fetched is not None
    assert fetched.version_number == 1

    fetched_by_number = await get_document_version_by_number(async_db, document.id, 2)
    assert fetched_by_number is not None
    assert fetched_by_number.id == version_two.id

    listed = await list_document_versions(async_db, document.id)
    assert [version.version_number for version in listed] == [1, 2]

    latest = await get_latest_document_version(async_db, document.id)
    assert latest is not None
    assert latest.id == version_two.id
    assert latest.content_hash == "version-hash-2"


@pytest.mark.anyio
async def test_document_version_repository_enforces_unique_content_hash(async_db: AsyncSession) -> None:
    source = await create_source(
        async_db,
        SourceCreate(
            name="Version Duplicate Repo",
            provider_type="github",
            config={"source_path": "/repo/duplicate"},
        ),
    )
    document = await create_source_document(
        async_db,
        SourceDocumentCreate(
            source_id=source.id,
            external_id="guide.md",
            title="Guide",
            metadata={},
        ),
    )
    await async_db.commit()

    await create_document_version(
        async_db,
        DocumentVersionCreate(
            document_id=document.id,
            content_hash="same-hash",
            content="Initial content",
            change_type="created",
        ),
        1,
    )
    await async_db.commit()

    with pytest.raises(IntegrityError):
        await create_document_version(
            async_db,
            DocumentVersionCreate(
                document_id=document.id,
                content_hash="same-hash",
                content="Changed content",
                change_type="updated",
            ),
            2,
        )
    await async_db.rollback()
