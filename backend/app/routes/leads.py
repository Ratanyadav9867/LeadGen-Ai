from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadStats, LeadUpdate

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=List[LeadResponse])
def get_leads(
    priority: Optional[str] = Query(None, description="Filter by priority: High, Medium, Low"),
    email_status: Optional[str] = Query(None, description="Filter by email status: Pending, Sent, Failed"),
    search: Optional[str] = Query(None, description="Search by name, company, or email"),
    db: Session = Depends(get_db)
):
    query = db.query(Lead)

    if priority:
        query = query.filter(Lead.priority.ilike(priority))

    if email_status:
        query = query.filter(Lead.email_status.ilike(email_status))

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_fmt)) |
            (Lead.company.ilike(search_fmt)) |
            (Lead.email.ilike(search_fmt))
        )

    return query.order_by(Lead.created_at.desc()).all()


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    new_lead = Lead(**payload.model_dump())
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

