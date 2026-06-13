from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from utils.time_utils import utc_now


DocumentChangeType = Literal["created", "updated", "deleted", "restored"]


class DocumentVersionCreate(BaseModel):
    document_id: str
    content_hash: str = Field(...)
    content: str = Field(..., min_length=1)
    change_type: DocumentChangeType = "created"


class DocumentVersion(DocumentVersionCreate):
    id: str
    version_number: int
    created_at: datetime


def serialize_document_version(record: "DocumentVersionRecord") -> DocumentVersion:
    return DocumentVersion(
        id=record.id,
        document_id=record.document_id,
        content_hash=record.content_hash,
        content=record.content,
        change_type=record.change_type,
        version_number=record.version_number,
        created_at=record.created_at,
    )


class DocumentVersionRecord(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    change_type: Mapped[str] = mapped_column(String(32), nullable=False, default="created")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("document_id", "content_hash", name="uq_document_versions_document_hash"),
        UniqueConstraint("document_id", "version_number", name="uq_document_versions_document_version"),
        CheckConstraint("length(trim(content_hash)) > 0", name="ck_document_versions_content_hash_not_blank"),
        CheckConstraint("length(trim(content)) > 0", name="ck_document_versions_content_not_blank"),
        CheckConstraint("version_number > 0", name="ck_document_versions_version_number_positive"),
        CheckConstraint(
            "change_type IN ('created', 'updated', 'deleted', 'restored')",
            name="ck_document_versions_change_type_valid",
        ),
    )
