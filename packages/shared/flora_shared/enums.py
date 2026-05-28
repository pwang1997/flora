from enum import StrEnum


class ProviderType(StrEnum):
    LOCAL_MARKDOWN = "local_markdown"
    OBSIDIAN = "obsidian"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class EventType(StrEnum):
    SOURCE_SCAN_REQUESTED = "SOURCE_SCAN_REQUESTED"
    DOCUMENT_SYNC_REQUESTED = "DOCUMENT_SYNC_REQUESTED"
    CLAIM_EXTRACTION_REQUESTED = "CLAIM_EXTRACTION_REQUESTED"
    CLAIM_VERIFICATION_REQUESTED = "CLAIM_VERIFICATION_REQUESTED"
    PATCH_GENERATION_REQUESTED = "PATCH_GENERATION_REQUESTED"
    PATCH_APPLICATION_REQUESTED = "PATCH_APPLICATION_REQUESTED"


class ClaimStatus(StrEnum):
    EXTRACTED = "extracted"
    CLASSIFIED = "classified"
    VERIFIED = "verified"
    PATCH_PROPOSED = "patch_proposed"


class StalenessRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PatchStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"


class ApprovalDecisionType(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
