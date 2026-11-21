from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime


class AIResponsePayload(BaseModel):
    subject: str = Field(..., min_length=3, description="Personalized email subject")
    body: str = Field(..., min_length=10, description="Complete professional email body")
    summary: str = Field(..., min_length=3, description="Short summary of customer requirement")

    @field_validator("subject", "body", "summary")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")
        return trimmed


class RecordSendPayload(BaseModel):
    status: str = Field(..., description="Delivery status: Sent, Failed, Delivery Unknown")
    gmail_message_id: Optional[str] = Field(None, description="Gmail message ID when confirmed by API")
    error_message: Optional[str] = Field(None, description="Detailed error description on failure")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        trimmed = v.strip()
        allowed = ["Sent", "Failed", "Delivery Unknown", "Sending", "Draft"]
        if trimmed not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return trimmed


class EmailRecordResponse(BaseModel):
    id: int
    lead_id: int
    recipient: str
    subject: str
    body: str
    summary: Optional[str] = None
    status: str
    gmail_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
