from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from utils.time_utils import utc_now

OutboxEventStatus = Literal["pending", "publishing", "published", "failed"]


class OutboxEventCreate(BaseModel):
    event_type: str = Field(..., min_length=1)
    source_document_id: str
    document_version_id: str
    topic: str = Field(..., min_length=1)
    key: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    next_attempt_at: datetime = Field(default_factory=utc_now)


class OutboxEventRecord(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    event_type: Mapped[str] = mapped_column(String(64), nullable=False)

    source_document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id"),
        nullable=False,
        index=True,
    )

    document_version_id: Mapped[str] = mapped_column(
        ForeignKey("document_versions.id"),
        nullable=False,
        index=True,
    )

    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    retries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(String, nullable=True)

    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    claimed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'publishing', 'published', 'failed')",
            name="ck_outbox_events_status_valid",
        ),
        CheckConstraint("retries >= 0", name="ck_outbox_events_retries_non_negative"),
        CheckConstraint("length(trim(event_type)) > 0", name="ck_outbox_events_event_type_not_blank"),
        CheckConstraint("length(trim(topic)) > 0", name="ck_outbox_events_topic_not_blank"),
        CheckConstraint("length(trim(key)) > 0", name="ck_outbox_events_key_not_blank"),
        CheckConstraint(
            "length(trim(idempotency_key)) > 0",
            name="ck_outbox_events_idempotency_key_not_blank",
        ),
        Index(
            "ix_outbox_events_status_next_attempt_created",
            "status",
            "next_attempt_at",
            "created_at",
        ),
        Index(
            "ix_outbox_events_source_document_status",
            "source_document_id",
            "status",
        ),
    )
