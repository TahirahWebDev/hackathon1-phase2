#!/usr/bin/env python3
"""
Main entry point for the RAG Content Ingestion Pipeline.
This script runs the full ingestion pipeline end-to-end.
"""
import argparse
import sys
import logging
from typing import List

from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.agent_service import AgentService
from backend.src.api.chat_endpoint import router
from backend.src.lib.config_loader import get_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Create FastAPI app at module level for Vercel compatibility
app = FastAPI(title="RAG Content Ingestion Pipeline API",
              description="API for ingesting and retrieving documentation content using RAG",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router
app.include_router(router, prefix="/api/v1", tags=["chat"])


def setup_logging(level: str = "INFO"):
    """
    Set up logging configuration.

    Args:
        level: Logging level as a string (default: "INFO")
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


def main():
    """Main function to run the complete ingestion pipeline."""
    parser = argparse.ArgumentParser(description="RAG Content Ingestion Pipeline")
    parser.add_argument("--urls", nargs="+", required=True, help="URLs to crawl and ingest")
    parser.add_argument("--chunk-size", type=int, default=512, help="Size of text chunks (default: 512)")
    parser.add_argument("--overlap", type=int, default=20, help="Overlap between chunks (default: 20)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level (default: INFO)")

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = get_config()

        # Initialize services
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        agent_service = AgentService(retrieval_service)

        # Initialize the agent
        agent_service.initialize_agent(api_key=config.get("GEMINI_API_KEY"))

        logger.info(f"Starting server on {args.host}:{args.port}")
        logger.info(f"Logging level: {args.log_level}")

        # Run the server
        uvicorn.run(app, host=args.host, port=args.port)

        return 0

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error during pipeline execution: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())