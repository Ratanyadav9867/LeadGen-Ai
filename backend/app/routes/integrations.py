import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.lead import Lead

router = APIRouter(prefix="/integrations", tags=["Integrations"])


def check_status(env_var_name: str, placeholder: str) -> str:
    val = os.getenv(env_var_name, "").strip()
    if not val or val == placeholder:
        return "Not configured"
    return "Connected"


@router.get("/status")
def get_integrations_status() -> List[Dict[str, Any]]:
    # Genuine environment checks without exposing credentials
    sheets_status = check_status("GOOGLE_SHEET_ID", "your_google_sheet_id_here")
    gemini_status = check_status("GEMINI_API_KEY", "your_gemini_api_key_here")
    gmail_status = check_status("GMAIL_SENDER_ADDRESS", "your_email@gmail.com")
    n8n_status = check_status("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/leads")

    return [
        {
            "id": "google-forms",
            "name": "Google Forms",
            "category": "Lead Ingestion",
            "status": "Not configured",
            "details": "Trigger on new respondent submission",
            "workflow_step": 1
        },
        {
            "id": "google-sheets",
            "name": "Google Sheets",
            "category": "Spreadsheet Sync",
            "status": sheets_status,
            "details": "Centralized row storage & lead archival",
            "workflow_step": 2
        },
        {
            "id": "n8n",
            "name": "n8n Automation Engine",
            "category": "Orchestration",
            "status": n8n_status,
            "details": "Webhook pipeline & multi-branch conditional flow",
            "workflow_step": 3
        },
        {
            "id": "gemini-ai",
            "name": "Google Gemini AI",
            "category": "AI Qualification",
            "status": gemini_status,
            "details": "Lead scoring, urgency ranking & follow-up draft generation",
            "workflow_step": 4
        },
        {
            "id": "gmail",
            "name": "Gmail Outreach",
            "category": "Email Dispatch",
            "status": gmail_status,
            "details": "Automated personalized email dispatch",
            "workflow_step": 5
        }
    ]


@router.get("/emails")
def get_email_history(db: Session = Depends(get_db)):
    leads_with_emails = db.query(Lead).filter(
        (Lead.email_subject.isnot(None)) | (Lead.email_status.in_(["Sent", "Failed", "Pending"]))
    ).order_by(Lead.created_at.desc()).all()

    results = []
    for lead in leads_with_emails:
        results.append({
            "id": lead.id,
            "lead_name": lead.name,
            "company": lead.company,
            "recipient": lead.email,
            "subject": lead.email_subject or f"Follow-up: {lead.service} inquiry",
            "body": lead.email_body or "Automated AI follow-up draft scheduled for dispatch.",
            "status": lead.email_status,
            "timestamp": (lead.processed_at or lead.created_at).isoformat(),
            "priority": lead.priority
        })
    return results

