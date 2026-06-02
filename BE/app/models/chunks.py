# app/models/chunks.py

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base
from app.core.config import settings


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    # Optional metadata
    token_count = Column(Integer, nullable=True)

    # If your vector DB is separate, store a reference here
    embedding_id = Column(Text, nullable=True)

    # Flexible storage for extra metadata:
    # e.g. file_name, page_number, source_type, version, etc.
    metadata_json = Column(JSONB, nullable=True)

    # Useful when re-indexing a document and deactivating old chunks
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
