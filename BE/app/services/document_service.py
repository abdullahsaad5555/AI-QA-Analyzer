# app/services/document_service.py

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat
from app.models.documents import Document


class DocumentService:
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
    async def create_text_document(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        raw_text: str,
        file_name: str | None = None,
    ) -> Document:
        """
        Create a text-based document for a user's chat.
        """
        await DocumentService._get_owned_chat(db, chat_id, user_id)

        document = Document(
            chat_id=chat_id,
            user_id=user_id,
            source_type="text",
            file_name=file_name,
            mime_type="text/plain",
            raw_text=raw_text.strip(),
            version=1,
            status="processing",
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def list_chat_documents(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Document]:
        """
        List all documents for a given chat owned by the current user.
        """
        await DocumentService._get_owned_chat(db, chat_id, user_id)

        result = await db.execute(
            select(Document)
            .where(
                Document.chat_id == chat_id,
                Document.user_id == user_id,
            )
            .order_by(Document.updated_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_document_by_id(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Document:
        """
        Get one document by ID only if it belongs to the current user.
        """
        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return document

    @staticmethod
    async def update_document(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        raw_text: str | None = None,
        file_name: str | None = None,
        mime_type: str | None = None,
        status_value: str | None = None,
    ) -> Document:
        """
        Update document fields. If raw_text is updated, bump version and set status to processing
        so the re-indexing pipeline can run again.
        """
        document = await DocumentService.get_document_by_id(db, document_id, user_id)

        text_changed = False

        if raw_text is not None:
            cleaned_text = raw_text.strip()
            if cleaned_text != (document.raw_text or ""):
                document.raw_text = cleaned_text
                document.version += 1
                document.status = "processing"
                text_changed = True

        if file_name is not None:
            document.file_name = file_name

        if mime_type is not None:
            document.mime_type = mime_type

        if status_value is not None and not text_changed:
            document.status = status_value

        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Delete a document if it belongs to the current user.
        """
        document = await DocumentService.get_document_by_id(db, document_id, user_id)

        await db.delete(document)
        await db.commit()
