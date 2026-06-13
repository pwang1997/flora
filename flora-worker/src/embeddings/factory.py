import logging

from config import Settings
from embeddings.base import EmbeddingProvider
from embeddings.jina_provider import JinaEmbeddingProvider
from embeddings.openai_provider import OpenAIEmbeddingProvider

logger = logging.getLogger(__name__)


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()

    if provider == "openai":
        logger.info("Using openai embedding provider")
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            batch_size=settings.embedding_batch_size,
        )

    if provider == "jina":
        logger.info("Using jina embedding provider")
        return JinaEmbeddingProvider(
            api_key=settings.jina_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            batch_size=settings.embedding_batch_size,
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
