import json
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_process_endpoint(monkeypatch):
    # Mock Celery task to avoid background processing
    class DummyTask:
        def delay(self, *args, **kwargs):
            return self
        def get(self, timeout=None):
            return {"message_id": args[0], "summary": "mock", "priority": 3}
    monkeypatch.setattr('src.tasks.process_email_task', DummyTask())

    payload = {
        "message_id": "msg-123",
        "sender": "alice@example.com",
        "subject": "Quarterly Report",
        "body": "Please find the Q1 report attached. Let me know if you have questions."
    }
    resp = client.post("/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["message_id"] == "msg-123"
    assert data["summary"] == "processing"
