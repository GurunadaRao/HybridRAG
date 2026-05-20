from typing import List

from core.embeddings.factory import get_embedding_adapter, text_to_embedding as _text_to_embedding


def text_to_embedding(text: str) -> List[float]:
    """Return an embedding vector from the configured adapter."""

    return _text_to_embedding(text)


def get_embedding_service():
    """Expose the configured adapter for callers that need provider details."""

    return get_embedding_adapter()
