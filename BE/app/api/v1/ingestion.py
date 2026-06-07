# app/api/v1/ingestion.py

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.users import User
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

router = APIRouter(tags=["Ingestion"])


@router.post(
    "/documents/{document_id}/ingest",
    status_code=status.HTTP_200_OK,
)
async def ingest_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Trigger ingestion for a single document owned by the authenticated user.
    """
    result = await IngestionService.ingest_document_by_id(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    return result


@router.post(
    "/chats/{chat_id}/ingest",
    status_code=status.HTTP_200_OK,
)
async def ingest_chat_documents(
    chat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Trigger ingestion for all documents in a chat owned by the authenticated user.
    """
    documents = await DocumentService.list_chat_documents(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )

    results: list[dict[str, Any]] = []

    for document in documents:
        ingestion_result = await IngestionService.ingest_document(
            db=db,
            document=document,
        )
        results.append(ingestion_result)

    return {
        "chat_id": str(chat_id),
        "documents_found": len(documents),
        "results": results,
    }