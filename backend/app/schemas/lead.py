from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class LeadBase(BaseModel):
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    service: str
    budget: str
    description: Optional[str] = None
    priority: str = "Medium"
    priority_reason: Optional[str] = None
    email_status: str = "Pending"
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    gmail_message_id: Optional[str] = None
    error_message: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    service: Optional[str] = None
    budget: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    priority_reason: Optional[str] = None
    email_status: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    gmail_message_id: Optional[str] = None
    error_message: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LeadStats(BaseModel):
    total_leads: int
    new_leads: int
    high_priority_leads: int
    emails_sent: int
    emails_failed: int
