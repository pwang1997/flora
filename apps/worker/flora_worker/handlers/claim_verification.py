from sqlalchemy.orm import Session

from flora_core.services import AuditService, OutboxService, StubResearchService
from flora_shared.enums import EventType
from flora_shared.models import ClaimModel, OutboxEventModel

audit = AuditService()
outbox = OutboxService()
research = StubResearchService()


async def handle_claim_verification(db: Session, event: OutboxEventModel) -> None:
    claim = db.get(ClaimModel, event.payload["claim_id"])
    if not claim:
        raise ValueError(f"Claim not found: {event.payload['claim_id']}")
    evidence = research.verify(db, claim)
    outbox.enqueue(
        db,
        EventType.PATCH_GENERATION_REQUESTED,
        "claim",
        claim.id,
        {"claim_id": claim.id},
    )
    audit.record(db, "EVIDENCE_COLLECTED", "claim", claim.id, {"evidence_id": evidence.id})
