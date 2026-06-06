# 🛠️ API Reference

The HybridRAG API is built with FastAPI and follows RESTful principles.

## 🏥 Health
### `GET /api/health`
Checks system health and database connectivity.
- **Response**: `{"status": "ok", "mongodb": true}`

---

## 📥 Ingestion
### `POST /api/ingest/upload`
Upload a document (PDF/CSV/TXT) to be processed and indexed.
- **Form Data**: `file: File`
- **Response**: `{"document_id": "...", "chunks": 42}`

---

## 🧠 Query & Reasoning
### `POST /api/query/ask`
Execute an agentic query over the knowledge base.
- **Body**:
  ```json
  {
    "query": "How does contextual chunking work?",
    "stream": false
  }
  ```
- **Response**:
  ```json
  {
    "answer": "...",
    "sources": [
      {"id": "...", "content": "...", "score": 0.95}
    ],
    "steps": ["retrieve", "grade", "generate"]
  }
  ```

---

## 🧩 Chunk Management
### `GET /api/chunk/{doc_id}`
Retrieve all chunks for a specific document.
- **Response**: `[{"index": 0, "text": "...", "metadata": {}}]`
