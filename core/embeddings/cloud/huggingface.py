from __future__ import annotations

import json
from typing import List
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..base import EmbeddingAdapter


def _pool_embedding(response_value: object) -> List[float]:
    if isinstance(response_value, list) and response_value and isinstance(response_value[0], (int, float)):
        return [float(value) for value in response_value]

    if isinstance(response_value, list) and response_value and isinstance(response_value[0], list):
        if response_value[0] and isinstance(response_value[0][0], list):
            response_value = response_value[0]
        
        width = len(response_value[0])
        totals = [0.0] * width
        valid_rows = 0

        for row in response_value:
            if not isinstance(row, list) or len(row) != width:
                continue

            for index, value in enumerate(row):
                totals[index] += float(value)
            valid_rows += 1

        if valid_rows:
            return [value / valid_rows for value in totals]

    raise ValueError("hugging face embedding response could not be converted to a vector")


class HuggingFaceEmbeddingAdapter(EmbeddingAdapter):
    """Embedding adapter for the Hugging Face inference API."""

    def __init__(self, model: str, token: str, endpoint: str | None = None, timeout: int = 60) -> None:
        self.model = model
        self.token = token
        self.endpoint = endpoint or f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        self.timeout = timeout

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return []

        payload = json.dumps({"inputs": text, "options": {"wait_for_model": True}}).encode("utf-8")
        request = Request(
            self.endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"failed to fetch cloud embeddings from Hugging Face: {exc}") from exc

        data = json.loads(raw)
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(f"hugging face embedding error: {data['error']}")

        return _pool_embedding(data)
