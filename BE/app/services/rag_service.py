# app/services/rag_service.py

import math
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat
from app.models.documents import Document
from app.services.embedding_service import EmbeddingService
from app.utils.text_chunker import chunk_text_as_dicts


class RAGService:
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
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    @staticmethod
    async def _load_chat_documents(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Document]:
        """
        Load all documents for a chat owned by the current user.
        """
        await RAGService._get_owned_chat(db, chat_id, user_id)

        result = await db.execute(
            select(Document).where(
                Document.chat_id == chat_id,
                Document.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def build_chunk_corpus(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """
        Load documents for a chat and split them into chunk dictionaries.

        Each returned chunk includes document-level metadata.
        """
        documents = await RAGService._load_chat_documents(db, chat_id, user_id)

        corpus: list[dict[str, Any]] = []

        for document in documents:
            raw_text = (document.raw_text or "").strip()
            if not raw_text:
                continue

            chunks = chunk_text_as_dicts(raw_text)

            for chunk in chunks:
                corpus.append(
                    {
                        "document_id": str(document.id),
                        "chat_id": str(document.chat_id),
                        "file_name": document.file_name,
                        "source_type": document.source_type,
                        "document_version": document.version,
                        "document_status": document.status,
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                        "metadata": {
                            "file_name": document.file_name,
                            "source_type": document.source_type,
                            "version": document.version,
                            "status": document.status,
                            "start_char": chunk["start_char"],
                            "end_char": chunk["end_char"],
                        },
                    }
                )

        return corpus

    @staticmethod
    async def retrieve_relevant_chunks(
        db: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the top-k most relevant chunks for the query.

        Uses the placeholder EmbeddingService for now.
        """
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty",
            )

        corpus = await RAGService.build_chunk_corpus(db, chat_id, user_id)

        if not corpus:
            return []

        query_embedding = await EmbeddingService.embed_text(query)

        scored_chunks: list[dict[str, Any]] = []

        for chunk in corpus:
            chunk_embedding = await EmbeddingService.embed_text(chunk["content"])
            score = RAGService._cosine_similarity(query_embedding, chunk_embedding)

            scored_chunks.append(
                {
                    **chunk,
                    "score": score,
                }
            )

        scored_chunks.sort(key=lambda item: item["score"], reverse=True)
        return scored_chunks[:top_k]

    @staticmethod
    def _build_answer_from_chunks(
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:
        """
        Build a simple grounded answer from retrieved chunks.

        This is a placeholder answer builder until a real LLM is connected.
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
            content = chunk.get("content", "").strip()

            answer_lines.append(
                f"{index}. Source: {file_name} | Chunk #{chunk['chunk_index']}"
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
        End-to-end MVP RAG flow:
        1. Retrieve top relevant chunks
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
                "document_id": chunk["document_id"],
                "chunk_id": None,  # not persisted yet in document_chunks table
                "file_name": chunk.get("file_name"),
                "metadata": {
                    **(chunk.get("metadata") or {}),
                    "chunk_index": chunk["chunk_index"],
                    "score": chunk["score"],
                },
            }
            for chunk in retrieved_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }
