import logging

from fastapi import FastAPI
from src.routes.ingest import router as ingest_router
from src.routes.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple Agentic Healthcare RAG App",
    description="Learning project using FastAPI, Ollama, ChromaDB, RAG, and simple tools",
    version="1.0.0",
)

app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/health")
def health():
    logger.info("health endpoint called")

    return {
        "message": "Healthcare Agentic RAG API is running",
        "endpoints": {
            "ingest": "/ingest/file",
            "chat": "/chat/query",
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)