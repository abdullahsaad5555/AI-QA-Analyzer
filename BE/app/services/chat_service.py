# app/services/chat_service.py

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat


class ChatService:
    @staticmethod
    async def create_chat(
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
    ) -> Chat:
        chat = Chat(
            user_id=user_id,
            name=name.strip(),
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def list_user_chats(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[Chat]:
        result = await db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_chat_by_id(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Chat:
        result = await db.execute(
            select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
        )
        chat = result.scalar_one_or_none()

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return chat

    @staticmethod
    async def update_chat_name(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        new_name: str,
    ) -> Chat:
        chat = await ChatService.get_chat_by_id(db, chat_id, user_id)

        chat.name = new_name.strip()

        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def delete_chat(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        chat = await ChatService.get_chat_by_id(db, chat_id, user_id)

        await db.delete(chat)
        await db.commit()
