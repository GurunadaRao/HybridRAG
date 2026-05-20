from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import os
from dotenv import load_dotenv
from pathlib import Path

from .routes import health, ingest, chunk

from .utils.mongo import connect_mongo, close_mongo


# Load environment variables from the app directory .env (if present) so local credentials work
here = Path(__file__).parent
dot_env = here / ".env"
load_dotenv(dotenv_path=str(dot_env))


app = FastAPI(title="HybridRAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health")
app.include_router(ingest.router, prefix="/api/ingest")
app.include_router(chunk.router, prefix="/api/chunk")


@app.on_event("startup")
async def on_startup():
    """Connect to MongoDB if configured."""
    # Use environment variables if present; defaults keep local behavior.
    mongo_url = os.environ.get("MONGODB_URL")
    if mongo_url:
        await connect_mongo(app)


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo(app)


@app.get("/")
async def root(request: Request):
    info = {"service": "HybridRAG API", "status": "ok"}
    # indicate whether Mongo is connected
    info["mongodb"] = bool(getattr(request.app.state, "mongodb_client", None))
    return info
