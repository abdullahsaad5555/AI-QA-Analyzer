# app/api/v1/messages.py

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.users import User
from app.schemas.message import (
    AssistantAnswerResponse,
    MessageCreateRequest,
    MessageResponse,
    SourceReference,
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
    chat_id: uuid.UUID,
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
    chat_id: uuid.UUID,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> AssistantAnswerResponse:
    """
    Save the user's message, generate a RAG-based answer,
    save the assistant response, and return answer + sources.
    """
    # 1) Save user's message
    await MessageService.create_user_message(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        content=payload.content,
    )

    # 2) Generate grounded answer from RAG pipeline
    rag_result = await RAGService.answer_question(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        question=payload.content,
        top_k=5,
    )

    assistant_text = rag_result["answer"]
    sources = rag_result["sources"]

    # 3) Save assistant message in chat history
    await MessageService.create_assistant_message(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        content=assistant_text,
    )

    # 4) Return answer + sources
    return AssistantAnswerResponse(
        answer=assistant_text,
        sources=[SourceReference(**source) for source in sources],
    )
