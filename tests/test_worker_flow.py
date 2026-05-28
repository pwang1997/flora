from flora_core.services import OutboxService, new_id
from flora_shared.enums import EventType, JobStatus, ProviderType
from flora_shared.models import (
    AuditEventModel,
    ClaimModel,
    EvidenceItemModel,
    JobModel,
    OutboxEventModel,
    PatchProposalModel,
    SourceModel,
)
from flora_worker.polling import Worker


def test_worker_processes_markdown_scan_to_patch_proposal(db_session, tmp_path):
    import asyncio

    note = tmp_path / "market.md"
    note.write_text("As of 2024, the current market policy is unchanged.", encoding="utf-8")
    source = SourceModel(
        id=new_id(),
        name="Vault",
        provider_type=ProviderType.OBSIDIAN,
        config={"root_path": str(tmp_path)},
        status="active",
    )
    job = JobModel(id=new_id(), source_id=source.id, job_type="source_scan", status=JobStatus.PENDING)
    db_session.add_all([source, job])
    OutboxService().enqueue(
        db_session,
        EventType.SOURCE_SCAN_REQUESTED,
        "source",
        source.id,
        {"source_id": source.id, "job_id": job.id},
    )
    db_session.commit()

    worker = Worker("test-worker")
    for _ in range(10):
        event = db_session.query(OutboxEventModel).filter_by(status="pending").first()
        if event is None:
            break
        asyncio.run(worker.process_event(db_session, event))
        db_session.commit()

    assert db_session.query(ClaimModel).count() == 1
    assert db_session.query(EvidenceItemModel).count() == 1
    assert db_session.query(PatchProposalModel).count() == 1
    assert db_session.query(AuditEventModel).count() >= 4
