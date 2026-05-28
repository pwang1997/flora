from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from flora_shared.models import (
    AuditEventModel,
    ClaimModel,
    DocumentModel,
    DocumentSnapshotModel,
    EvidenceItemModel,
    OutboxEventModel,
    PatchProposalModel,
)
from flora_shared.enums import ClaimStatus, EventType, OutboxStatus, PatchStatus, StalenessRisk
from flora_shared.schemas import FloraDocument


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid.uuid4())


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AuditService:
    def record(
        self,
        db: Session,
        action: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEventModel:
        event = AuditEventModel(
            id=new_id(),
            action=action,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload or {},
        )
        db.add(event)
        return event


class OutboxService:
    def enqueue(
        self,
        db: Session,
        event_type: EventType,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any] | None = None,
    ) -> OutboxEventModel:
        event = OutboxEventModel(
            id=new_id(),
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload or {},
            status=OutboxStatus.PENDING,
        )
        db.add(event)
        return event


class DocumentService:
    def upsert_snapshot(self, db: Session, document: FloraDocument) -> tuple[DocumentModel, DocumentSnapshotModel]:
        ref = document.ref
        existing = (
            db.query(DocumentModel)
            .filter(
                DocumentModel.source_id == ref.source_id,
                DocumentModel.provider_document_id == ref.provider_document_id,
            )
            .one_or_none()
        )
        if existing is None:
            existing = DocumentModel(
                id=new_id(),
                source_id=ref.source_id,
                provider_document_id=ref.provider_document_id,
                title=ref.title,
                path=ref.path,
            )
            db.add(existing)
            db.flush()
        else:
            existing.title = ref.title
            existing.path = ref.path

        digest = content_hash(document.content)
        snapshot = (
            db.query(DocumentSnapshotModel)
            .filter(
                DocumentSnapshotModel.document_id == existing.id,
                DocumentSnapshotModel.content_hash == digest,
            )
            .one_or_none()
        )
        if snapshot is None:
            snapshot = DocumentSnapshotModel(
                id=new_id(),
                document_id=existing.id,
                content_hash=digest,
                content=document.content,
                provider_metadata={**ref.metadata, **document.metadata},
            )
            db.add(snapshot)
            db.flush()
        existing.latest_snapshot_id = snapshot.id
        return existing, snapshot


class ClaimExtractionService:
    _sentence_pattern = re.compile(r"(?<=[.!?])\s+|\n+")
    _time_pattern = re.compile(
        r"\b(latest|current|currently|today|now|as of|recent|202[0-9]|203[0-9])\b",
        re.IGNORECASE,
    )

    def extract(self, snapshot: DocumentSnapshotModel) -> list[str]:
        claims: list[str] = []
        for sentence in self._sentence_pattern.split(snapshot.content):
            text = re.sub(r"\s+", " ", sentence.strip(" -#\t\r\n"))
            if len(text) < 24:
                continue
            if self._time_pattern.search(text):
                claims.append(text)
        return claims[:20]

    def classify(self, text: str) -> StalenessRisk:
        lowered = text.lower()
        if any(token in lowered for token in ["latest", "current", "currently", "today", "now", "as of"]):
            return StalenessRisk.HIGH
        if re.search(r"\b202[0-9]\b", lowered):
            return StalenessRisk.MEDIUM
        return StalenessRisk.LOW

    def store_claims(self, db: Session, document_id: str, snapshot: DocumentSnapshotModel) -> list[ClaimModel]:
        stored: list[ClaimModel] = []
        for text in self.extract(snapshot):
            if db.query(ClaimModel).filter(ClaimModel.snapshot_id == snapshot.id, ClaimModel.text == text).first():
                continue
            risk = self.classify(text)
            claim = ClaimModel(
                id=new_id(),
                document_id=document_id,
                snapshot_id=snapshot.id,
                text=text,
                staleness_risk=risk,
                status=ClaimStatus.CLASSIFIED,
            )
            db.add(claim)
            stored.append(claim)
        return stored


class StubResearchService:
    def verify(self, db: Session, claim: ClaimModel) -> EvidenceItemModel:
        existing = db.query(EvidenceItemModel).filter(EvidenceItemModel.claim_id == claim.id).first()
        if existing:
            return existing
        evidence = EvidenceItemModel(
            id=new_id(),
            claim_id=claim.id,
            title="MVP stub evidence",
            url=f"flora://stub-evidence/{claim.id}",
            summary=f"Stub verification for claim: {claim.text}",
            evidence_metadata={"provider": "stub", "deterministic": True},
        )
        claim.status = ClaimStatus.VERIFIED
        db.add(evidence)
        return evidence


class PatchGenerator:
    def generate(self, db: Session, claim: ClaimModel) -> PatchProposalModel:
        existing = db.query(PatchProposalModel).filter(PatchProposalModel.claim_id == claim.id).first()
        if existing:
            return existing
        evidence = db.query(EvidenceItemModel).filter(EvidenceItemModel.claim_id == claim.id).all()
        citation_ids = [item.id for item in evidence]
        proposed_text = f"{claim.text} [Needs review against updated evidence: {', '.join(citation_ids) or 'stub'}]"
        proposal = PatchProposalModel(
            id=new_id(),
            claim_id=claim.id,
            document_id=claim.document_id,
            snapshot_id=claim.snapshot_id,
            original_text=claim.text,
            proposed_text=proposed_text,
            citation_ids=citation_ids,
            status=PatchStatus.PENDING,
        )
        claim.status = ClaimStatus.PATCH_PROPOSED
        db.add(proposal)
        return proposal


class ApprovalService:
    def approve(self, proposal: PatchProposalModel) -> None:
        proposal.status = PatchStatus.APPROVED

    def reject(self, proposal: PatchProposalModel) -> None:
        proposal.status = PatchStatus.REJECTED
