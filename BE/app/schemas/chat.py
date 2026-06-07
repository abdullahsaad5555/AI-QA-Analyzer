# app/schemas/chat.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="Project Alpha Notes")


class ChatUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="Updated Chat Name")


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    created_at: datetime
    updated_at: datetime