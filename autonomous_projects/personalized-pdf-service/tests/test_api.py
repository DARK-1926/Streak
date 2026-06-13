import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def auth_header():
    response = client.post("/auth/token", json={"user_id": "test-user"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_generate_endpoint(auth_header):
    payload = {
        "template_name": "contract",
        "user_profile": {"name": "Bob", "jurisdiction": "NY"},
        "extra_prompt": "Add a confidentiality clause for New York law."
    }
    resp = client.post("/pdf/generate", json=payload, headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "processing"]

def test_status_endpoint(auth_header):
    # Create a dummy job directly in DB for test purpose
    from src.database import SessionLocal
    from src.models import PdfJob
    db = SessionLocal()
    job = PdfJob(user_id="test-user", template_name="contract", status="success", pdf_url="/static/pdfs/dummy.pdf")
    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()
    resp = client.get(f"/pdf/status/{job.id}", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["pdf_url"] == "/static/pdfs/dummy.pdf"
