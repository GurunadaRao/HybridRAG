from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from .base import EmbeddingAdapter
from .cloud.huggingface import HuggingFaceEmbeddingAdapter
from .local.ollama import OllamaEmbeddingAdapter


def _trimmed_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if isinstance(value, str):
        value = value.strip()
    return value or None


@lru_cache(maxsize=1)
def get_embedding_adapter() -> EmbeddingAdapter:
    provider = (_trimmed_env("EMBEDDING_PROVIDER", "local") or "local").lower()

    if provider in {"cloud", "huggingface", "hf"}:
        token = _trimmed_env("HUGGINGFACE_API_TOKEN") or _trimmed_env("HF_TOKEN")
        if not token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN (or HF_TOKEN) is required for cloud embeddings")

        model = _trimmed_env("HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        endpoint = _trimmed_env("HUGGINGFACE_EMBEDDING_URL")
        return HuggingFaceEmbeddingAdapter(model=model, token=token, endpoint=endpoint)

    base_url = _trimmed_env("OLLAMA_BASE_URL", "http://localhost:11434")
    model = _trimmed_env("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")
    return OllamaEmbeddingAdapter(base_url=base_url or "http://localhost:11434", model=model or "nomic-embed-text:latest")


def text_to_embedding(text: str) -> List[float]:
    return get_embedding_adapter().embed_text(text)
