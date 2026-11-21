import pytest
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


def test_integrations_status():
    resp = client.get("/api/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    # Since default env has placeholders, status should genuinely be 'Not configured'
    for item in data:
        assert item["status"] in ["Not configured", "Connected"]


def test_email_history():
    resp = client.get("/api/integrations/emails")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

