from pathlib import Path

from config import REPO_ROOT, Settings, WORKER_ROOT


def test_settings_load_repo_root_env(monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings()

    assert settings.database_url == "postgresql+psycopg://flora:flora@postgres:5432/flora"


def test_settings_resolve_worker_relative_kafka_ssl_cafile(monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setenv("KAFKA_SSL_CAFILE", "ca.pem")

    settings = Settings()

    assert settings.kafka_ssl_cafile == str(WORKER_ROOT / "ca.pem")
    assert Path(settings.kafka_ssl_cafile).exists()
