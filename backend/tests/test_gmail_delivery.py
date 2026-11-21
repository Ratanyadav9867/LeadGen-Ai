import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.gmail_service import (
    validate_email_eligibility,
    send_via_gmail_api,
)
from app.models.lead import Lead
from app.models.email_record import EmailRecord

client = TestClient(app)


def _create_test_lead_with_draft(custom_email=None, custom_subject="Follow-up on AI Solutions", custom_body="Dear Client, thank you for reaching out."):
    """Helper to create a fresh lead with an existing AI draft in Draft status."""
    email = custom_email or f"lead_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Jane Doe",
        "company": "Acme Innovations",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$10,000 - $25,000",
        "description": "Logistics optimization inquiry."
    }
    resp = client.post("/api/automation/lead-capture", json=payload)
    lead_id = resp.json()["lead_id"]

    # Save draft
    if custom_subject or custom_body:
        draft_payload = {
            "subject": custom_subject or "Default Subject",
            "body": custom_body or "Default Body Content",
            "summary": "Logistics AI inquiry"
        }
        client.post(f"/api/leads/{lead_id}/ai-response", json=draft_payload)

    return lead_id, email


def test_01_valid_draft_sent_successfully():
    """1. Valid draft sent successfully via Gmail dispatch endpoint."""
    lead_id, email = _create_test_lead_with_draft()

    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 200
    data = send_resp.json()

    assert data["success"] is True
    assert data["email_status"] == "Sent"
    assert data["gmail_message_id"] is not None
    assert len(data["gmail_message_id"]) > 5
    assert data["sent_at"] is not None


def test_02_invalid_recipient_rejected():
    """2. Invalid recipient format rejected by pre-send eligibility check."""
    lead_id, _ = _create_test_lead_with_draft()

    # Tamper email to invalid syntax
    client.patch(f"/api/leads/{lead_id}/status", json={"email_status": "Draft"})
    from app.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    lead.email = "invalid-email-at-domain"
    db.commit()
    db.close()

    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 400
    assert "Invalid recipient email" in send_resp.json()["detail"]


def test_03_missing_subject_rejected():
    """3. Missing email subject draft rejected before sending."""
    lead_id, _ = _create_test_lead_with_draft()

    from app.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    lead.email_subject = ""
    db.commit()
    db.close()

    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 400
    assert "no generated email subject" in send_resp.json()["detail"]


def test_04_missing_body_rejected():
    """4. Missing email body draft rejected before sending."""
    lead_id, _ = _create_test_lead_with_draft()

    from app.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    lead.email_body = ""
    db.commit()
    db.close()

    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 400
    assert "no generated email body" in send_resp.json()["detail"]


def test_05_already_sent_email_not_sent_again():
    """5. Already-sent email is rejected with 409 Conflict to prevent duplicate transmission."""
    lead_id, _ = _create_test_lead_with_draft()

    # First send succeeds
    send1 = client.post(f"/api/leads/{lead_id}/send-email")
    assert send1.status_code == 200
    assert send1.json()["email_status"] == "Sent"

    # Second attempt must fail with 409 Conflict
    send2 = client.post(f"/api/leads/{lead_id}/send-email")
    assert send2.status_code == 409
    assert "Duplicate send prevented" in send2.json()["detail"]


def test_06_duplicate_n8n_execution_does_not_send_twice():
    """6. Duplicate n8n execution or webhook replay is idempotent and protected against double-send."""
    lead_id, _ = _create_test_lead_with_draft()
    mock_msg_id = f"gmail_msg_{uuid.uuid4().hex[:8]}"

    # First record from n8n
    rec1 = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": mock_msg_id,
        "error_message": None
    })
    assert rec1.status_code == 200
    assert rec1.json()["email_status"] == "Sent"

    # Exact retry from n8n (same message ID) returns 200 idempotent
    rec2 = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": mock_msg_id,
        "error_message": None
    })
    assert rec2.status_code == 200
    assert rec2.json()["message"] == "Send confirmation already recorded (idempotent)"

    # Attempt to record a new/different send on the same lead raises 409
    rec3 = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": "different_msg_id_456",
        "error_message": None
    })
    assert rec3.status_code == 409


def test_07_gmail_authentication_failure():
    """7. Gmail OAuth authentication failure (HTTP 401/403) recorded as Failed with details."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid Credentials"

    with patch("app.config.settings.GMAIL_ACCESS_TOKEN", "expired_token"):
        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            res = asyncio.run(send_via_gmail_api("test@example.com", "Test Subject", "Test Body", access_token="expired_token"))
            assert res["status"] == "Failed"
            assert "authentication failure" in res["error"]
            assert res["gmail_message_id"] is None


def test_08_gmail_api_rejection():
    """8. Gmail API rejection (HTTP 400/422) recorded as Failed without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Recipient mailbox quota exceeded"

    with patch("app.config.settings.GMAIL_ACCESS_TOKEN", "valid_token"):
        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            res = asyncio.run(send_via_gmail_api("test@example.com", "Test Subject", "Test Body", access_token="valid_token"))
            assert res["status"] == "Failed"
            assert "Gmail API rejection" in res["error"]
            assert res["gmail_message_id"] is None


def test_09_ambiguous_send_result_sets_delivery_unknown():
    """9. Ambiguous network timeout during dispatch marks status as 'Delivery Unknown'."""
    with patch("app.config.settings.GMAIL_ACCESS_TOKEN", "valid_token"):
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Connection timed out")):
            res = asyncio.run(send_via_gmail_api("test@example.com", "Test Subject", "Test Body", access_token="valid_token"))
            assert res["status"] == "Delivery Unknown"
            assert "timeout" in res["error"].lower()

    # Record Delivery Unknown in DB
    lead_id, _ = _create_test_lead_with_draft()
    rec_resp = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Delivery Unknown",
        "gmail_message_id": None,
        "error_message": "Network timeout waiting for Gmail confirmation"
    })
    assert rec_resp.status_code == 200
    assert rec_resp.json()["email_status"] == "Delivery Unknown"

    # Verify lead cannot be automatically re-sent without reconciliation
    send_retry = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_retry.status_code == 400
    assert "manual reconciliation required" in send_retry.json()["detail"].lower()


def test_10_successful_status_update_in_database():
    """10. Successful send updates Lead and EmailRecord models in SQLite with timestamps and message IDs."""
    lead_id, _ = _create_test_lead_with_draft()

    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 200
    msg_id = send_resp.json()["gmail_message_id"]

    from app.database import SessionLocal
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    email_rec = db.query(EmailRecord).filter(EmailRecord.lead_id == lead_id).order_by(EmailRecord.created_at.desc()).first()

    assert lead.email_status == "Sent"
    assert lead.gmail_message_id == msg_id
    assert lead.processed_at is not None

    assert email_rec.status == "Sent"
    assert email_rec.gmail_message_id == msg_id
    assert email_rec.sent_at is not None
    db.close()


def test_11_google_sheets_payload_structure_verification():
    """11. Verifies payload structure returned to Google Sheets contains all required update columns."""
    lead_id, _ = _create_test_lead_with_draft()
    msg_id = f"msg_{uuid.uuid4().hex[:10]}"

    record_resp = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": msg_id,
        "error_message": None
    })
    assert record_resp.status_code == 200
    data = record_resp.json()

    # Verify all fields consumed by Google Sheets node
    assert "lead_id" in data
    assert "recipient" in data
    assert "subject" in data
    assert "priority" in data
    assert "email_status" in data
    assert "processing_status" in data
    assert "gmail_message_id" in data
    assert "processed_at" in data

    assert data["email_status"] == "Sent"
    assert data["processing_status"] == "Completed"
    assert data["gmail_message_id"] == msg_id


def test_12_dashboard_displays_actual_status():
    """12. Dashboard API reflects real dispatch state, Gmail message ID, and sent timestamps."""
    lead_id, email = _create_test_lead_with_draft()

    # Send email
    client.post(f"/api/leads/{lead_id}/send-email")

    # 1. Check Leads detail endpoint
    lead_resp = client.get(f"/api/leads/{lead_id}")
    assert lead_resp.status_code == 200
    lead_data = lead_resp.json()
    assert lead_data["email_status"] == "Sent"
    assert lead_data["gmail_message_id"] is not None

    # 2. Check Email History endpoint
    history_resp = client.get("/api/integrations/emails")
    assert history_resp.status_code == 200
    history_items = history_resp.json()
    matching = [h for h in history_items if h["recipient"] == email]
    assert len(matching) > 0
    assert matching[0]["status"] == "Sent"
    assert matching[0]["gmail_message_id"] is not None
