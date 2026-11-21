from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.lead import Lead
from app.models.email_record import EmailRecord
from app.schemas.lead import LeadCreate, LeadResponse, LeadStats, LeadUpdate
from app.schemas.email_record import AIResponsePayload, RecordSendPayload
from app.services.gemini_service import (
    generate_gemini_email,
    classify_lead_priority,
    analyze_and_draft_lead,
)
from app.services.gmail_service import validate_email_eligibility, send_via_gmail_api

router = APIRouter(prefix="/leads", tags=["Leads"])


class StatusUpdatePayload(BaseModel):
    email_status: Optional[str] = None
    priority: Optional[str] = None


@router.get("", response_model=List[LeadResponse])
def get_leads(
    priority: Optional[str] = Query(None, description="Filter by priority: High, Medium, Low"),
    email_status: Optional[str] = Query(None, description="Filter by email status: Pending, Sent, Failed"),
    search: Optional[str] = Query(None, description="Search by name, company, or email"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Maximum items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Lead)

    if priority and priority != "All":
        query = query.filter(Lead.priority.ilike(priority))

    if email_status and email_status != "All":
        query = query.filter(Lead.email_status.ilike(email_status))

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_fmt)) |
            (Lead.company.ilike(search_fmt)) |
            (Lead.email.ilike(search_fmt)) |
            (Lead.service.ilike(search_fmt))
        )

    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead_dict = payload.model_dump()
    # Automatically execute AI qualification if not provided
    if not lead_dict.get("priority_reason") or not lead_dict.get("email_body"):
        ai_result = await analyze_and_draft_lead(lead_dict)
        lead_dict["priority"] = ai_result.get("priority", lead_dict.get("priority", "Medium"))
        lead_dict["priority_reason"] = ai_result.get("priority_reason")
        lead_dict["email_subject"] = ai_result.get("email_subject")
        lead_dict["email_body"] = ai_result.get("email_body")
        lead_dict["processed_at"] = datetime.utcnow()

    new_lead = Lead(**lead_dict)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead


@router.get("/stats", response_model=LeadStats)
def get_lead_stats(db: Session = Depends(get_db)):
    total = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.email_status == "Pending").count()
    high_priority = db.query(Lead).filter(Lead.priority == "High").count()
    emails_sent = db.query(Lead).filter(Lead.email_status == "Sent").count()
    emails_failed = db.query(Lead).filter(Lead.email_status == "Failed").count()

    return LeadStats(
        total_leads=total,
        new_leads=new_leads,
        high_priority_leads=high_priority,
        emails_sent=emails_sent,
        emails_failed=emails_failed
    )


@router.get("/check-duplicate")
def check_duplicate_lead(
    email: str = Query(..., description="Email to check for duplication"),
    db: Session = Depends(get_db)
):
    norm_email = email.strip().lower()
    lead = db.query(Lead).filter(Lead.email.ilike(norm_email)).first()
    if lead:
        return {
            "is_duplicate": True,
            "lead_id": lead.id,
            "email": lead.email,
            "name": lead.name,
            "company": lead.company,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "email_status": lead.email_status,
            "priority": lead.priority
        }
    return {
        "is_duplicate": False,
        "lead_id": None,
        "email": norm_email
    }


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/save-ai-response")
@router.post("/{lead_id}/ai-response")
def save_ai_response(
    lead_id: int,
    payload: AIResponsePayload,
    db: Session = Depends(get_db)
):
    """
    Saves an AI-generated subject, body, and summary associated with the specified lead.
    - Sets email_status to 'Draft' (not sent)
    - Saves in EmailRecord model
    - Prevents duplicate email records on retry (idempotent)
    - Strictly prevents overwriting previously sent emails (returns 409)
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Guard: Do not overwrite previously sent email records
    if lead.email_status == "Sent":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot overwrite AI response for a lead whose email has already been sent."
        )

    # Retry safety / Idempotency check:
    existing_draft = db.query(EmailRecord).filter(
        EmailRecord.lead_id == lead.id,
        EmailRecord.status == "Draft",
        EmailRecord.subject == payload.subject,
        EmailRecord.body == payload.body
    ).first()

    if existing_draft:
        return {
            "success": True,
            "message": "AI draft response already saved (idempotent retry)",
            "lead_id": lead.id,
            "email_record_id": existing_draft.id,
            "recipient": lead.email,
            "subject": existing_draft.subject,
            "body": existing_draft.body,
            "summary": existing_draft.summary,
            "priority": lead.priority,
            "priority_reason": lead.priority_reason,
            "email_status": "Draft",
            "processing_status": "Completed",
            "processed_at": lead.processed_at.isoformat() if lead.processed_at else None
        }

    # Create new EmailRecord in Draft status
    email_rec = EmailRecord(
        lead_id=lead.id,
        recipient=lead.email,
        subject=payload.subject,
        body=payload.body,
        summary=payload.summary,
        status="Draft"
    )
    db.add(email_rec)

    # Update Lead model
    lead.email_subject = payload.subject
    lead.email_body = payload.body
    lead.email_status = "Draft"
    lead.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(email_rec)
    db.refresh(lead)

    return {
        "success": True,
        "message": "AI response saved successfully in draft status",
        "lead_id": lead.id,
        "email_record_id": email_rec.id,
        "recipient": lead.email,
        "subject": lead.email_subject,
        "body": lead.email_body,
        "summary": payload.summary,
        "priority": lead.priority,
        "priority_reason": lead.priority_reason,
        "email_status": "Draft",
        "processing_status": "Completed",
        "processed_at": lead.processed_at.isoformat()
    }


@router.post("/{lead_id}/generate-ai")
async def generate_ai_for_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    On-demand AI email drafting endpoint using Google Gemini.
    - Sets priority deterministically via FastAPI
    - Synthesizes personalized subject, body, summary via Gemini
    - Saves in EmailRecord model as Draft
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.email_status == "Sent":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot re-generate AI response for a lead whose email has already been sent."
        )

    # 1. Authoritative deterministic priority classification in FastAPI
    priority, reason = classify_lead_priority(lead.budget, lead.description, lead.company)
    lead.priority = priority
    lead.priority_reason = reason

    # 2. Call Gemini service for personalized subject, body, summary
    lead_data = {
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "phone": lead.phone,
        "service": lead.service,
        "budget": lead.budget,
        "description": lead.description
    }
    ai_result = await generate_gemini_email(lead_data)

    # 3. Save EmailRecord
    email_rec = EmailRecord(
        lead_id=lead.id,
        recipient=lead.email,
        subject=ai_result["subject"],
        body=ai_result["body"],
        summary=ai_result["summary"],
        status="Draft"
    )
    db.add(email_rec)

    lead.email_subject = ai_result["subject"]
    lead.email_body = ai_result["body"]
    lead.email_status = "Draft"
    lead.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(email_rec)
    db.refresh(lead)

    return {
        "success": True,
        "lead_id": lead.id,
        "email_record_id": email_rec.id,
        "priority": lead.priority,
        "priority_reason": lead.priority_reason,
        "email_status": lead.email_status,
        "email_subject": lead.email_subject,
        "email_body": lead.email_body,
        "summary": ai_result["summary"],
        "processed_at": lead.processed_at.isoformat()
    }


@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(lead_id: int, payload: StatusUpdatePayload, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if payload.email_status:
        lead.email_status = payload.email_status
    if payload.priority:
        lead.priority = payload.priority

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return None


@router.get("/{lead_id}/send-eligibility")
def check_send_eligibility(lead_id: int, db: Session = Depends(get_db)):
    """
    Evaluates Phase 6 delivery preconditions:
    - Lead existence, valid email address
    - Presence of non-empty AI draft subject and body
    - Verification that outreach has not already been marked Sent
    - Exclusion of ambiguous Delivery Unknown states
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    email_rec = db.query(EmailRecord).filter(EmailRecord.lead_id == lead.id).order_by(EmailRecord.created_at.desc()).first()
    is_eligible, reason = validate_email_eligibility(lead, email_rec)

    return {
        "lead_id": lead.id,
        "eligible": is_eligible,
        "reason": reason,
        "recipient": lead.email,
        "email_status": lead.email_status,
        "has_draft": bool(lead.email_subject and lead.email_body),
        "subject": lead.email_subject,
        "body": lead.email_body
    }


@router.post("/{lead_id}/send-email")
async def send_email_for_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Dispatches the generated follow-up draft through Gmail.
    - Pre-send eligibility check prevents duplicate sends
    - Sets 'Sending' status before network call
    - Enforces accurate state transitions: 'Sent', 'Failed', or 'Delivery Unknown'
    - Updates Lead and EmailRecord models atomically
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    email_rec = db.query(EmailRecord).filter(EmailRecord.lead_id == lead.id).order_by(EmailRecord.created_at.desc()).first()

    is_eligible, reason = validate_email_eligibility(lead, email_rec)
    if not is_eligible:
        if "already been" in (reason or "").lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate send prevented: {reason}"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lead not eligible for sending: {reason}"
        )

    # Set sending state
    lead.email_status = "Sending"
    db.commit()

    # Dispatch via Gmail API
    result = await send_via_gmail_api(
        recipient=lead.email,
        subject=lead.email_subject,
        body=lead.email_body
    )

    send_status = result["status"]
    msg_id = result.get("gmail_message_id")
    error_msg = result.get("error")
    now = datetime.utcnow()

    # Update EmailRecord
    if not email_rec:
        email_rec = EmailRecord(
            lead_id=lead.id,
            recipient=lead.email,
            subject=lead.email_subject,
            body=lead.email_body,
            status=send_status,
            gmail_message_id=msg_id,
            error_message=error_msg,
            sent_at=now if send_status == "Sent" else None
        )
        db.add(email_rec)
    else:
        email_rec.status = send_status
        email_rec.gmail_message_id = msg_id
        email_rec.error_message = error_msg
        if send_status == "Sent":
            email_rec.sent_at = now

    # Update Lead
    lead.email_status = send_status
    lead.gmail_message_id = msg_id
    lead.error_message = error_msg
    lead.processed_at = now

    db.commit()
    db.refresh(lead)
    if email_rec:
        db.refresh(email_rec)

    return {
        "success": send_status == "Sent",
        "lead_id": lead.id,
        "email_record_id": email_rec.id if email_rec else None,
        "recipient": lead.email,
        "subject": lead.email_subject,
        "email_status": lead.email_status,
        "gmail_message_id": lead.gmail_message_id,
        "error_message": lead.error_message,
        "sent_at": email_rec.sent_at.isoformat() if (email_rec and email_rec.sent_at) else None
    }


@router.post("/{lead_id}/record-send")
def record_email_send_result(lead_id: int, payload: RecordSendPayload, db: Session = Depends(get_db)):
    """
    Dedicated endpoint for n8n Gmail workflow integration.
    Records delivery outcome (Sent, Failed, Delivery Unknown) and Gmail message ID.
    Enforces idempotency and prevents overwriting already-sent records.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Idempotency check: if already Sent
    if lead.email_status == "Sent" and payload.status == "Sent":
        if payload.gmail_message_id and lead.gmail_message_id == payload.gmail_message_id:
            return {
                "success": True,
                "message": "Send confirmation already recorded (idempotent)",
                "lead_id": lead.id,
                "email_status": lead.email_status,
                "gmail_message_id": lead.gmail_message_id,
                "processed_at": lead.processed_at.isoformat() if lead.processed_at else None
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot record send: Email has already been dispatched to this lead."
        )

    email_rec = db.query(EmailRecord).filter(EmailRecord.lead_id == lead.id).order_by(EmailRecord.created_at.desc()).first()
    now = datetime.utcnow()

    if not email_rec:
        email_rec = EmailRecord(
            lead_id=lead.id,
            recipient=lead.email,
            subject=lead.email_subject or f"Inquiry regarding {lead.service}",
            body=lead.email_body or "Automated response.",
            status=payload.status,
            gmail_message_id=payload.gmail_message_id,
            error_message=payload.error_message,
            sent_at=now if payload.status == "Sent" else None
        )
        db.add(email_rec)
    else:
        email_rec.status = payload.status
        if payload.gmail_message_id:
            email_rec.gmail_message_id = payload.gmail_message_id
        if payload.error_message:
            email_rec.error_message = payload.error_message
        if payload.status == "Sent":
            email_rec.sent_at = now

    # Update Lead model
    lead.email_status = payload.status
    if payload.gmail_message_id:
        lead.gmail_message_id = payload.gmail_message_id
    if payload.error_message:
        lead.error_message = payload.error_message
    lead.processed_at = now

    db.commit()
    db.refresh(lead)
    if email_rec:
        db.refresh(email_rec)

    return {
        "success": payload.status == "Sent",
        "lead_id": lead.id,
        "email_record_id": email_rec.id if email_rec else None,
        "recipient": lead.email,
        "subject": lead.email_subject,
        "priority": lead.priority,
        "email_status": lead.email_status,
        "processing_status": "Completed" if payload.status == "Sent" else ("Failed" if payload.status == "Failed" else "Ambiguous"),
        "gmail_message_id": lead.gmail_message_id,
        "error_message": lead.error_message,
        "processed_at": lead.processed_at.isoformat()
    }

