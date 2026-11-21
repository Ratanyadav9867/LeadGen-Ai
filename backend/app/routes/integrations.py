import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.lead import Lead

from app.config import settings

router = APIRouter(prefix="/integrations", tags=["Integrations"])


def check_status(key: str, placeholders: List[str]) -> str:
    # Check settings attribute first, then fallback to os.getenv
    val = getattr(settings, key, None)
    if val is None or not str(val).strip():
        val = os.getenv(key, "").strip()

    val_str = str(val or "").strip()
    if not val_str:
        return "Not configured"

    for p in placeholders:
        if val_str.lower() == p.lower() or val_str.startswith("your_"):
            return "Not configured"

    return "Connected"


@router.get("/status")
def get_integrations_status() -> List[Dict[str, Any]]:
    sheets_status = check_status("GOOGLE_SHEET_ID", ["your_google_sheet_id_here"])
    gemini_status = check_status("GEMINI_API_KEY", ["your_gemini_api_key_here"])
    gmail_status = check_status("GMAIL_SENDER_ADDRESS", ["your_email@gmail.com"])
    n8n_status = check_status("N8N_WEBHOOK_URL", ["your_n8n_webhook_url_here"])

    # Google Forms connects through Sheets or n8n pipeline
    forms_status = "Connected" if (sheets_status == "Connected" or n8n_status == "Connected") else "Not configured"

    return [
        {
            "id": "google-forms",
            "name": "Google Forms",
            "category": "Lead Ingestion",
            "status": forms_status,
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
    from app.models.email_record import EmailRecord

    # Join EmailRecords with Leads for comprehensive dispatch history
    records = db.query(EmailRecord, Lead).outerjoin(Lead, EmailRecord.lead_id == Lead.id).order_by(EmailRecord.created_at.desc()).all()

    if records:
        results = []
        for email_rec, lead in records:
            lead_name = lead.name if lead else "Unknown"
            lead_company = lead.company if lead else "Unknown"
            lead_priority = lead.priority if lead else "Medium"
            results.append({
                "id": email_rec.id,
                "lead_id": email_rec.lead_id,
                "lead_name": lead_name,
                "company": lead_company,
                "recipient": email_rec.recipient,
                "subject": email_rec.subject,
                "body": email_rec.body,
                "status": email_rec.status,
                "gmail_message_id": email_rec.gmail_message_id,
                "error_message": email_rec.error_message,
                "timestamp": (email_rec.sent_at or email_rec.created_at).isoformat(),
                "priority": lead_priority
            })
        return results

    # Fallback to Leads table if no individual EmailRecords exist yet
    leads_with_emails = db.query(Lead).filter(
        (Lead.email_subject.isnot(None)) | (Lead.email_status.in_(["Sent", "Failed", "Pending", "Draft", "Delivery Unknown"]))
    ).order_by(Lead.created_at.desc()).all()

    results = []
    for lead in leads_with_emails:
        results.append({
            "id": lead.id,
            "lead_id": lead.id,
            "lead_name": lead.name,
            "company": lead.company,
            "recipient": lead.email,
            "subject": lead.email_subject or f"Follow-up: {lead.service} inquiry",
            "body": lead.email_body or "Automated AI follow-up draft scheduled for dispatch.",
            "status": lead.email_status,
            "gmail_message_id": getattr(lead, "gmail_message_id", None),
            "error_message": getattr(lead, "error_message", None),
            "timestamp": (lead.processed_at or lead.created_at).isoformat(),
            "priority": lead.priority
        })
    return results

