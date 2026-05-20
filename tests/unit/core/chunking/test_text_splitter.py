from __future__ import annotations

from core.chunking.text_splitter import chunk_text, chunk_text_with_metadata


def test_chunk_text_prefers_structured_boundaries():
    text = """## Intro
This is the first paragraph. It stays together.

## Details
This is a second paragraph with more content. It should remain coherent.
"""

    chunks = chunk_text(text, chunk_size=120, overlap=20)

    assert len(chunks) >= 2
    assert chunks[0].startswith("## Intro")
    assert "first paragraph" in chunks[0]
    assert any(chunk.startswith("## Details") for chunk in chunks)


def test_chunk_text_splits_oversized_paragraphs():
    text = " ".join([f"word{i}" for i in range(300)])

    chunks = chunk_text(text, chunk_size=80, overlap=10)

    assert len(chunks) > 1
    assert all(len(chunk) <= 80 for chunk in chunks)


def test_chunk_text_with_metadata_reports_counts():
    records = chunk_text_with_metadata("## Section\nSome short text here.", chunk_size=80)

    assert len(records) == 1
    assert records[0].index == 0
    assert records[0].char_count > 0
    assert records[0].word_count >= 4
