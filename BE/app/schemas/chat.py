# app/schemas/chat.py

from datetime import datetime

from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="Project Alpha Notes")


class ChatUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="Updated Chat Name")


class ChatResponse(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
