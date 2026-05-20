from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


_HEADING_RE = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class ChunkRecord:
    index: int
    text: str
    char_count: int
    word_count: int


def _normalize_text(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        cleaned_lines.append(line.rstrip())

    normalized = "\n".join(cleaned_lines).strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized


def _split_sections(text: str) -> list[str]:
    if not text:
        return []

    lines = text.splitlines()
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        if _HEADING_RE.match(line) and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current).strip())

    return [section for section in sections if section]


def _split_paragraphs(section: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", section) if paragraph.strip()]
    return paragraphs or [section.strip()]


def _split_sentences(paragraph: str) -> list[str]:
    sentences = [sentence.strip() for sentence in _SENTENCE_RE.split(paragraph) if sentence.strip()]
    return sentences or [paragraph.strip()]


def _split_words(text: str) -> list[str]:
    words = [word for word in _WHITESPACE_RE.split(text.strip()) if word]
    return words


def _pack_units(units: list[str], chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    current = ""

    for unit in units:
        candidate = unit if not current else f"{current}\n\n{unit}"

        if current and len(candidate) > chunk_size:
            chunks.append(current.strip())
            if overlap > 0:
                tail = current[-overlap:].strip()
                current = tail if tail else ""
                if current:
                    candidate = f"{current}\n\n{unit}"
                    if len(candidate) <= chunk_size:
                        current = candidate
                        continue
            current = unit
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    return [chunk for chunk in chunks if chunk]


def _split_long_unit(unit: str, chunk_size: int) -> list[str]:
    if len(unit) <= chunk_size:
        return [unit]

    sentences = _split_sentences(unit)
    if len(sentences) > 1:
        packed = _pack_units(sentences, chunk_size, 0)
        if all(len(chunk) <= chunk_size for chunk in packed):
            return packed

    words = _split_words(unit)
    if not words:
        return [unit[:chunk_size]]

    chunks: list[str] = []
    current_words: list[str] = []

    for word in words:
        candidate = " ".join(current_words + [word])
        if current_words and len(candidate) > chunk_size:
            chunks.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def _build_units(text: str) -> list[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return []

    units: list[str] = []
    for section in _split_sections(normalized):
        paragraphs = _split_paragraphs(section)
        for paragraph in paragraphs:
            if len(paragraph) <= 1:
                continue
            if len(paragraph) > 1000:
                units.extend(_split_long_unit(paragraph, 1000))
            else:
                units.append(paragraph)

    return units


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split structured text into coherent chunks.

    The splitter prefers heading and paragraph boundaries, then sentence boundaries,
    and finally word boundaries if a unit is still too large.
    """

    if not text:
        return []

    normalized = _normalize_text(text)
    if not normalized:
        return []

    chunks: list[str] = []
    for section in _split_sections(normalized):
        section_units: list[str] = []
        for paragraph in _split_paragraphs(section):
            if len(paragraph) <= chunk_size:
                section_units.append(paragraph)
            else:
                section_units.extend(_split_long_unit(paragraph, chunk_size))

        if not section_units:
            continue

        packed_chunks = _pack_units(section_units, chunk_size, overlap)
        chunks.extend(chunk.strip() for chunk in packed_chunks if chunk.strip())

    return [chunk for chunk in chunks if chunk]


def chunk_text_with_metadata(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[ChunkRecord]:
    """Split text and return chunk metadata for downstream storage or inspection."""

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    records: list[ChunkRecord] = []

    for index, chunk in enumerate(chunks):
        records.append(
            ChunkRecord(
                index=index,
                text=chunk,
                char_count=len(chunk),
                word_count=len(_split_words(chunk)),
            )
        )

    return records
