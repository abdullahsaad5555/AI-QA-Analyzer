# app/services/ingestion_service.py#

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunks import DocumentChunk
from app.models.documents import Document
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
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
        Chunk the document text, generate embeddings, write them to ChromaDB,
        and store active chunks in SQL.

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

            # 4) Prepare vector-store records
            vector_records = []
            for chunk in embedded_chunks:
                chunk_ref_id = f"{document.id}:v{document.version}:chunk:{chunk['chunk_index']}"

                vector_records.append(
                    {
                        "id": chunk_ref_id,
                        "embedding": chunk["embedding"],
                        "document": chunk["content"],
                        "metadata": {
                            "chunk_id": chunk_ref_id,
                            "document_id": str(document.id),
                            "chat_id": str(document.chat_id),
                            "chunk_index": chunk["chunk_index"],
                            "file_name": document.file_name,
                            "source_type": document.source_type,
                            "version": document.version,
                            "status": document.status,
                            "start_char": chunk["start_char"],
                            "end_char": chunk["end_char"],
                            "embedding_dimension": chunk["embedding_dimension"],
                            "embedding_provider": chunk["embedding_provider"],
                            "embedding_model": chunk.get("embedding_model"),
                        },
                    }
                )

            # 5) Write vectors into vector DB and get ids back
            stored_ids = await VectorStoreService.upsert_records(vector_records)
            stored_id_by_chunk_index = {
                record["metadata"]["chunk_index"]: record_id
                for record, record_id in zip(vector_records, stored_ids)
            }

            # 6) Save new active chunks in SQL
            created_count = 0
            for chunk in embedded_chunks:
                db_chunk = DocumentChunk(
                    document_id=document.id,
                    chat_id=document.chat_id,
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    token_count=None,
                    embedding_id=stored_id_by_chunk_index.get(chunk["chunk_index"]),
                    metadata_json={
                        "chunk_id": stored_id_by_chunk_index.get(chunk["chunk_index"]),
                        "file_name": document.file_name,
                        "source_type": document.source_type,
                        "version": document.version,
                        "status": document.status,
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                        "embedding_dimension": chunk["embedding_dimension"],
                        "embedding_provider": chunk["embedding_provider"],
                        "embedding_model": chunk.get("embedding_model"),
                    },
                    is_active=True,
                )
                db.add(db_chunk)
                created_count += 1

            # 7) Mark document ready
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
