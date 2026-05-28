from sqlalchemy.orm import Session

from flora_core.services import AuditService, PatchGenerator
from flora_shared.models import ClaimModel, OutboxEventModel

audit = AuditService()
patches = PatchGenerator()


async def handle_patch_generation(db: Session, event: OutboxEventModel) -> None:
    claim = db.get(ClaimModel, event.payload["claim_id"])
    if not claim:
        raise ValueError(f"Claim not found: {event.payload['claim_id']}")
    proposal = patches.generate(db, claim)
    audit.record(db, "PATCH_PROPOSED", "patch_proposal", proposal.id, {"claim_id": claim.id})
