# app/api/v1/documents.py

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.users import User
from app.schemas.document import (
    DocumentResponse,
    DocumentUpdateRequest,
    TextDocumentCreateRequest,
)
from app.services.document_service import DocumentService

router = APIRouter(tags=["Documents"])


@router.get(
    "/chats/{chat_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    chat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    List all documents for a chat owned by the authenticated user.
    """
    documents = await DocumentService.list_chat_documents(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    return documents


@router.post(
    "/chats/{chat_id}/documents/text",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_text_document(
    chat_id: uuid.UUID,
    payload: TextDocumentCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a text-based document for a chat.
    """
    document = await DocumentService.create_text_document(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        raw_text=payload.raw_text,
        file_name=payload.file_name,
    )
    return document


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single document by ID for the authenticated user.
    """
    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    return document


@router.patch(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update a document. If raw_text changes, the service will bump the version
    and mark the document as 'processing' for re-indexing.
    """
    document = await DocumentService.update_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        raw_text=payload.raw_text,
        file_name=payload.file_name,
        mime_type=payload.mime_type,
        status_value=payload.status,
    )
    return document


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document for the authenticated user.
    """
    await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
