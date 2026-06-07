from flora_shared.document_events import DEFAULT_DOCUMENT_INGESTION_TOPIC
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Flora Core"
    database_url: str = "postgresql+psycopg://flora:flora@localhost:5400/flora"
    log_level: str = "DEBUG"
    kafka_bootstrap_servers: str = Field(
        "",
        validation_alias=AliasChoices("KAFKA_BOOTSTRAP_SERVER", "KAFKA_BOOTSTRAP_SERVERS"),
    )
    kafka_username: str = Field("", validation_alias="KAFKA_USERNAME")
    kafka_password: str = Field("", validation_alias="KAFKA_PASSWORD")
    kafka_documents_topic: str = Field(
        DEFAULT_DOCUMENT_INGESTION_TOPIC,
        validation_alias="KAFKA_DOCUMENTS_TOPIC",
    )

settings = Settings()
