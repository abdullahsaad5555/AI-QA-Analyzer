# app/services/ingestion_service.py

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunks import DocumentChunk
from app.models.documents import Document
from app.services.embedding_service import EmbeddingService
from app.utils.text_chunker import chunk_text_as_dicts


class IngestionService:
    @staticmethod
    async def get_document_for_user(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Document | None:
        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def deactivate_document_chunks(
        db: AsyncSession,
        document_id: uuid.UUID,
    ) -> None:
        """
        Soft-deactivate old chunks instead of deleting them.
        Commit is handled by the caller.
        """
        await db.execute(
            update(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.is_active.is_(True),
            )
            .values(is_active=False)
        )

    @staticmethod
    async def ingest_document(
        db: AsyncSession,
        document: Document,
    ) -> dict:
        """
        Chunk the document text, generate embeddings, and store chunks.

        Old chunks are soft-deactivated instead of deleted.
        """
        raw_text = (document.raw_text or "").strip()

        if not raw_text:
            document.status = "failed"
            await db.commit()
            await db.refresh(document)
            return {
                "document_id": str(document.id),
                "status": document.status,
                "chunks_created": 0,
            }

        try:
            # 1) Soft-deactivate previous active chunks for this document
            await IngestionService.deactivate_document_chunks(db, document.id)

            # 2) Chunk text
            chunks = chunk_text_as_dicts(raw_text)

            # 3) Generate embeddings
            embedded_chunks = await EmbeddingService.embed_chunks(chunks)

            # 4) Save new active chunks
            created_count = 0
            for chunk in embedded_chunks:
                db_chunk = DocumentChunk(
                    document_id=document.id,
                    chat_id=document.chat_id,
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    token_count=None,
                    embedding_id=None,
                    metadata_json={
                        "file_name": document.file_name,
                        "source_type": document.source_type,
                        "version": document.version,
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                        "embedding_dimension": chunk["embedding_dimension"],
                        "embedding_provider": chunk["embedding_provider"],
                    },
                    is_active=True,
                )
                db.add(db_chunk)
                created_count += 1

            # 5) Mark document ready
            document.status = "ready"

            await db.commit()
            await db.refresh(document)

            return {
                "document_id": str(document.id),
                "status": document.status,
                "chunks_created": created_count,
            }

        except Exception:
            await db.rollback()
            document.status = "failed"
            await db.commit()
            await db.refresh(document)

            return {
                "document_id": str(document.id),
                "status": document.status,
                "chunks_created": 0,
            }

    @staticmethod
    async def ingest_document_by_id(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        document = await IngestionService.get_document_for_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            return {
                "document_id": str(document_id),
                "status": "not_found",
                "chunks_created": 0,
            }

        return await IngestionService.ingest_document(
            db=db,
            document=document,
        )