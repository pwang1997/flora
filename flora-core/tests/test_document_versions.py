def _create_source_and_document(client) -> tuple[str, str]:
    source_response = client.post(
        "/v1/sources/create",
        json={
            "name": "Document Versions API",
            "provider_type": "github",
            "config": {"source_path": "/tmp/document-versions-api"},
        },
    )
    assert source_response.status_code == 201
    source_id = source_response.json()["id"]

    document_response = client.post(
        "/v1/source-documents/create",
        json={
            "source_id": source_id,
            "external_id": "README.md",
            "title": "Readme",
            "metadata": {"folder": "docs"},
        },
    )
    assert document_response.status_code == 201
    return source_id, document_response.json()["id"]


def test_document_version_create_list_get_and_latest_endpoints(client) -> None:
    _, document_id = _create_source_and_document(client)

    first_response = client.post(
        "/v1/document-versions/create",
        json={
            "document_id": document_id,
            "content_hash": "version-hash-1",
            "content": "Initial content",
            "change_type": "created",
        },
    )
    assert first_response.status_code == 201
    first = first_response.json()
    assert first["version_number"] == 1
    assert first["content"] == "Initial content"

    second_response = client.post(
        "/v1/document-versions/create",
        json={
            "document_id": document_id,
            "content_hash": "version-hash-2",
            "content": "Updated content",
            "change_type": "updated",
        },
    )
    assert second_response.status_code == 201
    second = second_response.json()
    assert second["version_number"] == 2

    list_response = client.get("/v1/document-versions/list", params={"document_id": document_id})
    assert list_response.status_code == 200
    assert [version["id"] for version in list_response.json()] == [first["id"], second["id"]]

    get_response = client.get(f"/v1/document-versions/get/{first['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["content_hash"] == "version-hash-1"

    latest_response = client.get(f"/v1/document-versions/latest/{document_id}")
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == second["id"]
    assert latest_response.json()["content_hash"] == "version-hash-2"


def test_document_version_create_returns_404_for_missing_document(client) -> None:
    response = client.post(
        "/v1/document-versions/create",
        json={
            "document_id": "missing-document",
            "content_hash": "version-hash-1",
            "content": "Initial content",
            "change_type": "created",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "source document not found"
