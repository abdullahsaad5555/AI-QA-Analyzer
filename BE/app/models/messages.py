# app/models/messages.py

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.config import settings


class Message(Base):
    __tablename__ = "messages"
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

    # 'user' | 'assistant' | 'system'
    role = Column(String, nullable=False, index=True)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
