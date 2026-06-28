import os
import shutil
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from src.utils.doc_loader import load_document
from src.rag.rag import rag

router = APIRouter()

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/ingest")
async def ingest_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a single PDF, DOCX, or TXT file and ingest it into ChromaDB.
    """

    logger.info("Received file ingestion request")
    logger.info("User ID: %s", user_id)
    logger.info("Uploaded filename: %s", file.filename)
    logger.info("Uploaded content type: %s", file.content_type)

    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        logger.info("Saving uploaded file to path: %s", file_path)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("File saved successfully: %s", file_path)

        logger.info("Loading document content from file: %s", file_path)
        documents = load_document(file_path)

        logger.info("Document loaded successfully")
        logger.info("Total document sections/pages loaded: %s", len(documents))

        for doc in documents:
            doc["metadata"]["uploaded_filename"] = file.filename

        logger.info("Starting document ingestion into ChromaDB")
        result = rag.ingest_documents(
            documents=documents,
            user_id=user_id,
        )

        logger.info("File ingestion completed successfully")
        logger.info("Ingestion result: %s", result)

        return {
            "message": "File ingested successfully",
            "filename": file.filename,
            "user_id": user_id,
            "result": result,
        }

    except Exception as e:
        logger.exception("Error occurred while ingesting file")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )