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


class EmailRecordResponse(BaseModel):
    id: int
    lead_id: int
    recipient: str
    subject: str
    body: str
    summary: Optional[str] = None
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
