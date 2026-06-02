# app/utils/text_chunker.py

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    start_char: int
    end_char: int


def normalize_text(text: str) -> str:
    """
    Normalize text before chunking:
    - strip leading/trailing whitespace
    - collapse repeated whitespace/newlines into single spaces
    """
    if not text:
        return ""

    return " ".join(text.split()).strip()


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """
    Split text into overlapping character-based chunks.

    Args:
        text: Raw input text
        chunk_size: Max characters per chunk
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        list[TextChunk]
    """
    cleaned_text = normalize_text(text)

    if not cleaned_text:
        return []

    size = chunk_size or settings.CHUNK_SIZE
    overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if overlap >= size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(start + size, text_length)
        chunk_content = cleaned_text[start:end].strip()

        if chunk_content:
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=chunk_content,
                    start_char=start,
                    end_char=end,
                )
            )
            chunk_index += 1

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def chunk_text_as_dicts(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict]:
    """
    Helper if you want plain dictionaries instead of dataclass objects.
    Useful before storing chunk metadata in DB.
    """
    chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return [
        {
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
        }
        for chunk in chunks
    ]