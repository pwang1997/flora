from __future__ import annotations

from openai import AsyncOpenAI

from flora_worker.config import settings


class EmbeddingService:
    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return list(response.data[0].embedding)
