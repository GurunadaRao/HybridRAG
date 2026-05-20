from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterable


def get_data_root() -> Path:
    return Path(os.environ.get("DATA_DIR", "data")).resolve()


def _safe_name(filename: str | None) -> str:
    name = Path(filename or "upload").name
    return name or "upload"


def save_raw_upload(filename: str | None, raw: bytes) -> Path:
    target = get_data_root() / "raw" / "uploads" / _safe_name(filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return target


def save_json_record(subdirectory: str, filename: str | None, payload: Any) -> Path:
    target = get_data_root() / "processed" / subdirectory / f"{Path(_safe_name(filename)).stem}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return target


def clear_local_ingestion_state() -> None:
    root = get_data_root()
    targets = [
        root / "raw" / "uploads",
        root / "processed" / "documents",
        root / "processed" / "chunks",
        root / "processed" / "contextual_chunks",
        root / "processed" / "embeddings",
    ]

    for target in targets:
        if target.exists():
            shutil.rmtree(target)

