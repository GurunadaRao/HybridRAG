from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class ContextualChunk:
    chunk_index: int
    text: str
    contextual_text: str
    prev_text: str | None = None
    next_text: str | None = None


def contextualize_chunks(chunks: List[str], window: int = 1) -> List[ContextualChunk]:
    """Build contextualized chunk records from plain chunks.

    Each chunk is enriched with adjacent chunk text (previous/next by default)
    so downstream embedding and retrieval can use better local context.
    """

    if not chunks:
        return []

    records: List[ContextualChunk] = []
    total = len(chunks)

    for idx, chunk in enumerate(chunks):
        start = max(0, idx - window)
        end = min(total, idx + window + 1)

        context_lines: list[str] = [f"[Chunk {idx}]", chunk]

        if idx > 0:
            prev_text = chunks[idx - 1]
        else:
            prev_text = None

        if idx < total - 1:
            next_text = chunks[idx + 1]
        else:
            next_text = None

        for n in range(start, end):
            if n == idx:
                continue
            label = "Prev" if n < idx else "Next"
            context_lines.append(f"[{label} Chunk {n}]")
            context_lines.append(chunks[n])

        contextual_text = "\n\n".join(line for line in context_lines if line)

        records.append(
            ContextualChunk(
                chunk_index=idx,
                text=chunk,
                contextual_text=contextual_text,
                prev_text=prev_text,
                next_text=next_text,
            )
        )

    return records


def contextualize_chunks_as_dicts(chunks: List[str], window: int = 1) -> list[dict]:
    """Convenience wrapper used by API/storage layers."""

    return [asdict(item) for item in contextualize_chunks(chunks, window=window)]
