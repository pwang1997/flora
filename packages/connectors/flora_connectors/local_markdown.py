from __future__ import annotations

from pathlib import Path
from typing import Any

from flora_connectors.base import KnowledgeSourceConnector
from flora_shared.schemas import DocumentRef, FloraDocument, PatchProposal, PatchResult


class LocalMarkdownConnector(KnowledgeSourceConnector):
    async def list_documents(self, source_id: str, source_config: dict[str, Any]) -> list[DocumentRef]:
        root = self._root(source_config)
        refs: list[DocumentRef] = []
        for path in sorted(root.rglob("*.md")):
            if any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            relative = path.relative_to(root).as_posix()
            refs.append(
                DocumentRef(
                    source_id=source_id,
                    provider_document_id=relative,
                    title=path.stem,
                    path=str(path),
                    metadata={"root_path": str(root), "relative_path": relative},
                )
            )
        return refs

    async def read_document(self, document_ref: DocumentRef) -> FloraDocument:
        path = Path(document_ref.path)
        content = path.read_text(encoding="utf-8")
        return FloraDocument(
            ref=document_ref,
            content=content,
            metadata={"size": path.stat().st_size, "mtime": path.stat().st_mtime},
        )

    async def apply_patch(self, document_ref: DocumentRef, patch: PatchProposal) -> PatchResult:
        path = Path(document_ref.path)
        content = path.read_text(encoding="utf-8")
        if patch.original_text not in content:
            return PatchResult(applied=False, message="Original text not found; source may have changed")
        updated = content.replace(patch.original_text, patch.proposed_text, 1)
        path.write_text(updated, encoding="utf-8")
        return PatchResult(applied=True, message="Patch applied", provider_metadata={"path": str(path)})

    def _root(self, source_config: dict[str, Any]) -> Path:
        root_path = source_config.get("root_path") or source_config.get("path")
        if not root_path:
            raise ValueError("Local Markdown sources require config.root_path")
        root = Path(root_path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Markdown root does not exist: {root}")
        return root
