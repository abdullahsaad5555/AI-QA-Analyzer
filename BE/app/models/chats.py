# app/models/chats.py

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey

from app.core.database import Base
from app.core.config import settings


def _fk_target(table_name: str, column_name: str = "id") -> str:
    """
    Build a ForeignKey target that works for both:
    - PostgreSQL with schema: public.users.id
    - SQLite/local dev without schema: users.id
    """
    return (
        f"{settings.DB_SCHEMA}.{table_name}.{column_name}"
        if settings.DB_SCHEMA
        else f"{table_name}.{column_name}"
    )


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"schema": settings.DB_SCHEMA} if settings.DB_SCHEMA else {}

    # SQLite-friendly local-dev ID storage
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(
        String,
        ForeignKey(_fk_target("users"), ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
