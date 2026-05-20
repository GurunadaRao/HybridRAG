from __future__ import annotations

import json

from core.embeddings.factory import get_embedding_adapter
from core.embeddings.factory import text_to_embedding


def test_cloud_embedding_adapter(monkeypatch):
    class FakeResponse:
        def __init__(self, payload: str):
            self._payload = payload

        def read(self):
            return self._payload.encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout=0):
        return FakeResponse(json.dumps([[[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]]]))

    monkeypatch.setenv("EMBEDDING_PROVIDER", "cloud")
    monkeypatch.setenv("HUGGINGFACE_API_TOKEN", "fake-token")
    monkeypatch.setenv("HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    monkeypatch.setattr("core.embeddings.cloud.huggingface.urlopen", fake_urlopen)
    get_embedding_adapter.cache_clear()

    vector = text_to_embedding("cloud path")

    assert vector == [0.2, 0.2, 0.2]
