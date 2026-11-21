import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.models.lead import Lead
from app.models.email_record import EmailRecord
from app.database import SessionLocal

client = TestClient(app)


def test_01_end_to_end_lead_creation_and_stats_sync():
    """1. Lead Creation: Ingests valid lead, validates initial status, and checks stats increment."""
    # Read initial stats
    initial_stats = client.get("/api/leads/stats").json()
    init_total = initial_stats["total_leads"]

    email = f"lead_{uuid.uuid4().hex[:6]}@enterprise.com"
    payload = {
        "name": "Sarah Connor",
        "company": "Cyberdyne Systems",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$25,000+",
        "description": "Enterprise robotics logistics automation."
    }

    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 201
    lead_id = resp.json()["lead_id"]

    # Verify stats updated
    new_stats = client.get("/api/leads/stats").json()
    assert new_stats["total_leads"] == init_total + 1
    assert new_stats["high_priority_leads"] >= 1


def test_02_duplicate_lead_prevention():
    """2. Duplicate Prevention: Secondary submission with existing email returns existing record, preventing duplicates."""
    email = f"bruce_{uuid.uuid4().hex[:6]}@wayne.com"
    payload = {
        "name": "Bruce Wayne",
        "company": "Wayne Enterprises",
        "email": email,
        "service": "CRM Lead Scoring",
        "budget": "$30,000+",
        "description": "High security data pipeline."
    }

    # 1st submission
    resp1 = client.post("/api/automation/lead-capture", json=payload)
    assert resp1.status_code == 201
    lead_id_1 = resp1.json()["lead_id"]

    # 2nd submission with duplicate email
    resp2 = client.post("/api/automation/lead-capture", json=payload)
    assert resp2.status_code == 200
    lead_id_2 = resp2.json()["lead_id"]

    assert lead_id_1 == lead_id_2
    assert resp2.json()["is_duplicate"] is True


def test_03_gemini_draft_generation_pipeline():
    """3. Gemini AI Draft Generation: Synthesizes personalized subject, consultative body, and summary."""
    email = f"peter_{uuid.uuid4().hex[:6]}@dailybugle.com"
    payload = {
        "name": "Peter Parker",
        "company": "Daily Bugle",
        "email": email,
        "service": "Google Workspace Integration",
        "budget": "$5,000 - $10,000",
        "description": "Automatic photo sync to Google Drive."
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]

    ai_resp = client.post(f"/api/leads/{lead_id}/generate-ai")
    assert ai_resp.status_code == 200
    data = ai_resp.json()

    assert "Daily Bugle" in data["email_subject"]
    assert "Peter" in data["email_body"]
    assert data["summary"] is not None
    assert len(data["summary"]) > 5
    assert data["email_status"] == "Draft"


def test_04_draft_persistence_and_association():
    """4. Draft Persistence: Saves draft in EmailRecord with Draft status and links to Lead."""
    email = f"clark_{uuid.uuid4().hex[:6]}@dailyplanet.com"
    payload = {
        "name": "Clark Kent",
        "company": "Daily Planet",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$10,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]

    draft_payload = {
        "subject": "Optimizing Daily Planet Workflows",
        "body": "Dear Clark, thank you for reaching out to LeadGen AI...",
        "summary": "Publishing workflow automation."
    }
    save_resp = client.post(f"/api/leads/{lead_id}/ai-response", json=draft_payload)
    assert save_resp.status_code == 200
    record_id = save_resp.json()["email_record_id"]

    db = SessionLocal()
    record = db.query(EmailRecord).filter(EmailRecord.id == record_id).first()
    assert record is not None
    assert record.lead_id == lead_id
    assert record.status == "Draft"
    assert record.subject == draft_payload["subject"]
    db.close()


def test_05_gmail_send_and_status_update():
    """5. Gmail Send & Status Update: Successful dispatch updates Lead and EmailRecord to Sent."""
    email = f"diana_{uuid.uuid4().hex[:6]}@themyscira.org"
    payload = {
        "name": "Diana Prince",
        "company": "Themyscira Cultural Center",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$15,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]

    client.post(f"/api/leads/{lead_id}/ai-response", json={
        "subject": "Themyscira AI Integration Architecture",
        "body": "Dear Diana, we look forward to assisting...",
        "summary": "Cultural archive intake sync."
    })

    # Dispatch email
    send_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert send_resp.status_code == 200
    data = send_resp.json()

    assert data["success"] is True
    assert data["email_status"] == "Sent"
    assert data["gmail_message_id"] is not None
    assert data["sent_at"] is not None


def test_06_duplicate_email_prevention_on_retry():
    """6. Duplicate Email Prevention: Re-dispatching to an already-sent lead raises HTTP 409 Conflict."""
    email = f"barry_{uuid.uuid4().hex[:6]}@starlabs.com"
    payload = {
        "name": "Barry Allen",
        "company": "S.T.A.R. Labs",
        "email": email,
        "service": "CRM Lead Scoring",
        "budget": "$20,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]

    client.post(f"/api/leads/{lead_id}/ai-response", json={
        "subject": "S.T.A.R. Labs CRM Pipeline",
        "body": "Dear Barry, telemetry sync details...",
        "summary": "Accelerator telemetry scoring."
    })

    # First send succeeds
    res1 = client.post(f"/api/leads/{lead_id}/send-email")
    assert res1.status_code == 200

    # Second send attempt blocked
    res2 = client.post(f"/api/leads/{lead_id}/send-email")
    assert res2.status_code == 409
    assert "Duplicate send prevented" in res2.json()["detail"]


def test_07_google_sheets_synchronization_payload():
    """7. Google Sheets Synchronization: Verifies record-send returns all columns expected by spreadsheet node."""
    email = f"hal_{uuid.uuid4().hex[:6]}@ferris.com"
    payload = {
        "name": "Hal Jordan",
        "company": "Ferris Aircraft",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$15,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]
    client.post(f"/api/leads/{lead_id}/generate-ai")

    mock_msg_id = f"gmail_{uuid.uuid4().hex[:10]}"
    sync_resp = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": mock_msg_id,
        "error_message": None
    })
    assert sync_resp.status_code == 200
    data = sync_resp.json()

    # Required spreadsheet columns
    for key in ["lead_id", "recipient", "subject", "priority", "email_status", "processing_status", "gmail_message_id", "processed_at"]:
        assert key in data
    assert data["email_status"] == "Sent"
    assert data["processing_status"] == "Completed"


def test_08_dashboard_statistics_calculation():
    """8. Dashboard Statistics: Verifies stats calculation reflects live data."""
    stats = client.get("/api/leads/stats").json()
    assert "total_leads" in stats
    assert "new_leads" in stats
    assert "high_priority_leads" in stats
    assert "emails_sent" in stats
    assert "emails_failed" in stats
    assert stats["total_leads"] >= stats["emails_sent"]


def test_09_email_history_aggregation():
    """9. Email History: Verifies /api/integrations/emails aggregates dispatch records with message IDs."""
    email = f"arthur_{uuid.uuid4().hex[:6]}@atlantis.org"
    payload = {
        "name": "Arthur Curry",
        "company": "Atlantis Marine",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$25,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]
    client.post(f"/api/leads/{lead_id}/generate-ai")
    client.post(f"/api/leads/{lead_id}/send-email")

    history_resp = client.get("/api/integrations/emails")
    assert history_resp.status_code == 200
    items = history_resp.json()
    assert len(items) > 0

    matching = [item for item in items if item["recipient"] == email]
    assert len(matching) > 0
    assert matching[0]["status"] == "Sent"
    assert matching[0]["gmail_message_id"] is not None


def test_10_failure_and_retry_handling():
    """10. Failure & Retry Handling: Handles Delivery Unknown, prevents blind retry, and reconciles on success."""
    email = f"victor_{uuid.uuid4().hex[:6]}@cybernetics.org"
    payload = {
        "name": "Victor Stone",
        "company": "Cybernetics Inc",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$15,000"
    }
    lead_id = client.post("/api/automation/lead-capture", json=payload).json()["lead_id"]
    client.post(f"/api/leads/{lead_id}/generate-ai")

    # 1. Ambiguous timeout occurred
    client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Delivery Unknown",
        "gmail_message_id": None,
        "error_message": "Gateway timeout waiting for Gmail response"
    })

    # 2. Automated blind re-send is rejected to avoid duplicate delivery
    retry_resp = client.post(f"/api/leads/{lead_id}/send-email")
    assert retry_resp.status_code == 400
    assert "manual reconciliation required" in retry_resp.json()["detail"].lower()

    # 3. Manual reconciliation confirms receipt or re-dispatches
    reconcile_resp = client.post(f"/api/leads/{lead_id}/record-send", json={
        "status": "Sent",
        "gmail_message_id": f"rec_{uuid.uuid4().hex[:8]}",
        "error_message": None
    })
    assert reconcile_resp.status_code == 200
    assert reconcile_resp.json()["email_status"] == "Sent"
