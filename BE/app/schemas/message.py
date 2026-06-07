from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, example="What does this document say about payment terms?")


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    user_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SourceReference(BaseModel):
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    file_name: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class AssistantAnswerResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = []