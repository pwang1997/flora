import logging

from fastapi.testclient import TestClient


def test_list_sources(client: TestClient, caplog) -> None:
    client.post(
        "/v1/sources",
        json={
            "name": "Personal Obsidian Vault",
            "provider_type": "obsidian",
            "config": {"root_path": "/Users/pwang/Documents/Knowledge"},
        },
    )

    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger="routes.sources.sources"):
        response = client.get("/v1/sources")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Personal Obsidian Vault"
    assert payload[0]["provider_type"] == "obsidian"
    assert payload[0]["status"] == "active"
    assert [record.message for record in caplog.records] == [
        "sources.list.start",
        "sources.list.completed",
    ]
    assert caplog.records[-1].data_state == {"changed": False, "returned_count": 1}


def test_create_source(client: TestClient, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="routes.sources.sources"):
        response = client.post(
            "/v1/sources",
            json={
                "name": "My Vault",
                "provider_type": "obsidian",
                "config": {"root_path": "/Users/pwang/Documents/My Vault"},
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"].startswith("src_")
    assert payload["name"] == "My Vault"
    assert payload["provider_type"] == "obsidian"
    assert payload["config"]["root_path"] == "/Users/pwang/Documents/My Vault"

    list_response = client.get("/v1/sources")
    assert list_response.json()[0]["id"] == payload["id"]
    assert [record.message for record in caplog.records] == [
        "sources.create.start",
        "sources.create.completed",
    ]
    assert caplog.records[0].source_request == {
        "name": "My Vault",
        "provider_type": "obsidian",
    }
    assert caplog.records[-1].data_state == {
        "changed": True,
        "before_count": 0,
        "after_count": 1,
        "created_source_id": payload["id"],
        "created_source_status": "active",
    }
