from abc import ABC, abstractmethod
from typing import Any

from flora_shared.schemas import DocumentRef, FloraDocument, PatchProposal, PatchResult


class KnowledgeSourceConnector(ABC):
    @abstractmethod
    async def list_documents(self, source_id: str, source_config: dict[str, Any]) -> list[DocumentRef]:
        raise NotImplementedError

    @abstractmethod
    async def read_document(self, document_ref: DocumentRef) -> FloraDocument:
        raise NotImplementedError

    @abstractmethod
    async def apply_patch(self, document_ref: DocumentRef, patch: PatchProposal) -> PatchResult:
        raise NotImplementedError
