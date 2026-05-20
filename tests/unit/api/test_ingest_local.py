from __future__ import annotations

import asyncio
from io import BytesIO
from types import SimpleNamespace

from starlette.datastructures import UploadFile

from apps.api.routes.ingest import ingest


class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class InsertManyResult:
    def __init__(self, inserted_ids):
        self.inserted_ids = inserted_ids


class FakeCollection:
    def __init__(self):
        self.rows = []
        self._counter = 0
        self.deleted = False

    async def delete_many(self, filter_document):
        self.rows.clear()
        self.deleted = True
        return None

    async def insert_one(self, document):
        self._counter += 1
        stored = dict(document)
        stored["_id"] = f"doc-{self._counter}"
        self.rows.append(stored)
        return InsertOneResult(stored["_id"])

    async def insert_many(self, documents):
        inserted_ids = []
        for document in documents:
            self._counter += 1
            stored = dict(document)
            stored["_id"] = f"chunk-{self._counter}"
            self.rows.append(stored)
            inserted_ids.append(stored["_id"])
        return InsertManyResult(inserted_ids)

    async def update_one(self, filter_document, update_document):
        target_id = filter_document.get("_id")
        updated_fields = update_document.get("$set", {})
        for row in self.rows:
            if row.get("_id") == target_id:
                row.update(updated_fields)
                return None
        raise AssertionError(f"missing row for {target_id}")


def test_local_ingestion_pipeline_completes(monkeypatch):
    async def run_test():
        documents = FakeCollection()
        chunks = FakeCollection()
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(
                    mongodb_collections={"documents": documents, "chunks": chunks}
                )
            )
        )

        monkeypatch.setattr(
            "apps.api.routes.ingest.text_to_embedding",
            lambda text: [0.11, 0.22, 0.33],
        )

        upload = UploadFile(
            file=BytesIO(
                b"HybridRAG local ingestion pipeline test input. "
                b"This should be chunked, embedded, and stored successfully."
            ),
            filename="local-ingest.txt",
        )

        response = await ingest(request, [upload])

        assert response["message"] == "ingest completed"
        assert response["documents_saved"] == 1
        assert response["chunks_saved"] >= 1
        assert response["received"] == ["local-ingest.txt"]
        assert len(response["document_ids"]) == 1
        assert all(row.get("embedding") == [0.11, 0.22, 0.33] for row in chunks.rows)

    asyncio.run(run_test())
