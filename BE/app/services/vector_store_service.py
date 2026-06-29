# app/services/vector_store_service.py

import asyncio
from typing import Any

import chromadb

from app.core.config import settings


class VectorStoreService:
    """
    ChromaDB-backed vector store service for ingestion and retrieval.

    This version is intentionally aligned with the current project state:
    - VECTOR_DB_PROVIDER is expected to be "chromadb"
    - embeddings are generated externally by EmbeddingService
    - ingestion writes vectors once
    - retrieval queries by vector + metadata filter (chat_id)
    """

    _collection = None

    @staticmethod
    def _ensure_chromadb_enabled() -> None:
        if settings.VECTOR_DB_PROVIDER != "chromadb":
            raise RuntimeError(
                "VectorStoreService is configured only for ChromaDB in this version. "
                f"Current VECTOR_DB_PROVIDER={settings.VECTOR_DB_PROVIDER}"
            )

    @staticmethod
    def _get_collection():
        """
        Lazily create/load the Chroma collection.
        """
        VectorStoreService._ensure_chromadb_enabled()

        if VectorStoreService._collection is None:
            client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            VectorStoreService._collection = client.get_or_create_collection(
                name=settings.VECTOR_DB_COLLECTION
            )

        return VectorStoreService._collection

    @staticmethod
    async def upsert_records(records: list[dict[str, Any]]) -> list[str]:
        """
        Upsert records into ChromaDB.

        Expected record format:
        {
            "id": "stable-string-id",
            "embedding": [float, ...],
            "document": "chunk text",
            "metadata": {...}
        }

        Returns:
            list[strds that were written
        """
        if not records:
            return []

        collection = VectorStoreService._get_collection     
        ids = [record["id"] for record in records]
        embeddings = [record["embedding"] for record in records]
        documents = [record["document"] for record in records]
        metadatas = [record["metadata"] for record in records]

        def _upsert():
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

        await asyncio.to_thread(_upsert)
        return ids

    @staticmethod
    async def query_records(
        *,
        query_embedding: list[float],
        chat_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Query ChromaDB for the nearest chunk embeddings filtered by chat_id.

        Returns a normalized list of chunk dictionaries that matches what
        RAGService expects.
        """
        collection = VectorStoreService._get_collection()

        def _query():
            return collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"chat_id": chat_id},
                include=["documents", "metadatas", "distances"],
            )

        results = await asyncio.to_thread(_query)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_items: list[dict[str, Any]] = []

        for content, metadata, distance in zip(documents, metadatas, distances):
            metadata = metadata or {}

            retrieved_items.append(
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

        return retrieved_items
