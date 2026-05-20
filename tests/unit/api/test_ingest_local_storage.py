from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from starlette.datastructures import UploadFile

from apps.api.routes.ingest import ingest


def test_local_file_backed_ingestion_completes(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("apps.api.routes.ingest.text_to_embedding", lambda text: [0.5, 0.25])

    async def run_test():
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(mongodb_collections=None)))
        upload = UploadFile(
            file=BytesIO(b'{"title": "HybridRAG", "body": "local file-backed ingestion"}'),
            filename="local.json",
        )

        response = await ingest(request, [upload])

        assert response["message"] == "ingest completed locally"
        assert response["storage_mode"] == "local_filesystem"
        assert response["documents_saved"] == 1
        assert response["chunks_saved"] >= 1
        assert len(response["local_artifacts"]) == 1

        raw_path = tmp_path / "raw" / "uploads" / "local.json"
        document_path = tmp_path / "processed" / "documents" / "local.json"
        chunk_path = tmp_path / "processed" / "chunks" / "local.json"
        contextual_chunk_path = tmp_path / "processed" / "contextual_chunks" / "local.json"
        embedding_path = tmp_path / "processed" / "embeddings" / "local.json"

        assert raw_path.exists()
        assert document_path.exists()
        assert chunk_path.exists()
        assert contextual_chunk_path.exists()
        assert embedding_path.exists()

        stored_document = document_path.read_text(encoding="utf-8")
        assert "## JSON Document" in stored_document
        assert 'title: \\\"HybridRAG\\\"' in stored_document
        assert 'body: \\\"local file-backed ingestion\\\"' in stored_document

    import asyncio

    asyncio.run(run_test())


def test_local_file_backed_ingestion_keeps_previous_state(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("apps.api.routes.ingest.text_to_embedding", lambda text: [0.5, 0.25])

    async def run_test():
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(mongodb_collections=None)))

        first_upload = UploadFile(file=BytesIO(b'{"title": "first", "body": "old"}'), filename="first.json")
        first_response = await ingest(request, [first_upload])
        assert first_response["documents_saved"] == 1

        stale_document = tmp_path / "processed" / "documents" / "first.json"
        assert stale_document.exists()

        second_upload = UploadFile(file=BytesIO(b'{"title": "second", "body": "new"}'), filename="second.json")
        second_response = await ingest(request, [second_upload])

        assert second_response["documents_saved"] == 1
        assert stale_document.exists()
        assert (tmp_path / "processed" / "documents" / "second.json").exists()

    import asyncio

    asyncio.run(run_test())
