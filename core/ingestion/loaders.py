from __future__ import annotations

import csv
import json
from io import BytesIO, StringIO
from pathlib import Path

from pypdf import PdfReader


def _decode_text(raw: bytes) -> str | None:
    try:
        return raw.decode("utf-8")
    except Exception:
        return None


def _flatten_json(value: object, prefix: str = "") -> list[str]:
    lines: list[str] = []

    if isinstance(value, dict):
        for key in sorted(value.keys()):
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(_flatten_json(value[key], child_prefix))
        return lines

    if isinstance(value, list):
        if not value:
            lines.append(f"{prefix}: []")
            return lines

        for index, item in enumerate(value, start=1):
            child_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            lines.extend(_flatten_json(item, child_prefix))
        return lines

    rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else str(value)
    lines.append(f"{prefix}: {rendered}" if prefix else rendered)
    return lines


def _format_section(title: str, body: str) -> str:
    cleaned_body = body.strip()
    if not cleaned_body:
        return ""

    return f"## {title}\n{cleaned_body}"


def _load_plain_text(raw: bytes) -> str | None:
    decoded = _decode_text(raw)
    if decoded is None:
        return None

    cleaned = "\n".join(line.rstrip() for line in decoded.splitlines()).strip()
    return cleaned or None


def _load_json_text(raw: bytes) -> str | None:
    decoded = _decode_text(raw)
    if decoded is None:
        return None

    parsed = json.loads(decoded)
    flattened = _flatten_json(parsed)
    structured_body = "\n".join(flattened).strip()
    if not structured_body:
        return None

    return "\n\n".join([_format_section("JSON Document", structured_body), ""]).strip()


def _load_csv_text(raw: bytes) -> str | None:
    decoded = _decode_text(raw)
    if decoded is None:
        return None

    rows = list(csv.DictReader(StringIO(decoded)))
    if not rows:
        return None

    sections = ["## CSV Table"]
    headers = list(rows[0].keys())
    sections.append("Headers: " + ", ".join(headers))
    for index, row in enumerate(rows, start=1):
        sections.append(f"Row {index}")
        for header in headers:
            sections.append(f"- {header}: {row.get(header, '')}")

    return "\n".join(sections).strip()


def _load_pdf_text(raw: bytes) -> str | None:
    reader = PdfReader(BytesIO(raw))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        extracted = (page.extract_text() or "").strip()
        if extracted:
            cleaned_lines = [line.rstrip() for line in extracted.splitlines() if line.strip()]
            pages.append(f"## Page {index}\n" + "\n".join(cleaned_lines))

    if not pages:
        return None

    return "\n\n".join(pages).strip()


def extract_text_from_upload(filename: str | None, raw: bytes, content_type: str | None = None) -> tuple[str | None, str]:
    """Extract and normalize text from common upload formats.

    Returns the structured text and a loader label describing the format path.
    """

    suffix = Path(filename or "").suffix.lower()
    normalized_content_type = (content_type or "").lower()

    if suffix == ".pdf" or "pdf" in normalized_content_type:
        return _load_pdf_text(raw), "pdf"
    if suffix == ".json" or "json" in normalized_content_type:
        return _load_json_text(raw), "json"
    if suffix == ".csv" or "csv" in normalized_content_type:
        return _load_csv_text(raw), "csv"

    return _load_plain_text(raw), "text"
