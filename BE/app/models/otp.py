# app/models/otp.py

import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.config import settings


class EmailOTP(Base):
    __tablename__ = "email_otps"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, nullable=False, index=True)

    # Store hashed OTP, not raw OTP
    code_hash = Column(String, nullable=False)

    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    consumed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def build_expiry():
        return datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
