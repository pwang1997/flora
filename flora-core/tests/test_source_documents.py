def _create_source(client, name: str = "Documents API") -> str:
    response = client.post(
        "/v1/sources/create",
        json={
            "name": name,
            "provider_type": "github",
            "config": {"source_path": f"/tmp/{name.lower().replace(' ', '-')}"},
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_source_document_crud_endpoints(client) -> None:
    source_id = _create_source(client)

    create_response = client.post(
        "/v1/source-documents/create",
        json={
            "source_id": source_id,
            "external_id": "README.md",
            "title": "Readme",
            "uri": "https://example.com/README.md",
            "content_hash": "hash-1",
            "metadata": {"folder": "docs"},
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    document_id = created["id"]
    assert created["metadata"] == {"folder": "docs"}
    assert created["status"] == "active"

    list_response = client.get("/v1/source-documents/list", params={"source_id": source_id})
    assert list_response.status_code == 200
    assert [document["id"] for document in list_response.json()] == [document_id]

    get_response = client.get(f"/v1/source-documents/get/{document_id}")
    assert get_response.status_code == 200
    assert get_response.json()["external_id"] == "README.md"

    update_response = client.patch(
        f"/v1/source-documents/update/{document_id}",
        json={
            "title": "Updated readme",
            "content_hash": "hash-2",
            "metadata": {"folder": "docs", "updated": True},
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Updated readme"
    assert updated["content_hash"] == "hash-2"
    assert updated["metadata"] == {"folder": "docs", "updated": True}

    delete_response = client.delete(f"/v1/source-documents/delete/{document_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"


def test_source_document_get_returns_404_for_missing_document(client) -> None:
    response = client.get("/v1/source-documents/get/missing-document")

    assert response.status_code == 404
    assert response.json()["detail"] == "source document not found"


def test_source_document_create_returns_404_for_missing_source(client) -> None:
    response = client.post(
        "/v1/source-documents/create",
        json={
            "source_id": "missing-source",
            "external_id": "README.md",
            "title": "Readme",
            "content_hash": "hash-1",
            "metadata": {},
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "source not found"
