# core/chunking

Chunking strategies and splitters.

The current implementation is structure-aware:

- preserves heading and paragraph boundaries when possible
- falls back to sentence and word splitting for long sections
- supports chunk metadata for downstream inspection
