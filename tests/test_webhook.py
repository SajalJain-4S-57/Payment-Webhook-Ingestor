import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from app.main import app
from app.config import settings
from app.database import get_db


def test_health_check_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


def test_webhook_flow_and_idempotency(client):
    unique_id = f"evt_test_{uuid.uuid4().hex[:8]}"
    payload = {
        "event_id": unique_id,
        "event_type": "payment_success",
        "amount": 150.0,
    }
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}

    # First delivery -> Success
    res1 = client.post("/webhook", json=payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"

    # Duplicate delivery -> Ignored
    res2 = client.post("/webhook", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "ignored"


def test_webhook_invalid_secret(client):
    payload = {
        "event_id": f"evt_secret_{uuid.uuid4().hex[:8]}",
        "event_type": "payment_success",
        "amount": 5000.0,
    }
    headers = {"X-Webhook-Secret": "wrong-secret"}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 401


def test_webhook_invalid_payload(client):
    payload = {"event_id": f"evt_bad_{uuid.uuid4().hex[:8]}"}
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 422


def test_webhook_stale_timestamp(client):
    old_time = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    payload = {
        "event_id": f"evt_stale_{uuid.uuid4().hex[:8]}",
        "event_type": "payment_success",
        "amount": 50.0,
        "timestamp": old_time,
    }
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 422


def test_webhook_payload_too_large(client):
    headers = {
        "X-Webhook-Secret": settings.WEBHOOK_SECRET,
        "Content-Length": str(2 * 1024 * 1024),  # 2MB
    }
    payload = {
        "event_id": "evt_large",
        "event_type": "payment_success",
        "amount": 10.0,
    }
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 413


def test_database_failure_handling(client):
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("DB Connection Lost")

    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        "event_id": f"evt_fail_{uuid.uuid4().hex[:8]}",
        "event_type": "payment_success",
        "amount": 100.0,
    }
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}

    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 500
    assert response.json()["detail"] == "Database operational failure"

    app.dependency_overrides.clear()
