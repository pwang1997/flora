from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from flora_api.database import get_db
from flora_core.services import AuditService, OutboxService, new_id
from flora_shared.enums import ApprovalDecisionType, EventType, PatchStatus
from flora_shared.models import ApprovalDecisionModel, PatchProposalModel
from flora_shared.schemas import PatchProposal

router = APIRouter(tags=["patches"])
audit = AuditService()
outbox = OutboxService()


@router.get("/patch-proposals", response_model=list[PatchProposal])
def list_patch_proposals(db: Session = Depends(get_db)) -> list[PatchProposalModel]:
    return db.query(PatchProposalModel).order_by(PatchProposalModel.created_at.desc()).all()


@router.get("/patch-proposals/{proposal_id}", response_model=PatchProposal)
def get_patch_proposal(proposal_id: str, db: Session = Depends(get_db)) -> PatchProposalModel:
    proposal = db.get(PatchProposalModel, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Patch proposal not found")
    return proposal


@router.post("/patch-proposals/{proposal_id}/approve", response_model=PatchProposal)
def approve_patch(proposal_id: str, db: Session = Depends(get_db)) -> PatchProposalModel:
    proposal = db.get(PatchProposalModel, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Patch proposal not found")
    proposal.status = PatchStatus.APPROVED
    db.add(ApprovalDecisionModel(id=new_id(), proposal_id=proposal.id, decision=ApprovalDecisionType.APPROVED))
    outbox.enqueue(
        db,
        EventType.PATCH_APPLICATION_REQUESTED,
        "patch_proposal",
        proposal.id,
        {"proposal_id": proposal.id},
    )
    audit.record(db, "PATCH_APPROVED", "patch_proposal", proposal.id)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/patch-proposals/{proposal_id}/reject", response_model=PatchProposal)
def reject_patch(proposal_id: str, db: Session = Depends(get_db)) -> PatchProposalModel:
    proposal = db.get(PatchProposalModel, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Patch proposal not found")
    proposal.status = PatchStatus.REJECTED
    db.add(ApprovalDecisionModel(id=new_id(), proposal_id=proposal.id, decision=ApprovalDecisionType.REJECTED))
    audit.record(db, "PATCH_REJECTED", "patch_proposal", proposal.id)
    db.commit()
    db.refresh(proposal)
    return proposal
