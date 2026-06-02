# app/services/embedding_service.py

import hashlib
from typing import Iterable

from app.core.config import settings


class EmbeddingService:
    """
    MVP embedding service.

    For now, this generates deterministic pseudo-embeddings from text using SHA-256.
    This is NOT a semantic embedding model, but it is useful for:
    - local development
    - testing ingestion pipelines
    - validating DB/vector storage flow

    Later, replace `embed_text()` with a real provider call.
    """

    DEFAULT_DIMENSION = 32

    @staticmethod
    def _hash_to_vector(text: str, dimension: int = DEFAULT_DIMENSION) -> list[float]:
        """
        Convert text into a deterministic pseudo-vector using repeated SHA-256 hashing.
        Output values are normalized to floats between 0 and 1.
        """
        if not text:
            return [0.0] * dimension

        values: list[float] = []
        seed = text.encode("utf-8")

        while len(values) < dimension:
            digest = hashlib.sha256(seed).digest()

            # Convert digest bytes into normalized floats
            for byte in digest:
                values.append(byte / 255.0)
                if len(values) >= dimension:
                    break

            seed = digest

        return values[:dimension]

    @staticmethod
    async def embed_text(text: str, dimension: int | None = None) -> list[float]:
        """
        Generate an embedding vector for a single text input.

        This currently returns a deterministic pseudo-embedding.
        """
        dim = dimension or EmbeddingService.DEFAULT_DIMENSION
        return EmbeddingService._hash_to_vector(text=text, dimension=dim)

    @staticmethod
    async def embed_texts(
        texts: Iterable[str],
        dimension: int | None = None,
    ) -> list[list[float]]:
        """
        Generate embedding vectors for multiple text inputs.
        """
        dim = dimension or EmbeddingService.DEFAULT_DIMENSION
        return [
            EmbeddingService._hash_to_vector(text=text, dimension=dim)
            for text in texts
        ]

    @staticmethod
    async def embed_chunks(
        chunks: list[dict],
        dimension: int | None = None,
    ) -> list[dict]:
        """
        Accepts a list of chunk dictionaries and returns the same list enriched with embeddings.

        Expected chunk format:
        [
            {
                "chunk_index": 0,
                "content": "some text",
                "start_char": 0,
                "end_char": 1000
            }
        ]
        """
        dim = dimension or EmbeddingService.DEFAULT_DIMENSION
        enriched_chunks: list[dict] = []

        for chunk in chunks:
            content = chunk.get("content", "")
            embedding = EmbeddingService._hash_to_vector(content, dimension=dim)

            enriched_chunk = {
                **chunk,
                "embedding": embedding,
                "embedding_dimension": dim,
                "embedding_provider": settings.VECTOR_DB_PROVIDER,
            }
            enriched_chunks.append(enriched_chunk)

        return enriched_chunks
