from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

DEFAULT_DOCUMENT_INGESTION_TOPIC = "flora.documents.created"
DocumentChangeType = Literal["created", "updated", "deleted", "restored"]


def document_version_event_type(change_type: DocumentChangeType | str) -> str:
    return f"document.version.{change_type}"


class DocumentIngestionEventPayload(BaseModel):
    event_type: str = Field(..., min_length=1)
    source_document_id: str
    document_version_id: str
    source_id: str
    version_number: int
    change_type: DocumentChangeType
    content_hash: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    uri: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime
