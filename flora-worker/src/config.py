from pathlib import Path
from typing import Literal
from flora_shared import DEFAULT_DOCUMENT_INGESTION_TOPIC
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

WORKER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKER_ROOT.parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://flora:flora@localhost:5400/flora"

    kafka_bootstrap_servers: str = Field(
        "localhost:9092",
        validation_alias=AliasChoices("KAFKA_BOOTSTRAP_SERVER", "KAFKA_BOOTSTRAP_SERVERS"),
    )
    kafka_username: str = Field("", validation_alias="KAFKA_USERNAME")
    kafka_password: str = Field("", validation_alias="KAFKA_PASSWORD")
    kafka_ssl_cafile: str = Field("ca.pem", validation_alias="KAFKA_SSL_CAFILE")
    kafka_sasl_mechanism: str = Field("SCRAM-SHA-256", validation_alias="KAFKA_SASL_MECHANISM")
    kafka_documents_topic: str = Field(
        DEFAULT_DOCUMENT_INGESTION_TOPIC,
        validation_alias="KAFKA_DOCUMENTS_TOPIC",
    )
    kafka_producer_client_id: str = "flora-worker-outbox-publisher"
    kafka_consumer_client_id: str = "flora-worker-consumer"
    kafka_consumer_group_id: str = "flora-worker"
    kafka_poll_timeout_ms: int = 1000

    outbox_claim_timeout_seconds: int = 30
    outbox_retry_backoff_seconds: int = 30
    outbox_publish_batch_size: int = 50
    worker_role: Literal["publisher", "ingester", "all"] = Field(
        "all",
        validation_alias="WORKER_ROLE",
    )
    worker_api_host: str = Field("0.0.0.0", validation_alias="WORKER_API_HOST")
    worker_api_port: int = Field(8100, validation_alias="WORKER_API_PORT")

    embedding_provider: str = Field("jina", validation_alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field("jina-embeddings-v3", validation_alias="EMBEDDING_MODEL")
    embedding_dimension: int | None = Field(None, validation_alias="EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(128, validation_alias="EMBEDDING_BATCH_SIZE")
    openai_api_key: str | None = Field(None, validation_alias="OPENAI_API_KEY")
    jina_api_key: str | None = Field(None, validation_alias="JINA_API_KEY")

    qdrant_host: str = Field(validation_alias="QDRANT_HOST")
    qdrant_port: int = Field(6333, validation_alias="QDRANT_PORT")
    qdrant_api_key: str | None = Field(None, validation_alias="QDRANT_API_KEY")
    qdrant_vector_size: int = Field(1024, validation_alias="QDRANT_VECTOR_SIZE")
    qdrant_distance: str = Field("Cosine", validation_alias="QDRANT_DISTANCE")

    @field_validator("kafka_ssl_cafile", mode="after")
    @classmethod
    def resolve_kafka_ssl_cafile(cls, value: str) -> str:
        cafile = Path(value).expanduser()
        if cafile.is_absolute():
            return str(cafile)

        if cafile.exists():
            return str(cafile.resolve())

        worker_relative = WORKER_ROOT / cafile
        return str(worker_relative)


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
