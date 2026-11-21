from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    service = Column(String(100), nullable=False)
    budget = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    priority_reason = Column(Text, nullable=True)
    email_status = Column(String(20), default="Pending")  # Pending, Sent, Failed
    email_subject = Column(String(255), nullable=True)
    email_body = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

