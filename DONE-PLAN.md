# HybridRAG Done Plan

## Completed Work

- Split the environment files into clear local and cloud sections.
- Updated `.env.example` to mirror the local/cloud organization.
- Kept the existing server config keys working with the new env layout.
- Added cloud storage configuration placeholders for NoSQL/MongoDB.
- Exposed cloud storage settings in the server runtime config.
- Exposed cloud storage settings in the ingest config.
- Confirmed the server still has a working local-first ingestion and retrieval flow.
- Confirmed the query path uses LangGraph orchestration with intent routing, retrieval, grading, refinement, and fallback behavior.
- Confirmed the React UI is wired to send queries to the backend.

## Notes

- Cloud storage settings are now planned in config, but actual MongoDB persistence is not implemented yet.
- The cloud retrieval adapter still falls back to the local retrieval implementation.
- File-based storage remains the active ingestion/indexing mechanism for local mode.
