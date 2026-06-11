from qdrant_client import models

from config import settings
from vector_store import QdrantVectorStore


class FakeQdrantClient:
    def __init__(self, collection_exists: bool) -> None:
        self._collection_exists = collection_exists
        self.created_collections: list[tuple[str, models.VectorParams]] = []
        self.upserts: list[tuple[str, list[models.PointStruct]]] = []
        self.deletes: list[tuple[str, models.PointIdsList]] = []

    def collection_exists(self, collection_name: str) -> bool:
        return self._collection_exists

    def create_collection(self, *, collection_name: str, vectors_config: models.VectorParams) -> None:
        self.created_collections.append((collection_name, vectors_config))
        self._collection_exists = True

    def upsert(self, *, collection_name: str, points: list[models.PointStruct]) -> None:
        self.upserts.append((collection_name, points))

    def delete(self, *, collection_name: str, points_selector: models.PointIdsList) -> None:
        self.deletes.append((collection_name, points_selector))


def test_vector_store_creates_collection_when_absent() -> None:
    client = FakeQdrantClient(collection_exists=False)
    vector_store = QdrantVectorStore(client=client)

    vector_store.create_collection_if_not_exists("source_src_1")

    assert len(client.created_collections) == 1
    collection_name, vectors_config = client.created_collections[0]
    assert collection_name == "source_src_1"
    assert vectors_config.size == settings.qdrant_vector_size
    assert vectors_config.distance == models.Distance.COSINE


def test_vector_store_does_not_create_existing_collection() -> None:
    client = FakeQdrantClient(collection_exists=True)
    vector_store = QdrantVectorStore(client=client)

    vector_store.create_collection_if_not_exists("source_src_1")

    assert client.created_collections == []
