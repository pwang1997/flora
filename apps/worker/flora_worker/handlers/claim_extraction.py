from sqlalchemy.orm import Session

from flora_core.services import AuditService, ClaimExtractionService, OutboxService
from flora_shared.enums import EventType, StalenessRisk
from flora_shared.models import DocumentSnapshotModel, OutboxEventModel

audit = AuditService()
claims = ClaimExtractionService()
outbox = OutboxService()


async def handle_claim_extraction(db: Session, event: OutboxEventModel) -> None:
    snapshot = db.get(DocumentSnapshotModel, event.payload["snapshot_id"])
    if not snapshot:
        raise ValueError(f"Snapshot not found: {event.payload['snapshot_id']}")
    stored = claims.store_claims(db, event.payload["document_id"], snapshot)
    for claim in stored:
        if claim.staleness_risk in {StalenessRisk.HIGH, StalenessRisk.MEDIUM}:
            outbox.enqueue(
                db,
                EventType.CLAIM_VERIFICATION_REQUESTED,
                "claim",
                claim.id,
                {"claim_id": claim.id},
            )
    audit.record(
        db,
        "CLAIMS_EXTRACTED",
        "document_snapshot",
        snapshot.id,
        {"claim_count": len(stored)},
    )
