from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import DateTime, Index, JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

ProviderType = Literal["local_markdown", "obsidian"]
SourceStatus = Literal["active", "paused"]


def utc_now() -> datetime:
    return datetime.now(UTC)


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    provider_type: ProviderType
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("config")
    @classmethod
    def validate_source_path(cls, config: dict[str, Any]) -> dict[str, Any]:
        source_path = config.get("source_path")
        if not isinstance(source_path, str) or not source_path.strip():
            raise ValueError("config.source_path is required")
        return config


class Source(SourceCreate):
    id: str
    status: SourceStatus = "active"
    document_count: int = 0
    changed_count: int = 0
    last_scan_at: datetime | None = None


class SourceRecord(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(64), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    __table_args__ = (
        Index(
            "uq_sources_config_source_path",
            config["source_path"].as_string(),
            unique=True,
        ),
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    changed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


def serialize_source(record: SourceRecord) -> Source:
    return Source(
        id=record.id,
        name=record.name,
        provider_type=record.provider_type,
        config=record.config,
        status=record.status,
        document_count=record.document_count,
        changed_count=record.changed_count,
        last_scan_at=record.last_scan_at,
    )
