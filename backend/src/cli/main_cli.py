"""
Command-line interface for individual component execution of the RAG Chatbot Agent.
This module provides CLI commands for running specific components of the system.
"""
import argparse
import sys
import logging
from typing import List, Optional

from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.agent_service import AgentService
from backend.src.lib.config_loader import get_config


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


def test_retrieval_component(urls: List[str], query: str, top_k: int = 5):
    """
    Test the retrieval component by ingesting URLs and then performing a search.

    Args:
        urls: List of URLs to ingest
        query: Query to test retrieval with
        top_k: Number of results to retrieve
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize services
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        
        print(f"Ingesting content from URLs: {urls}")
        # Ingest content from URLs
        retrieval_service.ingest_content(urls)
        
        print(f"Retrieving content for query: '{query}'")
        # Perform retrieval
        results = retrieval_service.retrieve_content(query, top_k=top_k)
        
        print(f"Retrieved {len(results)} results:")
        for i, result in enumerate(results, 1):
            content = getattr(result, 'content', '')[:200]  # Limit content display
            print(f"{i}. Content preview: {content}...")
            print(f"   Source: {getattr(result, 'source_url', 'Unknown')}")
            print(f"   Score: {getattr(result, 'score', 0.0)}")
            print()
        
    except Exception as e:
        logger.error(f"Error in retrieval component test: {str(e)}", exc_info=True)
        sys.exit(1)


def test_agent_component(query: str, session_id: Optional[str] = None):
    """
    Test the agent component by processing a query.

    Args:
        query: Query to process with the agent
        session_id: Session identifier for conversation context
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize services
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        agent_service = AgentService(retrieval_service)
        
        # Initialize the agent
        agent_service.initialize_agent()
        
        print(f"Processing query with agent: '{query}'")
        # Process the message
        result = agent_service.process_message(query, session_id=session_id)
        
        print(f"Agent response: {result['response']}")
        print(f"Session ID: {result['session_id']}")
        print(f"Sources: {len(result['sources'])} found")
        
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source['title']} - {source['url']} (confidence: {source['confidence']})")
        
    except Exception as e:
        logger.error(f"Error in agent component test: {str(e)}", exc_info=True)
        sys.exit(1)


def test_qdrant_connection():
    """
    Test the connection to Qdrant.
    """
    logger = logging.getLogger(__name__)
    
    try:
        print("Testing Qdrant connection...")
        
        # Load configuration
        config = get_config()
        
        # Initialize Qdrant service
        qdrant_service = QdrantConnectionService()
        
        # Test the connection
        is_connected = qdrant_service.test_connection()
        
        if is_connected:
            print("✓ Qdrant connection successful")
        else:
            print("✗ Qdrant connection failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error testing Qdrant connection: {str(e)}", exc_info=True)
        sys.exit(1)


def main():
    """Main CLI function to handle different commands."""
    parser = argparse.ArgumentParser(description="RAG Chatbot Agent CLI")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level (default: INFO)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subparser for testing Qdrant connection
    qdrant_parser = subparsers.add_parser("test-qdrant", help="Test Qdrant connection")
    
    # Subparser for testing retrieval component
    retrieval_parser = subparsers.add_parser("test-retrieval", help="Test retrieval component")
    retrieval_parser.add_argument("--urls", nargs="+", required=True, help="URLs to ingest and test")
    retrieval_parser.add_argument("--query", type=str, required=True, help="Query to test retrieval with")
    retrieval_parser.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve (default: 5)")
    
    # Subparser for testing agent component
    agent_parser = subparsers.add_parser("test-agent", help="Test agent component")
    agent_parser.add_argument("--query", type=str, required=True, help="Query to process with the agent")
    agent_parser.add_argument("--session-id", type=str, help="Session identifier for conversation context")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    if args.command == "test-qdrant":
        test_qdrant_connection()
    elif args.command == "test-retrieval":
        test_retrieval_component(args.urls, args.query, args.top_k)
    elif args.command == "test-agent":
        test_agent_component(args.query, args.session_id)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()