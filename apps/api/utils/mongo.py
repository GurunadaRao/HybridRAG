import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional


async def connect_mongo(app) -> None:
    """Create Mongo client and attach to app.state."""
    mongo_url = os.environ.get("MONGODB_URL")
    if not mongo_url:
        return

    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get("MONGODB_DATABASE", "hybrid_rag")
    documents_coll = os.environ.get("MONGODB_DOCUMENTS_COLLECTION", "documents")
    chunks_coll = os.environ.get("MONGODB_CHUNKS_COLLECTION", "chunks")

    app.state.mongodb_client = client
    app.state.mongodb_db = client[db_name]
    # store collection names for convenience
    app.state.mongodb_collections = {
        "documents": app.state.mongodb_db[documents_coll],
        "chunks": app.state.mongodb_db[chunks_coll],
    }

    # Ensure basic indexes for performance
    try:
        # documents: filename, created_at
        await app.state.mongodb_collections["documents"].create_index(
            [("filename", 1)], name="idx_documents_filename"
        )
        await app.state.mongodb_collections["documents"].create_index(
            [("created_at", -1)], name="idx_documents_created_at"
        )

        # chunks: document_id, chunk_index, created_at
        await app.state.mongodb_collections["chunks"].create_index(
            [("document_id", 1)], name="idx_chunks_document_id"
        )
        await app.state.mongodb_collections["chunks"].create_index(
            [("created_at", -1)], name="idx_chunks_created_at"
        )
    except Exception:
        # index creation failures shouldn't stop the app; log silently here
        pass


async def close_mongo(app) -> None:
    client: Optional[AsyncIOMotorClient] = getattr(app.state, "mongodb_client", None)
    if client:
        client.close()
        app.state.mongodb_client = None
        app.state.mongodb_db = None
        app.state.mongodb_collections = {}
