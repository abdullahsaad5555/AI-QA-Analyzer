# app/api/v1/documents.py

import uuid

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.users import User
from app.schemas.document import (
    DocumentResponse,
    DocumentUpdateRequest,
    TextDocumentCreateRequest,
)
from app.services.document_service import DocumentService
from app.services.file_parser_service import FileParserService
from app.services.ingestion_service import IngestionService

router = APIRouter(tags=["Documents"])


@router.get(
    "/chats/{chat_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
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
    chat_id: str,
    payload: TextDocumentCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Create a text-based document for a chat and immediately ingest it.
    """
    document = await DocumentService.create_text_document(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        raw_text=payload.raw_text,
        file_name=payload.file_name,
    )

    await IngestionService.ingest_document(
        db=db,
        document=document,
    )

    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document.id,
        user_id=current_user.id,
    )

    return document


@router.post(
    "/chats/{chat_id}/documents/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    chat_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Upload a TXT, PDF, or DOCX file for a chat,
    convert it into text, and immediately ingest it.
    """
    parsed = await FileParserService.parse_upload_file(file)

    document = await DocumentService.create_text_document(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        raw_text=parsed["raw_text"],
        file_name=parsed["file_name"],
    )

    # Preserve detected mime type after creation
    if parsed["mime_type"]:
        document = await DocumentService.update_document(
            db=db,
            document_id=document.id,
            user_id=current_user.id,
            mime_type=parsed["mime_type"],
        )

    await IngestionService.ingest_document(
        db=db,
        document=document,
    )

    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document.id,
        user_id=current_user.id,
    )

    return document


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
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
    document_id: str,
    payload: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Update a document. If raw_text changes, the service will bump the version
    and mark the document as 'processing', then ingestion will run again.
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

    await IngestionService.ingest_document(
        db=db,
        document=document,
    )

    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document.id,
        user_id=current_user.id,
    )

    return document


@router.post(
    "/documents/{document_id}/ingest",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def ingest_document(
    document_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Manually trigger ingestion for a document owned by the authenticated user.
    Useful for retries/debugging/reprocessing.
    """
    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    await IngestionService.ingest_document(
        db=db,
        document=document,
    )

    document = await DocumentService.get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    return document


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id:str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Delete a document for the authenticated user.
    """
    await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)