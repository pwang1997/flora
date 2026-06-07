from __future__ import annotations

import asyncio
from typing import Any

from qdrant_client import QdrantClient, models

from flora_worker.config import settings


class QdrantVectorStore:
    def __init__(self, client: QdrantClient | None = None) -> None:
        self._client = client or QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
        )
        self._collection_name = settings.qdrant_collection_name

    async def upsert_document_version(
        self,
        *,
        document_version_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        point = models.PointStruct(
            id=document_version_id,
            vector=vector,
            payload=payload,
        )
        await asyncio.to_thread(
            self._client.upsert,
            collection_name=self._collection_name,
            points=[point],
        )

    async def delete_document_version(self, document_version_id: str) -> None:
        await asyncio.to_thread(
            self._client.delete,
            collection_name=self._collection_name,
            points_selector=models.PointIdsList(points=[document_version_id]),
        )
