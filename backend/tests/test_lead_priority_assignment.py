import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.services.gemini_service import classify_lead_priority, validate_ai_response
from app.models.lead import Lead
from app.database import SessionLocal

client = TestClient(app)


def test_example_1_high_priority_classification():
    """Example 1: Budget 25000+, urgent requirement -> High Priority."""
    priority, reason = classify_lead_priority(
        budget="25000+",
        description="Urgent requirement for automating the company's sales operations.",
        company="Global Enterprise Inc.",
        service="AI Workflow Automation"
    )
    assert priority == "High"
    assert "urgent" in reason.lower() or "investment" in reason.lower() or "opportunity" in reason.lower()


def test_example_2_medium_priority_classification():
    """Example 2: Budget 10000, Custom Web App, standard functionality -> Medium Priority."""
    priority, reason = classify_lead_priority(
        budget="10000",
        description="Looking for a business website with standard functionality.",
        company="Local Retail LLC",
        service="Custom Web App"
    )
    assert priority == "Medium"
    assert "standard" in reason.lower() or "moderate" in reason.lower()


def test_example_3_low_priority_classification():
    """Example 3: Budget 5000, CRM Lead Scoring, exploratory -> Low Priority."""
    priority, reason = classify_lead_priority(
        budget="5000",
        description="Just exploring available options without a confirmed requirement.",
        company="Solo Freelancer",
        service="CRM Lead Scoring"
    )
    assert priority == "Low"
    assert "exploratory" in reason.lower() or "entry-level" in reason.lower()


def test_customer_cannot_override_priority_in_lead_capture():
    """Customer-facing /api/automation/lead-capture must NOT allow customer to choose priority."""
    email = f"customer_{uuid.uuid4().hex[:6]}@enterprise.com"
    payload = {
        "name": "Customer User",
        "company": "Customer Enterprise",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$35,000",
        "description": "Urgent enterprise-wide deployment needed.",
        "priority": "Low"  # Attempted override by malicious or misguided customer
    }
    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    # Priority MUST be assigned by backend AI engine (High), NOT customer's Low
    assert data["priority"] == "High"
    assert data["priority_reason"] is not None


def test_customer_cannot_override_priority_in_webhook():
    """Customer-facing /api/automation/webhook must evaluate priority via AI engine."""
    email = f"webhook_{uuid.uuid4().hex[:6]}@urgentcorp.com"
    payload = {
        "name": "Urgent Lead",
        "company": "Urgent Corp",
        "email": email,
        "service": "AI Workflow Automation",
        "budget": "$50,000",
        "description": "Critical emergency rollout required immediately.",
        "priority": "Low"  # Customer attempted override
    }
    resp = client.post("/api/automation/webhook", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["priority"] == "High"


def test_admin_can_manually_select_priority():
    """Admin manual creation via POST /api/leads allows manual priority selection."""
    email = f"admin_manual_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Manual VIP",
        "company": "VIP Partner",
        "email": email,
        "service": "Custom Web App",
        "budget": "$5,000",
        "description": "Small budget but strategic partner.",
        "priority": "High"  # Admin chooses High priority despite small budget
    }
    resp = client.post("/api/leads", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["priority"] == "High"
    assert data["priority_source"] == "manual"
    assert "manual" in data["priority_reason"].lower()


def test_admin_auto_priority_calls_ai_engine():
    """Admin creation without priority (or None) automatically triggers AI priority classification."""
    email = f"admin_auto_{uuid.uuid4().hex[:6]}@exploration.com"
    payload = {
        "name": "Curious Prospect",
        "company": "Browsing Co",
        "email": email,
        "service": "CRM Lead Scoring",
        "budget": "$3,000",
        "description": "Just exploring available options without a confirmed requirement."
    }
    resp = client.post("/api/leads", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["priority"] == "Low"
    assert data["priority_source"] == "ai"


def test_validate_ai_response_priority_fallback():
    """If Gemini returns invalid priority, validate_ai_response safely falls back to Medium."""
    invalid_data = {
        "priority": "SuperUrgentP0",
        "priority_reason": "Random reason",
        "subject": "Valid Subject",
        "body": "Valid body text that is long enough.",
        "summary": "Valid summary"
    }
    res = validate_ai_response(invalid_data)
    assert res["priority"] == "Medium"


def test_save_ai_response_updates_priority():
    """POST /api/leads/{id}/ai-response updates priority and priority_reason."""
    email = f"ai_resp_{uuid.uuid4().hex[:6]}@test.com"
    lead_resp = client.post("/api/automation/lead-capture", json={
        "name": "Test Prospect",
        "company": "Test LLC",
        "email": email,
        "service": "Custom Web App",
        "budget": "$10,000",
        "description": "Standard business portal."
    })
    lead_id = lead_resp.json()["lead_id"]

    # Save AI draft with explicit priority
    save_resp = client.post(f"/api/leads/{lead_id}/ai-response", json={
        "subject": "Follow-up proposal for Test LLC",
        "body": "Dear Test Prospect, thank you for contacting us...",
        "summary": "Business portal inquiry",
        "priority": "Medium",
        "priority_reason": "Moderate budget with standard scope"
    })
    assert save_resp.status_code == 200

    # Verify updated on lead
    get_resp = client.get(f"/api/leads/{lead_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["priority"] == "Medium"
    assert get_resp.json()["priority_reason"] == "Moderate budget with standard scope"


def test_high_priority_filter_returns_only_high():
    """GET /api/leads?priority=High returns only High priority records."""
    resp = client.get("/api/leads?priority=High&limit=50")
    assert resp.status_code == 200
    leads = resp.json()
    for l in leads:
        assert l["priority"] == "High"
