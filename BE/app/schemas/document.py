# app/schemas/document.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TextDocumentCreateRequest(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=1,
        example="This is the text I want to upload.",
    )
    file_name: Optional[str] = Field(default=None, example="notes.txt")


class DocumentUpdateRequest(BaseModel):
    raw_text: Optional[str] = Field(default=None, example="Updated document text")
    file_name: Optional[str] = Field(default=None, example="updated_notes.txt")
    mime_type: Optional[str] = Field(default=None, example="text/plain")
    status: Optional[str] = Field(default=None, example="processing")


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    user_id: str
    source_type: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    storage_url: Optional[str] = None
    raw_text: Optional[str] = None
    version: int
    status: str
    created_at: datetime
    updated_at: datetime