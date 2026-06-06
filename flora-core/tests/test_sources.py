import logging

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models.sources import SourceRecord


def test_list_sources(client: TestClient, caplog) -> None:
    client.post(
        "/v1/sources/create",
        json={
            "name": "Personal Obsidian Vault",
            "provider_type": "obsidian",
            "config": {"source_path": "/Users/pwang/Documents/Knowledge"},
        },
    )

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="routes.sources.sources"):
        response = client.get("/v1/sources/list")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Personal Obsidian Vault"
    assert payload[0]["provider_type"] == "obsidian"
    assert payload[0]["status"] == "active"

    assert len(caplog.records) == 2
    assert caplog.records[0].message == "list_sources starts: {}"
    assert caplog.records[0].payload == {}
    assert caplog.records[1].message.startswith("list_sources completed: ")
    assert len(caplog.records[1].return_value) == 1
    assert caplog.records[1].return_value[0]["name"] == "Personal Obsidian Vault"


@pytest.mark.parametrize("provider_type", ["local_markdown", "obsidian", "github", "notion"])
def test_create_source_accepts_supported_providers(client: TestClient, provider_type: str) -> None:
    response = client.post(
        "/v1/sources/create",
        json={
            "name": f"{provider_type} source",
            "provider_type": provider_type,
            "config": {"source_path": f"/sources/{provider_type}"},
        },
    )

    assert response.status_code == 201
    assert response.json()["provider_type"] == provider_type


def test_create_source(client: TestClient, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="routes.sources.sources"):
        response = client.post(
            "/v1/sources/create",
            json={
                "name": "My Vault",
                "provider_type": "obsidian",
                "config": {"source_path": "/Users/pwang/Documents/My Vault"},
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"].startswith("src_")
    assert payload["name"] == "My Vault"
    assert payload["provider_type"] == "obsidian"
    assert payload["config"]["source_path"] == "/Users/pwang/Documents/My Vault"

    list_response = client.get("/v1/sources/list")
    assert list_response.json()[0]["id"] == payload["id"]

    assert len(caplog.records) == 2
    assert caplog.records[0].message.startswith("create_source starts: ")
    assert caplog.records[0].payload["payload"]["name"] == "My Vault"
    assert caplog.records[1].message.startswith("create_source completed: ")
    assert caplog.records[1].return_value["id"].startswith("src_")
    assert caplog.records[1].return_value["name"] == "My Vault"


def test_create_source_requires_source_path(client: TestClient) -> None:
    response = client.post(
        "/v1/sources/create",
        json={
            "name": "My Vault",
            "provider_type": "obsidian",
            "config": {},
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, config.source_path is required"


def test_create_source_rejects_duplicate_source_path(client: TestClient) -> None:
    payload = {
        "name": "My Vault",
        "provider_type": "obsidian",
        "config": {"source_path": "/Users/pwang/Documents/My Vault"},
    }

    first_response = client.post("/v1/sources/create", json=payload)
    duplicate_response = client.post(
        "/v1/sources/create",
        json={
            **payload,
            "name": "My Vault Copy",
        },
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "config.source_path must be unique"}


def test_source_path_is_required_by_database_constraint() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = None
    try:
        db = TestingSessionLocal()
        db.add(
            SourceRecord(
                id="src_missing_path",
                name="Missing Path",
                provider_type="obsidian",
                config={},
            )
        )

        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        if db is not None:
            db.close()
        Base.metadata.drop_all(bind=engine)


def test_sources_endpoints_are_documented(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/v1/sources/list" in paths
    assert "/v1/sources/create" in paths
