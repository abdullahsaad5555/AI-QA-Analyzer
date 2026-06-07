# app/api/v1/messages.py

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.config import settings
from app.models.users import User
from app.schemas.message import (
    AssistantAnswerResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.message_service import MessageService
from app.services.rag_service import RAGService

router = APIRouter(tags=["Messages"])


@router.get(
    "/chats/{chat_id}/messages",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
)
async def list_messages(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[MessageResponse]:
    """
    List all messages for a chat owned by the authenticated user.
    """
    messages = await MessageService.list_chat_messages(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    return messages


@router.post(
    "/chats/{chat_id}/messages",
    response_model=AssistantAnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def send_message(
    chat_id: str,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> AssistantAnswerResponse:
    """
    Save the user's message and return either:
    - a static local development response, or
    - a RAG-based response when static mode is disabled.
    """
    # 1) Save user's message
    await MessageService.create_user_message(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        content=payload.content,
    )

    # 2) Local dev static response mode
    if settings.ENABLE_STATIC_CHAT_RESPONSES:
        assistant_text = (
            f"{settings.STATIC_CHAT_RESPONSE_TEXT}\n\n"
            f"Question received: {payload.content}"
        )
        sources = []
    else:
        # 3) Real RAG flow
        rag_result = await RAGService.answer_question(
            db=db,
            chat_id=chat_id,
            user_id=current_user.id,
            question=payload.content,
            top_k=5,
        )
        assistant_text = rag_result["answer"]
        sources = rag_result["sources"]

    # 4) Save assistant message
    await MessageService.create_assistant_message(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        content=assistant_text,
    )

    # 5) Return response
    return AssistantAnswerResponse(
        answer=assistant_text,
        sources=sources,
    )
