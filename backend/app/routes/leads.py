from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadStats, LeadUpdate
from app.services.gemini_service import analyze_and_draft_lead

router = APIRouter(prefix="/leads", tags=["Leads"])


class StatusUpdatePayload(BaseModel):
    email_status: Optional[str] = None
    priority: Optional[str] = None


@router.get("", response_model=List[LeadResponse])
def get_leads(
    priority: Optional[str] = Query(None, description="Filter by priority: High, Medium, Low"),
    email_status: Optional[str] = Query(None, description="Filter by email status: Pending, Sent, Failed"),
    search: Optional[str] = Query(None, description="Search by name, company, or email"),
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

    return query.order_by(Lead.created_at.desc()).all()


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


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/generate-ai", response_model=LeadResponse)
async def generate_ai_for_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    On-demand AI scoring and email drafting endpoint using Google Gemini.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "phone": lead.phone,
        "service": lead.service,
        "budget": lead.budget,
        "description": lead.description
    }

    ai_result = await analyze_and_draft_lead(lead_data)

    lead.priority = ai_result.get("priority", lead.priority)
    lead.priority_reason = ai_result.get("priority_reason", lead.priority_reason)
    lead.email_subject = ai_result.get("email_subject", lead.email_subject)
    lead.email_body = ai_result.get("email_body", lead.email_body)
    lead.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(lead)
    return lead


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
