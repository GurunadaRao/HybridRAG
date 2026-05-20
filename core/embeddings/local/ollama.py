from __future__ import annotations

import json
from typing import List
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..base import EmbeddingAdapter


class OllamaEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter for a local Ollama instance."""

    def __init__(self, base_url: str, model: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return []

        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"failed to fetch local embeddings from Ollama: {exc}") from exc

        data = json.loads(raw)
        embedding = data.get("embedding")
        if not isinstance(embedding, list):
            raise ValueError("ollama embedding response did not include a vector")

        return [float(value) for value in embedding]
