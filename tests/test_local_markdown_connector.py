from flora_connectors import LocalMarkdownConnector
from flora_shared.schemas import PatchProposal


def test_local_markdown_connector_lists_reads_and_patches(tmp_path):
    import asyncio

    note = tmp_path / "note.md"
    note.write_text("The current API version is 2024.", encoding="utf-8")
    ignored = tmp_path / ".obsidian"
    ignored.mkdir()
    (ignored / "workspace.md").write_text("ignore", encoding="utf-8")

    connector = LocalMarkdownConnector()
    refs = asyncio.run(connector.list_documents("source-1", {"root_path": str(tmp_path)}))

    assert len(refs) == 1
    document = asyncio.run(connector.read_document(refs[0]))
    assert document.content == "The current API version is 2024."

    result = asyncio.run(
        connector.apply_patch(
            refs[0],
            PatchProposal(
                id="proposal-1",
                claim_id="claim-1",
                document_id="document-1",
                snapshot_id="snapshot-1",
                original_text="The current API version is 2024.",
                proposed_text="The current API version needs verification.",
                citation_ids=["evidence-1"],
                status="approved",
                created_at="2026-05-24T00:00:00Z",
                updated_at="2026-05-24T00:00:00Z",
            ),
        )
    )

    assert result.applied is True
    assert note.read_text(encoding="utf-8") == "The current API version needs verification."
