# core/embeddings

Embedding service adapters and utilities.

This package supports two runtime variants through a shared factory:

- Local: Ollama with `nomic-embed-text:latest`
- Cloud: Hugging Face inference API via a configurable adapter

The API layer keeps importing a single `text_to_embedding()` helper, so the ingestion path does not need to know which provider is active.
