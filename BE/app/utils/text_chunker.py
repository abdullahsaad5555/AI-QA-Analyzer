# app/utils/text_chunker.py

import re
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
    Normalize text before chunking while preserving structure:
    - normalize line endings
    - strip trailing spaces on each line
    - collapse excessive blank lines
    - keep paragraph boundaries intact
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse 3+ blank lines into 2 blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _split_paragraphs(text: str) -> list[str]:
    """
    Split text into paragraph-like blocks.
    """
    if not text:
        return []

    parts = re.split(r"\n\s*\n", text)
    return [part.strip() for part in parts if part.strip()]


def _split_sentences(text: str) -> list[str]:
    """
    Lightweight sentence splitter.
    Falls back to the whole text if no good split is found.
    """
    if not text:
        return []

    # Split on punctuation followed by whitespace
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    parts = [part.strip() for part in parts if part.strip()]

    return parts if parts else [text.strip()]


def _hard_split(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Final fallback when text is still too large:
    split by raw character windows with overlap.
    """
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def _split_large_unit(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Recursively split a large unit:
    - first by sentences
    - then by hard character fallback if needed
    """
    if len(text) <= chunk_size:
        return [text.strip()]

    sentence_parts = _split_sentences(text)

    if len(sentence_parts) == 1 and len(sentence_parts[0]) > chunk_size:
        return _hard_split(sentence_parts[0], chunk_size, chunk_overlap)

    chunks: list[str] = []
    current = ""

    for sentence in sentence_parts:
        if not current:
            candidate = sentence
        else:
            candidate = f"{current} {sentence}"

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())

        if len(sentence) > chunk_size:
            chunks.extend(_hard_split(sentence, chunk_size, chunk_overlap))
            current = ""
        else:
            current = sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """
    Split text into structure-aware chunks.

    Strategy:
    1. Preserve paragraphs where possible
    2. Pack paragraphs into chunks up to chunk_size
    3. If a paragraph is too large, split it by sentence groups
    4. If a sentence is still too large, fall back to hard character splitting

    Note:
    - chunk_size and chunk_overlap are still character-based here
    - this is a practical improvement over naive fixed slicing
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

    paragraph_blocks = _split_paragraphs(cleaned_text)
    built_chunks: list[str] = []
    current = ""

    for block in paragraph_blocks:
        if len(block) > size:
            # Flush current chunk first
            if current.strip():
                built_chunks.append(current.strip())
                current = ""

            built_chunks.extend(_split_large_unit(block, size, overlap))
            continue

        if not current:
            candidate = block
        else:
            candidate = f"{current}\n\n{block}"

        if len(candidate) <= size:
            current = candidate
        else:
            if current.strip():
                built_chunks.append(current.strip())

            if overlap > 0 and built_chunks:
                previous_tail = built_chunks[-1][-overlap:].strip()
                if previous_tail:
                    current = f"{previous_tail}\n\n{block}"
                else:
                    current = block
            else:
                current = block

    if current.strip():
        built_chunks.append(current.strip())

    chunks: list[TextChunk] = []
    search_start = 0

    for chunk_index, chunk_content in enumerate(built_chunks):
        # Best-effort char span mapping back into cleaned_text
        found_at = cleaned_text.find(chunk_content, search_start)
        if found_at == -1:
            found_at = cleaned_text.find(chunk_content)

        start_char = found_at if found_at >= 0 else search_start
        end_char = start_char + len(chunk_content)

        chunks.append(
            TextChunk(
                chunk_index=chunk_index,
                content=chunk_content,
                start_char=start_char,
                end_char=end_char,
            )
        )

        search_start = end_char

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