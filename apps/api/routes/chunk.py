from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
import json

from core.chunking.text_splitter import chunk_text
from core.ingestion.storage import get_data_root

router = APIRouter()


class ChunkRequest(BaseModel):
    text: Optional[str] = None
    filename: Optional[str] = None
    document_id: Optional[str] = None


@router.post("/")
async def chunk_endpoint(request: Request, body: ChunkRequest):
    """Return chunks for provided text, a local filename, or a Mongo document id.

    This endpoint does not persist chunks; it only runs the chunker and returns results.
    """
    # 1) If raw text provided, chunk it directly
    if body.text:
        chunks = chunk_text(body.text)
        return {"source": "text", "chunks": chunks, "count": len(chunks)}

    # 2) If filename provided, attempt to read the processed document JSON
    if body.filename:
        try:
            root = get_data_root()
            fname = body.filename
            # use same stem naming as save_json_record
            path = root / "processed" / "documents" / f"{fname.rsplit('.',1)[0]}.json"
            if not path.exists():
                return {"error": "file_not_found", "path": str(path)}
            doc = json.loads(path.read_text(encoding="utf-8"))
            text = doc.get("text") or doc.get("structured_text")
            if not text:
                return {"error": "no_text_in_document", "path": str(path)}
            chunks = chunk_text(text)
            return {"source": "local_document", "chunks": chunks, "count": len(chunks), "path": str(path)}
        except Exception as e:
            return {"error": "failed_to_chunk_local", "detail": str(e)}

    # 3) If document_id provided and Mongo is configured, fetch the document and chunk
    if body.document_id:
        collections = getattr(request.app.state, "mongodb_collections", None)
        if not collections:
            return {"error": "no_mongo", "message": "MongoDB not configured on server"}
        try:
            # assume document_id is a string representation; let driver handle conversion
            doc = await collections["documents"].find_one({"_id": body.document_id})
            if not doc:
                return {"error": "not_found", "document_id": body.document_id}
            text = doc.get("text") or doc.get("structured_text")
            if not text:
                return {"error": "no_text_in_document", "document_id": body.document_id}
            chunks = chunk_text(text)
            return {"source": "mongo_document", "chunks": chunks, "count": len(chunks), "document_id": body.document_id}
        except Exception as e:
            return {"error": "failed_to_chunk_mongo", "detail": str(e)}

    return {"error": "no_input", "message": "Provide text, filename, or document_id"}
