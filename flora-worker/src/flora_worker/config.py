from typing import Literal

from flora_shared import DEFAULT_DOCUMENT_INGESTION_TOPIC
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://flora:flora@localhost:5400/flora"

    kafka_bootstrap_servers: str = Field(
        "",
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
    worker_role: Literal["publisher", "ingester", "all"] = "all"

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "flora_documents"


settings = Settings()
