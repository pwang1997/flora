from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from flora_shared.enums import (
    ApprovalDecisionType,
    ClaimStatus,
    EventType,
    JobStatus,
    OutboxStatus,
    PatchStatus,
    ProviderType,
    StalenessRisk,
)


class SourceCreate(BaseModel):
    name: str
    provider_type: ProviderType = ProviderType.LOCAL_MARKDOWN
    config: dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    provider_type: ProviderType
    config: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentRef(BaseModel):
    source_id: str
    provider_document_id: str
    title: str
    path: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FloraDocument(BaseModel):
    ref: DocumentRef
    content: str
    content_type: str = "text/markdown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    content_hash: str
    content: str
    provider_metadata: dict[str, Any]
    created_at: datetime


class Claim(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    snapshot_id: str
    text: str
    status: ClaimStatus
    staleness_risk: StalenessRisk
    created_at: datetime


class EvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    claim_id: str
    title: str
    url: str
    summary: str
    published_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PatchProposal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    claim_id: str
    document_id: str
    snapshot_id: str
    original_text: str
    proposed_text: str
    citation_ids: list[str]
    status: PatchStatus
    created_at: datetime
    updated_at: datetime


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    decision: ApprovalDecisionType
    decided_at: datetime


class AuditEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    aggregate_type: str
    aggregate_id: str
    payload: dict[str, Any]
    created_at: datetime


class OutboxEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: EventType
    aggregate_type: str
    aggregate_id: str
    payload: dict[str, Any]
    status: OutboxStatus
    attempts: int
    available_at: datetime
    created_at: datetime


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str | None
    job_type: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime


class PatchResult(BaseModel):
    applied: bool
    message: str
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
