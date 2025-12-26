"""
API endpoint for the chat functionality of the RAG Content Ingestion Pipeline.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

from backend.src.models.chat_message import ChatMessage
from backend.src.services.agent_service import AgentService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.lib.config_loader import get_config


router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    top_k: int = 5


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat endpoint that accepts user messages and returns agent responses.

    Args:
        request: ChatRequest object containing message, session_id, and top_k

    Returns:
        Dictionary containing the agent's response and metadata
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if request.top_k <= 0 or request.top_k > 100:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 100")

    try:
        # Load configuration
        config = get_config()

        # Initialize services
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        agent_service = AgentService(retrieval_service)

        # Initialize the agent with API key
        agent_service.initialize_agent(api_key=config.get("GEMINI_API_KEY"))

        # Process the message
        options = {"top_k": request.top_k}
        result = agent_service.process_message(
            message=request.message,
            session_id=request.session_id,
            options=options
        )

        return result

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")