from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EmailRecord(Base):
    __tablename__ = "email_records"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, nullable=False)
    sender = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
