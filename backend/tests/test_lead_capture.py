import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_check_duplicate_lead_not_found():
    random_email = f"unknown_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.get(f"/api/leads/check-duplicate?email={random_email}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_duplicate"] is False
    assert data["lead_id"] is None
    assert data["email"] == random_email


def test_lead_capture_valid_new_lead():
    unique_id = uuid.uuid4().hex[:8]
    payload = {
        "name": f"Jessica Pearson {unique_id}",
        "company": "Pearson Specter Litt",
        "email": f"jessica_{unique_id}@psl.com",
        "phone": "+1 (555) 301-4499",
        "service": "AI Workflow Automation",
        "budget": "$15,000 - $30,000",
        "description": "Streamlining law firm intake from Google Forms to internal CRM.",
        "spreadsheet_row": 12
    }

    # 1. Post to lead-capture endpoint
    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["status"] == "Processing"
    assert data["is_duplicate"] is False
    assert data["lead_id"] is not None
    assert data["spreadsheet_row"] == 12

    lead_id = data["lead_id"]

    # 2. Verify duplicate check now detects it
    dup_resp = client.get(f"/api/leads/check-duplicate?email={payload['email']}")
    assert dup_resp.status_code == 200
    dup_data = dup_resp.json()
    assert dup_data["is_duplicate"] is True
    assert dup_data["lead_id"] == lead_id

    # 3. Duplicate submission to lead-capture returns 200 OK with duplicate indicator
    dup_post_resp = client.post("/api/automation/lead-capture", json=payload)
    assert dup_post_resp.status_code == 200
    dup_post_data = dup_post_resp.json()
    assert dup_post_data["is_duplicate"] is True
    assert dup_post_data["status"] == "Duplicate"
    assert dup_post_data["lead_id"] == lead_id


def test_lead_capture_invalid_email():
    payload = {
        "name": "Harvey Specter",
        "company": "PSL",
        "email": "not-an-email",
        "service": "AI Automation",
        "budget": "$10,000"
    }
    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 422
    err_detail = resp.json()["detail"]
    assert any("email" in str(e).lower() for e in err_detail)


def test_lead_capture_blank_name():
    payload = {
        "name": "   ",
        "company": "PSL",
        "email": "harvey@psl.com",
        "service": "AI Automation",
        "budget": "$10,000"
    }
    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 422
    err_detail = resp.json()["detail"]
    assert any("name" in str(e).lower() for e in err_detail)


def test_lead_capture_missing_required_fields():
    # Missing email
    payload = {
        "name": "Mike Ross",
        "company": "PSL"
    }
    resp = client.post("/api/automation/lead-capture", json=payload)
    assert resp.status_code == 422

