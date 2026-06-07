# app/services/message_service.py

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat
from app.models.messages import Message


class MessageService:
    @staticmethod
    async def _get_owned_chat(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Chat:
        """
        Ensure the chat exists and belongs to the current user.
        """
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
    async def create_message(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        content: str,
    ) -> Message:
        """
        Create a message in a chat after verifying ownership.
        """
        await MessageService._get_owned_chat(db, chat_id, user_id)

        message = Message(
            chat_id=chat_id,
            user_id=user_id,
            role=role,
            content=content.strip(),
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def create_user_message(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> Message:
        """
        Convenience method for creating a user message.
        """
        return await MessageService.create_message(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            role="user",
            content=content,
        )

    @staticmethod
    async def create_assistant_message(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> Message:
        """
        Convenience method for creating an assistant message.
        Note:
        The assistant response is stored in the same user's chat history.
        """
        return await MessageService.create_message(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            role="assistant",
            content=content,
        )

    @staticmethod
    async def list_chat_messages(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Message]:
        """
        List all messages for a chat owned by the current user.
        """
        await MessageService._get_owned_chat(db, chat_id, user_id)

        result = await db.execute(
            select(Message)
            .where(
                Message.chat_id == chat_id,
                Message.user_id == user_id,
            )
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_message_by_id(
        db: AsyncSession,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Message:
        """
        Get one message by ID only if it belongs to the current user.
        """
        result = await db.execute(
            select(Message).where(
                Message.id == message_id,
                Message.user_id == user_id,
            )
        )
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return message

    @staticmethod
    async def delete_message(
        db: AsyncSession,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Delete a message if it belongs to the current user.
        """
        message = await MessageService.get_message_by_id(
            db=db,
            message_id=message_id,
            user_id=user_id,
        )

        await db.delete(message)
        await db.commit()