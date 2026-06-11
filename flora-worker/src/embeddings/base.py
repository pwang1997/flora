from typing import Protocol, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingModelInfo:
    provider: str
    model: str
    dimension: int


@dataclass(frozen=True)
class EmbeddingResult:
    text: str
    vector: list[float]
    model_info: EmbeddingModelInfo


class EmbeddingProvider(Protocol):
    @property
    def model_info(self) -> EmbeddingModelInfo:
        ...

    async def embed_query(self, text: str) -> list[float]:
        ...

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        ...