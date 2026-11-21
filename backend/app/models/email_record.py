from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.database import Base


class EmailRecord(Base):
    __tablename__ = "email_records"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    recipient = Column(String(150), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(30), default="Draft")  # Draft, Sent, Failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
