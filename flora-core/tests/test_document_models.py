from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models.document_versions import DocumentVersionRecord
from models.documents import SourceDocumentRecord
from models.sources import SourceRecord


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_document_tables_are_registered_in_metadata() -> None:
    assert "source_documents" in Base.metadata.tables
    assert "document_versions" in Base.metadata.tables


def test_source_document_constraints(db_session) -> None:
    db_session.add(
        SourceRecord(
            id="src_docs",
            name="Docs Source",
            provider_type="obsidian",
            config={"source_path": "/docs"},
        )
    )
    db_session.commit()

    db_session.add(
        SourceDocumentRecord(
            id="doc_1",
            source_id="src_docs",
            external_id="note-1",
            title="First note",
            uri="obsidian://note-1",
            content_hash="abc123",
            last_modified_at=datetime.now(UTC),
            metadata_={"folder": "research"},
        )
    )
    db_session.commit()

    db_session.add(
        SourceDocumentRecord(
            id="doc_2",
            source_id="src_docs",
            external_id="note-1",
            title="Duplicate external id",
            content_hash="def456",
            metadata_={},
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_document_version_constraints(db_session) -> None:
    db_session.add(
        SourceRecord(
            id="src_versions",
            name="Versioned Source",
            provider_type="github",
            config={"source_path": "/repo/docs"},
        )
    )
    db_session.add(
        SourceDocumentRecord(
            id="doc_versions",
            source_id="src_versions",
            external_id="README.md",
            title="Readme",
            content_hash="hash-1",
            metadata_={},
        )
    )
    db_session.commit()

    db_session.add(
        DocumentVersionRecord(
            id="ver_1",
            document_id="doc_versions",
            content_hash="hash-1",
            content="Initial content",
            version_number=1,
            change_type="created",
        )
    )
    db_session.commit()

    db_session.add(
        DocumentVersionRecord(
            id="ver_bad_change",
            document_id="doc_versions",
            content_hash="hash-2",
            content="Changed content",
            version_number=2,
            change_type="unknown",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    db_session.add(
        DocumentVersionRecord(
            id="ver_bad_number",
            document_id="doc_versions",
            content_hash="hash-3",
            content="Changed content",
            version_number=0,
            change_type="updated",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
