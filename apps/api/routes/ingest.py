from fastapi import APIRouter, UploadFile, File, Request
from datetime import datetime
from typing import List

from ..utils.chunker import chunk_text
from ..utils.embeddings import text_to_embedding
from core.contextualization.context_builder import contextualize_chunks_as_dicts
from core.ingestion.loaders import extract_text_from_upload
from core.ingestion.storage import clear_local_ingestion_state, save_json_record, save_raw_upload

router = APIRouter()


@router.post("/")
async def ingest(request: Request, files: List[UploadFile] | None = File(default=None)):
    """Ingest uploaded files and persist documents + chunks to MongoDB when configured.

    If MongoDB is not configured (no MONGODB_URL), this returns a scaffold response.
    """
    collections = getattr(request.app.state, "mongodb_collections", None)
    filenames = [f.filename for f in (files or [])]

    if not collections:
        # clear_local_ingestion_state()  # disabled: avoid removing existing local artifacts
        saved_documents = []
        local_records = []
        total_chunks = 0

        for f in (files or []):
            try:
                raw = await f.read()
                text, loader_name = extract_text_from_upload(f.filename, raw, f.content_type)
                raw_path = save_raw_upload(f.filename, raw)

                document_record = {
                    "filename": f.filename,
                    "content_length": len(raw),
                    "created_at": datetime.utcnow(),
                    "source": "upload",
                    "loader": loader_name,
                    "storage": "local",
                    "raw_path": str(raw_path),
                    "structured_text": text,
                }
                if text is not None:
                    document_record["text"] = text

                document_path = save_json_record("documents", f.filename, document_record)
                saved_documents.append(str(document_path))

                if text:
                    chunks = chunk_text(text)
                    contextual_chunks = contextualize_chunks_as_dicts(chunks, window=1)
                    chunk_records = []
                    embedding_records = []
                    for idx, contextual in enumerate(contextual_chunks):
                        contextual_text = contextual.get("contextual_text") or contextual.get("text", "")
                        embedding = text_to_embedding(contextual_text)
                        chunk_records.append(
                            {
                                "chunk_index": idx,
                                "text": contextual.get("text", ""),
                                "contextual_text": contextual_text,
                                "prev_text": contextual.get("prev_text"),
                                "next_text": contextual.get("next_text"),
                                "created_at": datetime.utcnow(),
                                "embedding": embedding,
                            }
                        )
                        embedding_records.append(
                            {
                                "chunk_index": idx,
                                "embedding": embedding,
                            }
                        )

                    if chunk_records:
                        total_chunks += len(chunk_records)
                        chunk_path = save_json_record("chunks", f.filename, chunk_records)
                        contextual_path = save_json_record("contextual_chunks", f.filename, contextual_chunks)
                        embedding_path = save_json_record("embeddings", f.filename, embedding_records)
                        local_records.append(
                            {
                                "chunks": str(chunk_path),
                                "contextual_chunks": str(contextual_path),
                                "embeddings": str(embedding_path),
                            }
                        )

            except Exception as e:
                return {"error": "failed to ingest file", "file": f.filename, "detail": str(e)}

        return {
            "message": "ingest completed locally",
            "storage_mode": "local_filesystem",
            "received": filenames,
            "documents_saved": len(saved_documents),
            "document_ids": saved_documents,
            "chunks_saved": total_chunks,
            "local_artifacts": local_records,
        }

    saved_documents = []
    total_chunks = 0

    # NOTE: disabling automatic deletion of existing Mongo documents
    # for collection_name in ("documents", "chunks"):
    #     try:
    #         await collections[collection_name].delete_many({})
    #     except Exception:
    #         return {"error": "failed to clear existing documents", "collection": collection_name}

    for f in (files or []):
        try:
            raw = await f.read()
            text, loader_name = extract_text_from_upload(f.filename, raw, f.content_type)

            doc = {
                "filename": f.filename,
                "content_length": len(raw),
                "created_at": datetime.utcnow(),
                "source": "upload",
                "loader": loader_name,
                "structured_text": text,
            }
            if text is not None:
                doc["text"] = text

            res = await collections["documents"].insert_one(doc)
            doc_id = res.inserted_id
            saved_documents.append(str(doc_id))

            # create chunks if we have text
            if text:
                chunks = chunk_text(text)
                contextual_chunks = contextualize_chunks_as_dicts(chunks, window=1)
                chunk_docs = []
                for idx, contextual in enumerate(contextual_chunks):
                    contextual_text = contextual.get("contextual_text") or contextual.get("text", "")
                    chunk_docs.append(
                        {
                            "document_id": doc_id,
                            "chunk_index": idx,
                            "text": contextual.get("text", ""),
                            "contextual_text": contextual_text,
                            "prev_text": contextual.get("prev_text"),
                            "next_text": contextual.get("next_text"),
                            "created_at": datetime.utcnow(),
                            "embedding": None,
                        }
                    )

                if chunk_docs:
                    # insert chunks and then compute embeddings for each inserted chunk
                    result = await collections["chunks"].insert_many(chunk_docs)
                    inserted_ids = getattr(result, "inserted_ids", [])
                    total_chunks += len(inserted_ids)

                    # generate embeddings from contextualized chunk text
                    for cid, chunk_doc in zip(inserted_ids, chunk_docs):
                        emb = text_to_embedding(chunk_doc.get("contextual_text", ""))
                        try:
                            await collections["chunks"].update_one(
                                {"_id": cid}, {"$set": {"embedding": emb}}
                            )
                        except Exception:
                            # ignore embedding update failures but continue
                            pass

        except Exception as e:
            # continue on error per-file but record the issue
            return {"error": "failed to ingest file", "file": f.filename, "detail": str(e)}

    return {
        "message": "ingest completed",
        "received": filenames,
        "documents_saved": len(saved_documents),
        "document_ids": saved_documents,
        "chunks_saved": total_chunks,
    }
