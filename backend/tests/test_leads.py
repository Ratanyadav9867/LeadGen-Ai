import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_leads():
    new_lead = {
        "name": "Sarah Connor",
        "company": "Cyberdyne Systems",
        "email": "sarah@cyberdyne.com",
        "phone": "+1-555-0199",
        "service": "AI Workflow Automation",
        "budget": "$10,000 - $25,000",
        "description": "Looking to automate client onboarding pipelines using n8n and AI agents.",
        "priority": "High",
        "priority_reason": "High budget and urgent timeline.",
        "email_status": "Pending",
        "email_subject": "Optimizing Cyberdyne Workflows with LeadGen AI",
        "email_body": "Hi Sarah, thank you for contacting us regarding AI automation..."
    }

    create_resp = client.post("/api/leads", json=new_lead)
    assert create_resp.status_code == 201
    lead_id = create_resp.json()["id"]

    # Retrieve lead
    get_resp = client.get(f"/api/leads/{lead_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Sarah Connor"
    assert get_resp.json()["priority"] == "High"

    # Verify stats
    stats_resp = client.get("/api/leads/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["total_leads"] >= 1


def test_ai_generation_endpoint():
    new_lead = {
        "name": "Bruce Wayne",
        "company": "Wayne Enterprises",
        "email": "bruce@waynecorp.com",
        "service": "CRM Lead Scoring & Ingestion",
        "budget": "$25,000+",
        "description": "Need enterprise AI scoring pipeline for high-volume defense and tech inquiries."
    }
    create_resp = client.post("/api/leads", json=new_lead)
    assert create_resp.status_code == 201
    lead_id = create_resp.json()["id"]

    # Trigger AI generation
    ai_resp = client.post(f"/api/leads/{lead_id}/generate-ai")
    assert ai_resp.status_code == 200
    data = ai_resp.json()
    assert data["priority"] == "High"
    assert data["priority_reason"] is not None
    assert "Wayne Enterprises" in data["email_subject"]
    assert "Bruce" in data["email_body"]


def test_lead_status_update():
    new_lead = {
        "name": "Diana Prince",
        "company": "Themyscira Global",
        "email": "diana@themyscira.org",
        "service": "Google Workspace Integration",
        "budget": "$5,000 - $10,000",
        "description": "Automate consultation requests."
    }
    create_resp = client.post("/api/leads", json=new_lead)
    lead_id = create_resp.json()["id"]

    # Update status to Sent
    patch_resp = client.patch(f"/api/leads/{lead_id}/status", json={"email_status": "Sent"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["email_status"] == "Sent"


def test_automation_webhook_and_deduplication():
    test_id = str(uuid.uuid4())[:8]
    webhook_payload = {
        "name": f"Arthur Dent {test_id}",
        "company": f"Megadodo Publications {test_id}",
        "email": f"arthur_{test_id}@megadodo.com",
        "phone": "+44 20 7946 0912",
        "service": "AI Workflow Automation",
        "budget": "$10,000 - $25,000",
        "description": "Looking to automate publication review queries."
    }

    # First webhook submission
    resp1 = client.post("/api/automation/webhook", json=webhook_payload)
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["success"] is True
    assert data1["is_duplicate_updated"] is False
    assert data1["priority"] == "High"
    lead_id = data1["lead_id"]

    # Duplicate submission from same email/company
    resp2 = client.post("/api/automation/webhook", json=webhook_payload)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["success"] is True
    assert data2["is_duplicate_updated"] is True
    assert data2["lead_id"] == lead_id


def test_integrations_status():
    resp = client.get("/api/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    for item in data:
        assert item["status"] in ["Not configured", "Connected"]


def test_email_history():
    resp = client.get("/api/integrations/emails")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
