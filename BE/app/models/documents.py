# app/models/documents.py

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text

from app.core.database import Base
from app.core.config import settings


def _fk_target(table_name: str, column_name: str = "id") -> str:
    """
    Build a ForeignKey target that works for both:
    - PostgreSQL with schema: public.chats.id
    - SQLite/local dev without schema: chats.id
    """
    return (
        f"{settings.DB_SCHEMA}.{table_name}.{column_name}"
        if settings.DB_SCHEMA
        else f"{table_name}.{column_name}"
    )


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": settings.DB_SCHEMA} if settings.DB_SCHEMA else {}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    chat_id = Column(
        String,
        ForeignKey(_fk_target("chats"), ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        String,
        ForeignKey(_fk_target("users"), ondelete="CASCADE"),
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