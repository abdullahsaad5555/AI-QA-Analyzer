# app/services/rag_service.py

import uuid
from collections.abc import AsyncIterator
from typing import Any

import chromadb
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chats import Chat
from app.services.embedding_service import EmbeddingService


class RAGService:
    _chroma_collection = None

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
    def _get_chroma_collection():
        """
        Lazy-load the ChromaDB collection used for chunk retrieval.
        """
        if settings.VECTOR_DB_PROVIDER != "chromadb":
            raise RuntimeError(
                "RAGService is currently configured for ChromaDB retrieval only. "
                f"Current VECTOR_DB_PROVIDER={settings.VECTOR_DB_PROVIDER}"
            )

        if RAGService._chroma_collection is None:
            client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            RAGService._chroma_collection = client.get_or_create_collection(
                name=settings.VECTOR_DB_COLLECTION
            )

        return RAGService._chroma_collection

    @staticmethod
    async def retrieve_relevant_chunks(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the top-k most relevant chunks for the query
        from ChromaDB using the pre-ingested chunk embeddings.
        """
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty",
            )

        # Ensure the chat exists and belongs to the user
        await RAGService._get_owned_chat(db, chat_id, user_id)

        collection = RAGService._get_chroma_collection()
        query_embedding = await EmbeddingService.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"chat_id": str(chat_id)},
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks: list[dict[str, Any]] = []

        for content, metadata, distance in zip(documents, metadatas, distances):
            metadata = metadata or {}

            retrieved_chunks.append(
                {
                    "document_id": metadata.get("document_id"),
                    "chat_id": metadata.get("chat_id"),
                    "file_name": metadata.get("file_name"),
                    "source_type": metadata.get("source_type"),
                    "document_version": metadata.get("version"),
                    "document_status": metadata.get("status"),
                    "chunk_index": metadata.get("chunk_index"),
                    "content": content or "",
                    "start_char": metadata.get("start_char"),
                    "end_char": metadata.get("end_char"),
                    "chunk_id": metadata.get("chunk_id"),
                    "retrieval_distance": distance,
                    "metadata": {
                        "file_name": metadata.get("file_name"),
                        "source_type": metadata.get("source_type"),
                        "version": metadata.get("version"),
                        "status": metadata.get("status"),
                        "start_char": metadata.get("start_char"),
                        "end_char": metadata.get("end_char"),
                    },
                }
            )

        return retrieved_chunks

    @staticmethod
    def _build_answer_from_chunks(
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:
        """
        Build a simple grounded answer from retrieved chunks.
        This is still a placeholder answer builder until a real LLM answer layer
        is connected.
        """
        if not chunks:
            return (
                "I could not find any relevant content in the documents attached "
                "to this chat."
            )

        answer_lines = [
            f"Question: {question}",
            "",
            "Based on the most relevant document content I found:",
            "",
        ]

        for index, chunk in enumerate(chunks, start=1):
            file_name = chunk.get("file_name") or "Untitled document"
            content = (chunk.get("content") or "").strip()
            chunk_index = chunk.get("chunk_index")

            answer_lines.append(
                f"{index}. Source: {file_name} | Chunk #{chunk_index}"
            )
            answer_lines.append(content)
            answer_lines.append("")

        answer_lines.append(
            "Note: This is a retrieval-based response. "
            "A real LLM-generated answer layer can be added next."
        )

        return "\n".join(answer_lines).strip()

    @staticmethod
    async def answer_question(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        question: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        End-to-end RAG flow:
        1. Retrieve top relevant chunks from ChromaDB
        2. Build a grounded answer from those chunks
        3. Return answer + source references
        """
        retrieved_chunks = await RAGService.retrieve_relevant_chunks(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            query=question,
            top_k=top_k,
        )

        answer = RAGService._build_answer_from_chunks(question, retrieved_chunks)

        sources = [
            {
                "document_id": chunk.get("document_id"),
                "chunk_id": chunk.get("chunk_id"),
                "file_name": chunk.get("file_name"),
                "metadata": {
                    **(chunk.get("metadata") or {}),
                    "chunk_index": chunk.get("chunk_index"),
                    "retrieval_distance": chunk.get("retrieval_distance"),
                },
            }
            for chunk in retrieved_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    async def stream_answer_question(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        question: str,
        top_k: int = 5,
        chunk_size: int = 40,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Streaming-friendly helper.

        Current behavior:
        - retrieves relevant chunks from ChromaDB
        - builds the full answer
        - yields it gradually in small pieces

        This does NOT yet stream token-by-token from your generator model.
        It only streams the final built answer in chunks.
        """
        retrieved_chunks = await RAGService.retrieve_relevant_chunks(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            query=question,
            top_k=top_k,
        )

        answer = RAGService._build_answer_from_chunks(question, retrieved_chunks)

        sources = [
            {
                "document_id": chunk.get("document_id"),
                "chunk_id": chunk.get("chunk_id"),
                "file_name": chunk.get("file_name"),
                "metadata": {
                    **(chunk.get("metadata") or {}),
                    "chunk_index": chunk.get("chunk_index"),
                    "retrieval_distance": chunk.get("retrieval_distance"),
                },
            }
            for chunk in retrieved_chunks
        ]

        for start in range(0, len(answer), chunk_size):
            delta = answer[start:start + chunk_size]
            yield {
                "type": "chunk",
                "delta": delta,
            }

        yield {
            "type": "done",
            "answer": answer,
            "sources": sources,
        }