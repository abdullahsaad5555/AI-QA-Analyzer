# app/models/documents.py

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.config import settings


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 'upload' or 'text'
    source_type = Column(String, nullable=False)

    # File-related metadata (nullable for pasted text)
    file_name = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    storage_url = Column(Text, nullable=True)

    # Raw text content (for pasted text or extracted text if needed)
    raw_text = Column(Text, nullable=True)

    # Used when document is updated and re-indexed
    version = Column(Integer, default=1, nullable=False)

    # processing | ready | failed
    status = Column(String, default="processing", nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
