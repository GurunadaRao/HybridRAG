from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace

from starlette.datastructures import UploadFile

from apps.api.routes.ingest import ingest


class FakeResult:
    def __init__(self, inserted_id=None, inserted_ids=None):
        self.inserted_id = inserted_id
        self.inserted_ids = inserted_ids or []


class FakeCollection:
    def __init__(self):
        self.items = []
        self.deleted = False
        self._counter = 0

    async def delete_many(self, filter_document):
        self.items.clear()
        self.deleted = True
        return FakeResult()

    async def insert_one(self, document):
        self._counter += 1
        stored = dict(document)
        stored["_id"] = f"doc-{self._counter}"
        self.items.append(stored)
        return FakeResult(inserted_id=stored["_id"])

    async def insert_many(self, documents):
        inserted_ids = []
        for document in documents:
            self._counter += 1
            stored = dict(document)
            stored["_id"] = f"chunk-{self._counter}"
            self.items.append(stored)
            inserted_ids.append(stored["_id"])
        return FakeResult(inserted_ids=inserted_ids)

    async def update_one(self, filter_document, update_document):
        target_id = filter_document.get("_id")
        for item in self.items:
            if item.get("_id") == target_id:
                item.update(update_document.get("$set", {}))
                return None
        raise AssertionError(f"missing row for {target_id}")


def test_mongo_ingestion_keeps_previous_state(monkeypatch):
    async def run_test():
        documents = FakeCollection()
        chunks = FakeCollection()
        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace(mongodb_collections={"documents": documents, "chunks": chunks}))
        )

        monkeypatch.setattr("apps.api.routes.ingest.text_to_embedding", lambda text: [0.1, 0.2])

        first_upload = UploadFile(file=BytesIO(b"hello world"), filename="first.txt")
        first_response = await ingest(request, [first_upload])
        assert first_response["documents_saved"] == 1

        documents.items.append({"_id": "stale-doc"})
        chunks.items.append({"_id": "stale-chunk"})

        second_upload = UploadFile(file=BytesIO(b"fresh content"), filename="second.txt")
        second_response = await ingest(request, [second_upload])

        assert first_response["documents_saved"] == 1
        assert second_response["documents_saved"] == 1
        assert documents.deleted is False
        assert chunks.deleted is False
        assert any(item.get("_id") == "stale-doc" for item in documents.items)
        assert any(item.get("_id") == "stale-chunk" for item in chunks.items)

    import asyncio

    asyncio.run(run_test())