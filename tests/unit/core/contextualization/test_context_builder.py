from __future__ import annotations

from core.contextualization.context_builder import contextualize_chunks


def test_contextualize_chunks_adds_neighbor_context():
    chunks = ["alpha", "beta", "gamma"]

    records = contextualize_chunks(chunks, window=1)

    assert len(records) == 3
    assert records[1].prev_text == "alpha"
    assert records[1].next_text == "gamma"
    assert "[Chunk 1]" in records[1].contextual_text
    assert "[Prev Chunk 0]" in records[1].contextual_text
    assert "[Next Chunk 2]" in records[1].contextual_text


def test_contextualize_chunks_handles_empty_input():
    assert contextualize_chunks([]) == []
