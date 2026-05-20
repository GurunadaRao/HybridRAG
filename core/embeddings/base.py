from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class EmbeddingAdapter(ABC):
    """Common interface for all embedding backends."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError
