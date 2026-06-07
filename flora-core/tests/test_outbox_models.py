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
from models.outbox_events import OutboxEventRecord
from models.sources import SourceRecord


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_outbox_table_is_registered_in_metadata() -> None:
    assert "outbox_events" in Base.metadata.tables


def test_outbox_constraints(db_session) -> None:
    db_session.add(
        SourceRecord(
            id="src_outbox",
            name="Outbox Source",
            provider_type="github",
            config={"source_path": "/repo/outbox"},
        )
    )
    db_session.add(
        SourceDocumentRecord(
            id="doc_outbox",
            source_id="src_outbox",
            external_id="README.md",
            title="Readme",
            content_hash="doc-hash",
            metadata_={},
        )
    )
    db_session.add(
        DocumentVersionRecord(
            id="ver_outbox",
            document_id="doc_outbox",
            content_hash="version-hash",
            content="Initial content",
            version_number=1,
            change_type="created",
        )
    )
    db_session.commit()

    db_session.add(
        OutboxEventRecord(
            id="evt_1",
            event_type="document.version.created",
            source_document_id="doc_outbox",
            document_version_id="ver_outbox",
            topic="flora.documents",
            key="doc_outbox",
            idempotency_key="outbox-doc_outbox-ver_outbox-created",
            payload={"document_version_id": "ver_outbox"},
            next_attempt_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    db_session.add(
        OutboxEventRecord(
            id="evt_2",
            event_type="document.version.created",
            source_document_id="doc_outbox",
            document_version_id="ver_outbox",
            topic="flora.documents",
            key="doc_outbox",
            idempotency_key="outbox-doc_outbox-ver_outbox-created",
            payload={"document_version_id": "ver_outbox"},
            next_attempt_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    db_session.add(
        OutboxEventRecord(
            id="evt_3",
            event_type="document.version.failed",
            source_document_id="doc_outbox",
            document_version_id="ver_outbox",
            topic="flora.documents",
            key="doc_outbox",
            idempotency_key="outbox-doc_outbox-ver_outbox-failed",
            payload={"document_version_id": "ver_outbox"},
            status="failed",
            retries=-1,
            next_attempt_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    db_session.add(
        OutboxEventRecord(
            id="evt_4",
            event_type="document.version.retry",
            source_document_id="doc_outbox",
            document_version_id="ver_outbox",
            topic="flora.documents",
            key="doc_outbox",
            idempotency_key="outbox-doc_outbox-ver_outbox-retry",
            payload={"document_version_id": "ver_outbox"},
            status="unknown",
            next_attempt_at=datetime.now(UTC),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
