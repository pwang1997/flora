from __future__ import annotations

from collections.abc import Sequence

from openai import AsyncOpenAI

from embeddings.base import EmbeddingModelInfo


_OPENAI_DEFAULT_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimension: int | None = None,
        batch_size: int = 128,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required")

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
        )
        self._model = model
        self._dimension = dimension or _OPENAI_DEFAULT_DIMENSIONS.get(model)

        if self._dimension is None:
            raise ValueError(
                f"Unknown OpenAI embedding dimension for model={model!r}. "
                "Pass dimension explicitly."
            )

        self._batch_size = batch_size

    @property
    def model_info(self) -> EmbeddingModelInfo:
        return EmbeddingModelInfo(
            provider="openai",
            model=self._model,
            dimension=self._dimension,
        )

    async def embed_query(self, text: str) -> list[float]:
        self._validate_text(text)

        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
        )

        vector = response.data[0].embedding
        self._validate_vector(vector)

        return vector

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self._validate_texts(texts)

        vectors: list[list[float]] = []

        for batch in self._batch(texts, self._batch_size):
            response = await self._client.embeddings.create(
                model=self._model,
                input=list(batch),
            )

            # OpenAI returns embeddings in the same order as input.
            batch_vectors = [item.embedding for item in response.data]

            for vector in batch_vectors:
                self._validate_vector(vector)

            vectors.extend(batch_vectors)

        return vectors

    def _validate_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("Embedding input must be a string")

        if not text.strip():
            raise ValueError("Embedding input cannot be empty")

    def _validate_texts(self, texts: Sequence[str]) -> None:
        if not texts:
            raise ValueError("texts cannot be empty")

        for text in texts:
            self._validate_text(text)

    def _validate_vector(self, vector: list[float]) -> None:
        if len(vector) != self._dimension:
            raise ValueError(
                f"Unexpected embedding dimension. "
                f"Expected {self._dimension}, got {len(vector)}."
            )

    @staticmethod
    def _batch(
        texts: Sequence[str],
        batch_size: int,
    ) -> list[Sequence[str]]:
        return [
            texts[index : index + batch_size]
            for index in range(0, len(texts), batch_size)
        ]