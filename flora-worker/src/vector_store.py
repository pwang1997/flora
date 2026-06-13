from __future__ import annotations

import asyncio
from typing import Any

from qdrant_client import QdrantClient, models

from config import settings


class QdrantVectorStore:
    def __init__(self, client: QdrantClient | None = None) -> None:
        self._client = client or QdrantClient(
            url=settings.qdrant_host,
            api_key=settings.qdrant_api_key or None,
            cloud_inference=True,
        )

    def create_collection_if_not_exists(self, collection_name) -> None:
        if self._client.collection_exists(collection_name):
            return

        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.qdrant_vector_size,
                distance=models.Distance(settings.qdrant_distance),
            ),
        )

    async def upsert_document_version(
        self,
        *,
        collection_name : str,
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
            collection_name=collection_name,
            points=[point],
        )

    async def delete_document_version(
        self, 
        *,
        collection_name : str,
        document_version_id: str,
    ) -> None:
        await asyncio.to_thread(
            self._client.delete,
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[document_version_id]),
        )
