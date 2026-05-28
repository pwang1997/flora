from fastapi.testclient import TestClient

from flora_api.database import get_db
from flora_api.main import app
from flora_shared.models import OutboxEventModel


def test_source_scan_creates_job_and_outbox_event(db_session, tmp_path):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    response = client.post(
        "/sources",
        json={"name": "Notes", "provider_type": "local_markdown", "config": {"root_path": str(tmp_path)}},
    )
    assert response.status_code == 200
    source_id = response.json()["id"]

    scan = client.post(f"/sources/{source_id}/scan")
    assert scan.status_code == 200
    assert scan.json()["status"] == "pending"

    events = db_session.query(OutboxEventModel).all()
    assert len(events) == 1
    assert events[0].event_type == "SOURCE_SCAN_REQUESTED"

    app.dependency_overrides.clear()
