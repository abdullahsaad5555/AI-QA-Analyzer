# app/api/v1/chats.py

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.users import User
from app.schemas.chat import (
    ChatCreateRequest,
    ChatResponse,
    ChatUpdateRequest,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get(
    "",
    response_model=list[ChatResponse],
    status_code=status.HTTP_200_OK,
)
async def list_chats(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    List all chats for the authenticated user.
    """
    chats = await ChatService.list_user_chats(
        db=db,
        user_id=current_user.id,
    )
    return chats


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    payload: ChatCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new chat for the authenticated user.
    """
    chat = await ChatService.create_chat(
        db=db,
        user_id=current_user.id,
        name=payload.name,
    )
    return chat


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def get_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single chat by ID for the authenticated user.
    """
    chat = await ChatService.get_chat_by_id(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    return chat


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def update_chat(
    chat_id: str,
    payload: ChatUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Rename/update a chat for the authenticated user.
    """
    chat = await ChatService.update_chat_name(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        new_name=payload.name,
    )
    return chat


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a chat for the authenticated user.
    """
    await ChatService.delete_chat(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
