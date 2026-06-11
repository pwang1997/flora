from config import Settings
from embeddings.base import EmbeddingProvider
from embeddings.jina_provider import JinaEmbeddingProvider
from embeddings.openai_provider import OpenAIEmbeddingProvider


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()

    if provider == "openai":
        print("Using openai embedding provider")
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            batch_size=settings.embedding_batch_size,
        )

    if provider == "jina":
        print("Using jina embedding provider")
        return JinaEmbeddingProvider(
            api_key=settings.jina_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            batch_size=settings.embedding_batch_size,
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")