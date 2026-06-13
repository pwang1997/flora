from config import Settings


def test_kafka_settings_accept_existing_env_aliases(monkeypatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
    monkeypatch.setenv("KAFKA_USERNAME", "flora-user")
    monkeypatch.setenv("KAFKA_PASSWORD", "flora-pass")
    monkeypatch.setenv("KAFKA_DOCUMENTS_TOPIC", "flora.documents.ingestion")

    settings = Settings()

    assert settings.kafka_bootstrap_servers == "localhost:9092"
    assert settings.kafka_username == "flora-user"
    assert settings.kafka_password == "flora-pass"
    assert settings.kafka_documents_topic == "flora.documents.ingestion"
