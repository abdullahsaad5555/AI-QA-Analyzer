# app/services/embedding_service.py

import asyncio
from typing import Iterable

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """
    Real local embedding service using Sentence Transformers.

    Recommended for your setup:
    - Embedding model: sentence-transformers/all-MiniLM-L6-v2
    - Retrieval pattern: short query -> longer document chunks
    - Vector DB: ChromaDB / FAISS (handled elsewhere)

    Notes:
    - The model is loaded lazily once and reused.
    - Encoding is run in a worker thread because SentenceTransformer.encode(...)
      is synchronous/blocking.
    - Embeddings are normalized for cosine-similarity retrieval.
    """

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_EMBEDDING_PROVIDER = "sentence-transformers"

    _model: SentenceTransformer | None = None

    @staticmethod
    def _get_model_name() -> str:
        """
        Pull model name from settings if available, otherwise use default.
        """
        return getattr(
            settings,
            "EMBEDDING_MODEL_NAME",
            EmbeddingService.DEFAULT_MODEL_NAME,
        )

    @staticmethod
    def _get_device() -> str | None:
        """
        Optional device override from settings.
        Example values: "cpu", "cuda", "mps"
        """
        return getattr(settings, "EMBEDDING_DEVICE", None)

    @staticmethod
    def _get_model() -> SentenceTransformer:
        """
        Lazy singleton loader for the embedding model.
        """
        if EmbeddingService._model is None:
            model_name = EmbeddingService._get_model_name()
            device = EmbeddingService._get_device()

            if device:
                EmbeddingService._model = SentenceTransformer(
                    model_name,
                    device=device,
                )
            else:
                EmbeddingService._model = SentenceTransformer(model_name)

        return EmbeddingService._model

    @staticmethod
    def _safe_to_list(embedding) -> list[float]:
        """
        Convert numpy array / tensor-like / list to a plain Python list[float].
        """
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(x) for x in embedding]

    @staticmethod
    async def embed_text(text: str) -> list[float]:
        """
        Embed a single text item as a query.

        Uses encode_query() when available for asymmetric retrieval setups,
        otherwise falls back to encode().
        """
        model = EmbeddingService._get_model()

        if not text or not text.strip():
            dimension = model.get_sentence_embedding_dimension()
            return [0.0] * dimension

        cleaned = text.strip()

        def _encode() -> list[float]:
            if hasattr(model, "encode_query"):
                embedding = model.encode_query(
                    cleaned,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
            else:
                embedding = model.encode(
                    cleaned,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )

            return EmbeddingService._safe_to_list(embedding)

        return await asyncio.to_thread(_encode)

    @staticmethod
    async def embed_texts(texts: Iterable[str]) -> list[list[float]]:
        """
        Embed multiple text items as document/corpus entries.

        Uses encode_document() when available for asymmetric retrieval setups,
        otherwise falls back to encode().
        """
        text_list = [text.strip() for text in texts if text and text.strip()]

        if not text_list:
            return []

        model = EmbeddingService._get_model()

        def _encode_many() -> list[list[float]]:
            if hasattr(model, "encode_document"):
                embeddings = model.encode_document(
                    text_list,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
            else:
                embeddings = model.encode(
                    text_list,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )

            return [
                EmbeddingService._safe_to_list(embedding)
                for embedding in embeddings
            ]

        return await asyncio.to_thread(_encode_many)

    @staticmethod
    async def embed_chunks(chunks: list[dict]) -> list[dict]:
        """
        Accepts a list of chunk dictionaries and returns the same list enriched
        with embeddings.

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
        if not chunks:
            return []

        contents = [chunk.get("content", "") for chunk in chunks]
        embeddings = await EmbeddingService.embed_texts(contents)

        model = EmbeddingService._get_model()
        model_name = EmbeddingService._get_model_name()
        dimension = model.get_sentence_embedding_dimension()

        enriched_chunks: list[dict] = []

        for chunk, embedding in zip(chunks, embeddings):
            enriched_chunk = {
                **chunk,
                "embedding": embedding,
                "embedding_dimension": dimension,
                "embedding_provider": EmbeddingService.DEFAULT_EMBEDDING_PROVIDER,
                "embedding_model": model_name,
                "vector_db_provider": getattr(settings, "VECTOR_DB_PROVIDER", None),
            }
            enriched_chunks.append(enriched_chunk)

        return enriched_chunks