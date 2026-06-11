from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx

from embeddings.base import EmbeddingModelInfo


_JINA_DEFAULT_DIMENSIONS: dict[str, int] = {
    "jina-embeddings-v3": 1024,
    "jina-embeddings-v4": 2048,
}


class JinaEmbeddingProvider:
    def __init__(
        self,
        api_key: str,
        model: str = "jina-embeddings-v3",
        dimension: int | None = None,
        batch_size: int = 128,
        timeout: float = 30.0,
        base_url: str = "https://api.jina.ai/v1/embeddings",
        query_task: str = "retrieval.query",
        document_task: str = "retrieval.passage",
    ) -> None:
        if not api_key:
            raise ValueError("Jina API key is required")

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        self._api_key = api_key
        self._model = model
        self._dimension = dimension or _JINA_DEFAULT_DIMENSIONS.get(model)

        if self._dimension is None:
            raise ValueError(
                f"Unknown Jina embedding dimension for model={model!r}. "
                "Pass dimension explicitly."
            )

        self._batch_size = batch_size
        self._base_url = base_url
        self._query_task = query_task
        self._document_task = document_task

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    @property
    def model_info(self) -> EmbeddingModelInfo:
        return EmbeddingModelInfo(
            provider="jina",
            model=self._model,
            dimension=self._dimension,
        )

    async def embed_query(self, text: str) -> list[float]:
        self._validate_text(text)

        vectors = await self._embed(
            texts=[text],
            task=self._query_task,
        )

        return vectors[0]

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self._validate_texts(texts)

        vectors: list[list[float]] = []

        for batch in self._batch(texts, self._batch_size):
            batch_vectors = await self._embed(
                texts=list(batch),
                task=self._document_task,
            )
            vectors.extend(batch_vectors)

        return vectors

    async def close(self) -> None:
        await self._client.aclose()

    async def _embed(
        self,
        texts: Sequence[str],
        task: str,
    ) -> list[list[float]]:
        payload: dict[str, Any] = {
            "model": self._model,
            "task": task,
            "input": list(texts),
        }

        response = await self._client.post(
            self._base_url,
            json=payload,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Jina embedding request failed: "
                f"status={exc.response.status_code}, body={exc.response.text}"
            ) from exc

        body = response.json()

        data = body.get("data")
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected Jina response shape: {body}")

        vectors: list[list[float]] = []

        for item in data:
            embedding = item.get("embedding")

            if not isinstance(embedding, list):
                raise RuntimeError(f"Missing embedding in Jina response item: {item}")

            self._validate_vector(embedding)
            vectors.append(embedding)

        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Jina returned {len(vectors)} embeddings for {len(texts)} inputs"
            )

        return vectors

    def _validate_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("Embedding input must be a string")

        # if not text.strip():
        #     raise ValueError("Embedding input cannot be empty")

    def _validate_texts(self, texts: Sequence[str]) -> None:
        if not texts:
            raise ValueError("texts cannot be empty")

        if not isinstance(texts, list):
            texts = [texts]

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
