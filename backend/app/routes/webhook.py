from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.models.lead import Lead
from app.services.gemini_service import analyze_and_draft_lead

router = APIRouter(prefix="/automation", tags=["Automation"])


class WebhookLeadPayload(BaseModel):
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    service: str
    budget: str
    description: Optional[str] = None
    auto_qualify: bool = True


@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def handle_n8n_lead_webhook(payload: WebhookLeadPayload, db: Session = Depends(get_db)):
    """
    Webhook endpoint designed for n8n, Google Forms, and Google Sheets ingestion.
    Performs duplicate detection, Gemini AI qualification, and SQLite persistence.
    """
    # 1. Duplicate prevention check
    existing_lead = db.query(Lead).filter(
        Lead.email == payload.email,
        Lead.company == payload.company
    ).first()

    # 2. AI Lead Qualification & Email Drafting
    ai_result = await analyze_and_draft_lead(payload.model_dump())

    if existing_lead:
        # Update existing record if new inbound inquiry
        existing_lead.service = payload.service
        existing_lead.budget = payload.budget
        existing_lead.description = payload.description or existing_lead.description
        existing_lead.priority = ai_result.get("priority", existing_lead.priority)
        existing_lead.priority_reason = ai_result.get("priority_reason", existing_lead.priority_reason)
        existing_lead.email_subject = ai_result.get("email_subject", existing_lead.email_subject)
        existing_lead.email_body = ai_result.get("email_body", existing_lead.email_body)
        existing_lead.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_lead)
        target_lead = existing_lead
        is_duplicate = True
    else:
        new_lead = Lead(
            name=payload.name,
            company=payload.company,
            email=payload.email,
            phone=payload.phone,
            service=payload.service,
            budget=payload.budget,
            description=payload.description,
            priority=ai_result.get("priority", "Medium"),
            priority_reason=ai_result.get("priority_reason"),
            email_status="Pending",
            email_subject=ai_result.get("email_subject"),
            email_body=ai_result.get("email_body"),
            processed_at=datetime.utcnow()
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        target_lead = new_lead
        is_duplicate = False

    return {
        "success": True,
        "message": "Lead ingested and qualified successfully by LeadGen AI",
        "lead_id": target_lead.id,
        "is_duplicate_updated": is_duplicate,
        "name": target_lead.name,
        "company": target_lead.company,
        "email": target_lead.email,
        "priority": target_lead.priority,
        "priority_reason": target_lead.priority_reason,
        "email_status": target_lead.email_status,
        "email_subject": target_lead.email_subject,
        "email_body": target_lead.email_body,
        "ai_engine": ai_result.get("source", "leadgen_ai")
    }
