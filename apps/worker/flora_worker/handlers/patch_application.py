from sqlalchemy.orm import Session

from flora_core.services import AuditService
from flora_shared.enums import PatchStatus
from flora_shared.models import DocumentModel, OutboxEventModel, PatchProposalModel, SourceModel
from flora_shared.schemas import DocumentRef, PatchProposal
from flora_worker.handlers.connectors import connector_for

audit = AuditService()


async def handle_patch_application(db: Session, event: OutboxEventModel) -> None:
    proposal = db.get(PatchProposalModel, event.payload["proposal_id"])
    if not proposal:
        raise ValueError(f"Patch proposal not found: {event.payload['proposal_id']}")
    document = db.get(DocumentModel, proposal.document_id)
    if not document:
        raise ValueError(f"Document not found: {proposal.document_id}")
    source = db.get(SourceModel, document.source_id)
    if not source:
        raise ValueError(f"Source not found: {document.source_id}")
    ref = DocumentRef(
        source_id=source.id,
        provider_document_id=document.provider_document_id,
        title=document.title,
        path=document.path,
        metadata=source.config,
    )
    connector = connector_for(source.provider_type)
    result = await connector.apply_patch(ref, PatchProposal.model_validate(proposal))
    proposal.status = PatchStatus.APPLIED if result.applied else PatchStatus.FAILED
    audit.record(
        db,
        "PATCH_APPLIED" if result.applied else "PATCH_FAILED",
        "patch_proposal",
        proposal.id,
        result.model_dump(),
    )
