import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.gemini_service import (
    validate_ai_response,
    classify_lead_priority,
    generate_gemini_email,
)
from app.models.lead import Lead
from app.models.email_record import EmailRecord

client = TestClient(app)


def test_01_valid_lead_generates_email():
    """1. Valid lead generates an email with subject, body, summary, and deterministic priority."""
    unique_email = f"sarah_{uuid.uuid4().hex[:6]}@cyberdyne.com"
    lead_payload = {
        "name": "Sarah Connor",
        "company": "Cyberdyne Systems",
        "email": unique_email,
        "service": "AI Workflow Automation",
        "budget": "$15,000 - $30,000",
        "description": "Automating logistics freight quotes and dispatcher intake."
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    assert create_resp.status_code == 201
    lead_id = create_resp.json()["lead_id"]

    # Trigger AI generation
    ai_resp = client.post(f"/api/leads/{lead_id}/generate-ai")
    assert ai_resp.status_code == 200
    data = ai_resp.json()

    assert data["email_status"] == "Draft"
    assert "Cyberdyne" in data["email_subject"]
    assert "Sarah" in data["email_body"]
    assert data["summary"] is not None
    assert len(data["summary"]) > 5
    assert data["priority"] == "High"


def test_02_two_different_leads_generate_personalized_responses():
    """2. Two different leads generate distinct personalized responses matching their requirements."""
    lead1 = {
        "name": "Bruce Wayne",
        "company": "Wayne Enterprises",
        "email": f"bruce_{uuid.uuid4().hex[:6]}@wayne.com",
        "service": "CRM Lead Scoring",
        "budget": "$25,000+",
        "description": "High security defense technology inquiry."
    }
    lead2 = {
        "name": "Peter Parker",
        "company": "Daily Bugle Media",
        "email": f"peter_{uuid.uuid4().hex[:6]}@bugle.com",
        "service": "Google Workspace Integration",
        "budget": "$1,000 - $2,500",
        "description": "Sync photography submissions to Google Drive."
    }

    resp1 = client.post("/api/automation/lead-capture", json=lead1)
    resp2 = client.post("/api/automation/lead-capture", json=lead2)

    ai1 = client.post(f"/api/leads/{resp1.json()['lead_id']}/generate-ai").json()
    ai2 = client.post(f"/api/leads/{resp2.json()['lead_id']}/generate-ai").json()

    assert ai1["email_subject"] != ai2["email_subject"]
    assert "Wayne" in ai1["email_subject"]
    assert "Daily Bugle" in ai2["email_subject"]
    assert ai1["priority"] == "High"
    assert ai2["priority"] == "Low"


def test_03_missing_customer_information_handled_safely():
    """3. Missing customer information (empty description, company) is handled cleanly without crashing."""
    lead_payload = {
        "name": "Clark Kent",
        "company": "Daily Planet",
        "email": f"clark_{uuid.uuid4().hex[:6]}@planet.com",
        "service": "AI Workflow Automation",
        "budget": "$5,000 - $10,000",
        "description": ""  # Missing/empty description
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    assert create_resp.status_code == 201
    lead_id = create_resp.json()["lead_id"]

    ai_resp = client.post(f"/api/leads/{lead_id}/generate-ai")
    assert ai_resp.status_code == 200
    data = ai_resp.json()
    assert data["email_subject"] is not None
    assert data["email_body"] is not None
    assert "Daily Planet" in data["email_body"]


def test_04_malformed_gemini_json_rejected():
    """4. Malformed Gemini JSON is rejected by validation logic and API."""
    # Missing 'summary'
    with pytest.raises(ValueError, match="missing or empty required field: 'summary'"):
        validate_ai_response({"subject": "Test Subject", "body": "Test Body"})

    # Empty string subject
    with pytest.raises(ValueError, match="missing or empty required field: 'subject'"):
        validate_ai_response({"subject": "   ", "body": "Test Body", "summary": "Test Summary"})

    # Non-dictionary input
    with pytest.raises(ValueError, match="JSON object"):
        validate_ai_response("just a string")

    # FastAPI endpoint rejects malformed AI response payload with 422
    invalid_payload = {"subject": "", "body": "Valid body text here", "summary": "Valid summary"}
    post_resp = client.post("/api/leads/1/ai-response", json=invalid_payload)
    assert post_resp.status_code == 422


def test_05_gemini_api_timeout_handling():
    """5. Gemini API timeout is caught gracefully and falls back to safe deterministic response."""
    test_data = {
        "name": "Barry Allen",
        "company": "S.T.A.R. Labs",
        "email": f"barry_{uuid.uuid4().hex[:6]}@starlabs.com",
        "service": "AI Workflow Automation",
        "budget": "$10,000",
        "description": "Particle accelerator monitoring."
    }

    with patch("app.config.settings.GEMINI_API_KEY", "mock-active-key"):
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timed out")):
            result = asyncio.run(generate_gemini_email(test_data))
            assert result["subject"] is not None
            assert result["body"] is not None
            assert "S.T.A.R. Labs" in result["subject"]
            assert result["source"] == "fallback_after_api_error"


def test_06_gemini_api_rate_limit_handling():
    """6. Gemini API rate limit (429) triggers backoff and falls back cleanly without crashing."""
    test_data = {
        "name": "Victor Stone",
        "company": "Cybernetics Inc",
        "email": f"victor_{uuid.uuid4().hex[:6]}@cybernetics.org",
        "service": "CRM Lead Scoring",
        "budget": "$20,000",
        "description": "Neural interface integration."
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "RESOURCE_EXHAUSTED"

    with patch("app.config.settings.GEMINI_API_KEY", "mock-active-key"):
        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            result = asyncio.run(generate_gemini_email(test_data))
            assert result["subject"] is not None
            assert result["body"] is not None
            assert "Cybernetics Inc" in result["subject"]
            assert result["source"] == "fallback_after_api_error"


def test_07_duplicate_workflow_execution_idempotency():
    """7. Duplicate workflow execution does not create duplicate EmailRecord entries (Idempotency)."""
    unique_email = f"hal_{uuid.uuid4().hex[:6]}@ferris.com"
    lead_payload = {
        "name": "Hal Jordan",
        "company": "Ferris Aircraft",
        "email": unique_email,
        "service": "CRM Lead Scoring",
        "budget": "$10,000 - $25,000",
        "description": "Flight telemetry logging."
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    lead_id = create_resp.json()["lead_id"]

    ai_payload = {
        "subject": "Ferris Aircraft CRM Architecture",
        "body": "Dear Hal, thank you for reaching out regarding flight telemetry logging...",
        "summary": "Inquiry for CRM telemetry scoring."
    }

    # First save
    resp1 = client.post(f"/api/leads/{lead_id}/ai-response", json=ai_payload)
    assert resp1.status_code == 200
    record_id_1 = resp1.json()["email_record_id"]

    # Duplicate retry with same payload
    resp2 = client.post(f"/api/leads/{lead_id}/ai-response", json=ai_payload)
    assert resp2.status_code == 200
    record_id_2 = resp2.json()["email_record_id"]

    assert record_id_1 == record_id_2
    assert resp2.json()["email_status"] == "Draft"


def test_08_database_saves_generated_drafts():
    """8. Database saves generated drafts in EmailRecord with Draft status and links to Lead."""
    unique_email = f"diana_{uuid.uuid4().hex[:6]}@themyscira.org"
    lead_payload = {
        "name": "Diana Prince",
        "company": "Themyscira Cultural Center",
        "email": unique_email,
        "service": "Google Workspace Integration",
        "budget": "$5,000 - $10,000",
        "description": "Sync exhibition registration forms."
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    lead_id = create_resp.json()["lead_id"]

    save_resp = client.post(f"/api/leads/{lead_id}/ai-response", json={
        "subject": "Themyscira Cultural Center Integration Architecture",
        "body": "Dear Diana, thank you for reaching out...",
        "summary": "Exhibition registration sync request."
    })
    assert save_resp.status_code == 200
    data = save_resp.json()
    assert data["lead_id"] == lead_id
    assert data["email_status"] == "Draft"
    assert data["processing_status"] == "Completed"


def test_09_google_sheets_payload_structure_verification():
    """9. Verifies endpoint response contains all fields required for Google Sheets Phase 5 update."""
    unique_email = f"arthur_{uuid.uuid4().hex[:6]}@atlantis.org"
    lead_payload = {
        "name": "Arthur Curry",
        "company": "Atlantis Marine Research",
        "email": unique_email,
        "service": "AI Workflow Automation",
        "budget": "$15,000",
        "description": "Marine sonar data ingestion."
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    lead_id = create_resp.json()["lead_id"]

    ai_payload = {
        "subject": "Atlantis Marine Sonar Automation | LeadGen AI",
        "body": "Dear Arthur, thank you for connecting...",
        "summary": "Sonar data automation project."
    }
    resp = client.post(f"/api/leads/{lead_id}/ai-response", json=ai_payload)
    assert resp.status_code == 200
    data = resp.json()

    # Required Google Sheets update fields
    assert "subject" in data
    assert "body" in data
    assert "priority" in data
    assert "processing_status" in data
    assert "email_status" in data
    assert "processed_at" in data

    assert data["processing_status"] == "Completed"
    assert data["email_status"] == "Draft"


def test_10_dashboard_displays_generated_content_via_api():
    """10. Dashboard API (GET /api/leads/{id}) returns AI generated subject, body, priority, and draft status."""
    unique_email = f"oliver_{uuid.uuid4().hex[:6]}@queen.com"
    lead_payload = {
        "name": "Oliver Queen",
        "company": "Queen Industries",
        "email": unique_email,
        "service": "AI Workflow Automation",
        "budget": "$30,000+",
        "description": "Supply chain logistics intake."
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    lead_id = create_resp.json()["lead_id"]

    # Generate draft
    client.post(f"/api/leads/{lead_id}/generate-ai")

    # Fetch as dashboard does
    get_resp = client.get(f"/api/leads/{lead_id}")
    assert get_resp.status_code == 200
    lead_data = get_resp.json()

    assert lead_data["name"] == "Oliver Queen"
    assert lead_data["company"] == "Queen Industries"
    assert lead_data["email_status"] == "Draft"
    assert lead_data["email_subject"] is not None
    assert lead_data["email_body"] is not None
    assert lead_data["priority"] == "High"


def test_11_no_email_is_sent_during_phase_5():
    """11. Strict verification: Generated emails remain in 'Draft' status and are NEVER sent during Phase 5."""
    unique_email = f"jordan_{uuid.uuid4().hex[:6]}@ferriscorp.com"
    lead_payload = {
        "name": "Carol Ferris",
        "company": "Ferris Corp",
        "email": unique_email,
        "service": "AI Workflow Automation",
        "budget": "$15,000 - $30,000"
    }
    create_resp = client.post("/api/automation/lead-capture", json=lead_payload)
    lead_id = create_resp.json()["lead_id"]

    # Generate AI
    ai_resp = client.post(f"/api/leads/{lead_id}/generate-ai")
    assert ai_resp.status_code == 200

    # Retrieve lead and verify email_status is 'Draft', NOT 'Sent'
    lead_check = client.get(f"/api/leads/{lead_id}").json()
    assert lead_check["email_status"] == "Draft"
    assert lead_check["email_status"] != "Sent"

    # Verify that attempting to overwrite a 'Sent' lead fails with 409 Conflict
    client.patch(f"/api/leads/{lead_id}/status", json={"email_status": "Sent"})
    conflict_resp = client.post(f"/api/leads/{lead_id}/ai-response", json={
        "subject": "Attempt Overwrite",
        "body": "This should not be saved",
        "summary": "Illegal overwrite attempt"
    })
    assert conflict_resp.status_code == 409
