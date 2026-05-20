from __future__ import annotations

from io import BytesIO

from pypdf import PdfWriter

from core.ingestion.loaders import extract_text_from_upload


def test_extract_text_from_json_upload():
    text, loader = extract_text_from_upload(
        "sample.json",
        b'{"title": "HybridRAG", "items": [1, 2, 3]}',
    )

    assert loader == "json"
    assert "## JSON Document" in text
    assert "title: \"HybridRAG\"" in text
    assert "items[1]: 1" in text


def test_extract_text_from_csv_upload():
    text, loader = extract_text_from_upload(
        "sample.csv",
        b"name,score\nalpha,10\nbeta,20\n",
    )

    assert loader == "csv"
    assert "## CSV Table" in text
    assert "Row 1" in text
    assert "- name: alpha" in text
    assert "- score: 20" in text


def test_extract_text_from_pdf_upload():
    pdf_buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    text, loader = extract_text_from_upload("sample.pdf", pdf_buffer.getvalue())

    assert loader == "pdf"
    assert text is None or isinstance(text, str)
