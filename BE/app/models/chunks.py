# app/models/chunks.py

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.core.config import settings


def _fk_target(table_name: str, column_name: str = "id") -> str:
    """
    Build a ForeignKey target that works for both:
    - PostgreSQL with schema: public.documents.id
    - SQLite/local dev without schema: documents.id
    """
    return (
        f"{settings.DB_SCHEMA}.{table_name}.{column_name}"
        if settings.DB_SCHEMA
        else f"{table_name}.{column_name}"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = {"schema": settings.DB_SCHEMA} if settings.DB_SCHEMA else {}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    document_id = Column(
        String,
        ForeignKey(_fk_target("documents"), ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chat_id = Column(
        String,
        ForeignKey(_fk_target("chats"), ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    # Optional metadata
    token_count = Column(Integer, nullable=True)

    # If your vector DB is separate, store a reference here
    embedding_id = Column(Text, nullable=True)

    # Portable JSON column:
    # - JSON for SQLite/other DBs
    # - JSONB for PostgreSQL
    metadata_json = Column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)

    # Useful when re-indexing a document and deactivating old chunks
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)