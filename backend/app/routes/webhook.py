import re
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.models.lead import Lead
from app.services.gemini_service import analyze_and_draft_lead

router = APIRouter(prefix="/automation", tags=["Automation"])


class LeadCapturePayload(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of prospect")
    email: str = Field(..., min_length=3, description="Valid email address")
    company: Optional[str] = Field("Independent Client", description="Company or organization")
    phone: Optional[str] = Field(None, description="Contact phone number")
    service: Optional[str] = Field("AI Workflow Automation", description="Service category")
    budget: Optional[str] = Field("$5,000 - $10,000", description="Budget allocation")
    description: Optional[str] = Field(None, description="Project scope or inquiry details")
    spreadsheet_row: Optional[int] = Field(None, description="Original row in Google Sheets")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Prospect name cannot be blank")
        return trimmed

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        cleaned = v.strip().lower()
        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_regex, cleaned):
            raise ValueError(f"Invalid email address format: '{v}'")
        return cleaned


@router.post("/lead-capture")
def capture_lead_from_sheets(
    payload: LeadCapturePayload,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Dedicated Phase 4 lead capture endpoint for n8n Google Sheets automation.
    - Validates data format and required fields
    - Normalizes strings and email
    - Detects duplicates by email
    - Sets Processing status without sending emails
    - Returns 201 Created for new leads, 200 OK for existing duplicates
    """
    normalized_email = payload.email.strip().lower()
    normalized_name = payload.name.strip()
    normalized_company = (payload.company or "Independent Client").strip()
    normalized_service = (payload.service or "AI Workflow Automation").strip()
    normalized_budget = (payload.budget or "$5,000 - $10,000").strip()
    normalized_desc = (payload.description or "").strip() or None

    # Duplicate check
    existing_lead = db.query(Lead).filter(
        Lead.email.ilike(normalized_email)
    ).first()

    if existing_lead:
        response.status_code = status.HTTP_200_OK
        return {
            "success": True,
            "status": "Duplicate",
            "message": "Lead with this email already exists; skipping duplicate creation",
            "lead_id": existing_lead.id,
            "is_duplicate": True,
            "name": existing_lead.name,
            "email": existing_lead.email,
            "company": existing_lead.company,
            "spreadsheet_row": payload.spreadsheet_row
        }

    # Create new lead in database
    new_lead = Lead(
        name=normalized_name,
        company=normalized_company,
        email=normalized_email,
        phone=payload.phone.strip() if payload.phone else None,
        service=normalized_service,
        budget=normalized_budget,
        description=normalized_desc,
        priority="Medium",
        priority_reason="Captured from Google Sheets; awaiting Phase 5 AI scoring.",
        email_status="Pending",
        email_subject=None,
        email_body=None,
        created_at=datetime.utcnow()
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    response.status_code = status.HTTP_201_CREATED
    return {
        "success": True,
        "status": "Processing",
        "message": "Lead successfully captured from Google Sheets into LeadGen AI",
        "lead_id": new_lead.id,
        "is_duplicate": False,
        "name": new_lead.name,
        "email": new_lead.email,
        "company": new_lead.company,
        "service": new_lead.service,
        "budget": new_lead.budget,
        "spreadsheet_row": payload.spreadsheet_row,
        "created_at": new_lead.created_at.isoformat()
    }



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

