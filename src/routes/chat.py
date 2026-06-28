import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.agent import healthcare_agent

router = APIRouter()

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    user_id: str
    query: str


@router.post("/ask")
def chat_query(request: ChatRequest):
    """
    Ask a query.

    Example queries:
    - Give me the reports for current user
    - What is the medication for diabetes?
    - Schedule an appointment for me on 2026-07-01
    """

    logger.info("Received chat query request")
    logger.info("User ID: %s", request.user_id)
    logger.info("User query: %s", request.query)

    try:
        logger.info("Sending query to healthcare agent")

        result = healthcare_agent.run(
            query=request.query,
            user_id=request.user_id,
        )

        logger.info("Healthcare agent processed query successfully")
        logger.info("Selected tool: %s", result.get("selected_tool"))

        return result

    except Exception as e:
        logger.exception("Error occurred while processing chat query")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )