from pydantic import ConfigDict
from utils.time_utils import utc_now

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


SourceDocumentStatus = Literal["active", "deleted"]


class SourceDocumentCreate(BaseModel):
    source_id: str
    external_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    uri: str | None = None
    last_modified_at: datetime | None = None
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = ConfigDict(extra="allow")


class SourceDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    uri: str | None = None
    last_modified_at: datetime | None = None
    status: SourceDocumentStatus | None = None
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata")
    last_seen_at: datetime | None = None
    
    model_config = ConfigDict(extra="allow")


class SourceDocument(SourceDocumentCreate):
    id: str
    status: SourceDocumentStatus = "active"
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime


def serialize_source_document(record: "SourceDocumentRecord") -> SourceDocument:
    return SourceDocument(
        id=record.id,
        source_id=record.source_id,
        external_id=record.external_id,
        title=record.title,
        uri=record.uri,
        last_modified_at=record.last_modified_at,
        metadata=record.metadata_,
        status=record.status,
        first_seen_at=record.first_seen_at,
        last_seen_at=record.last_seen_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


class SourceDocumentRecord(Base):
    __tablename__ = "source_documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    source_id: Mapped[str] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    external_id: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    uri: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    last_modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_documents_source_external_id"),
        CheckConstraint("length(trim(external_id)) > 0", name="ck_source_documents_external_id_not_blank"),
        CheckConstraint("length(trim(title)) > 0", name="ck_source_documents_title_not_blank"),
        CheckConstraint(
            "status IN ('active', 'deleted')",
            name="ck_source_documents_status_valid",
        ),
    )
