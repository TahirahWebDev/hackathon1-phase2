#!/usr/bin/env python3
"""
Validation script to test the RAG Chatbot Agent with real queries against existing vectors.
"""
import sys
import os
import logging
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.agent_service import AgentService
from backend.src.lib.config_loader import get_config


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


def validate_qdrant_connection():
    """Validate the connection to Qdrant."""
    logger = logging.getLogger(__name__)
    logger.info("Validating Qdrant connection...")
    
    try:
        config = get_config()
        
        qdrant_service = QdrantConnectionService()
        
        # Connect to Qdrant
        connected = qdrant_service.connect(
            url=config["QDRANT_URL"],
            api_key=config["QDRANT_API_KEY"],
            collection_name=config["QDRANT_COLLECTION_NAME"]
        )
        
        if connected:
            logger.info("✓ Qdrant connection successful")
            return True
        else:
            logger.error("✗ Qdrant connection failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Qdrant connection error: {str(e)}")
        return False


def validate_retrieval_service():
    """Validate the retrieval service with a test query."""
    logger = logging.getLogger(__name__)
    logger.info("Validating retrieval service...")
    
    try:
        config = get_config()
        
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        
        # Connect to Qdrant
        connected = qdrant_service.connect(
            url=config["QDRANT_URL"],
            api_key=config["QDRANT_API_KEY"],
            collection_name=config["QDRANT_COLLECTION_NAME"]
        )
        
        if not connected:
            logger.error("Cannot validate retrieval service - Qdrant connection failed")
            return False
        
        # Test retrieval with a simple query
        test_query = "What is artificial intelligence?"
        results = retrieval_service.retrieve_content(test_query, top_k=3)
        
        logger.info(f"Retrieved {len(results)} results for query: '{test_query}'")
        
        if len(results) > 0:
            logger.info("✓ Retrieval service validation successful")
            for i, result in enumerate(results[:2], 1):  # Show first 2 results
                content_preview = getattr(result, 'content', '')[:100] + "..."
                logger.info(f"  Result {i}: {content_preview}")
            return True
        else:
            logger.warning("⚠ Retrieval service returned no results")
            return False
            
    except Exception as e:
        logger.error(f"✗ Retrieval service validation error: {str(e)}")
        return False


def validate_agent_service():
    """Validate the agent service with a test query."""
    logger = logging.getLogger(__name__)
    logger.info("Validating agent service...")
    
    try:
        config = get_config()
        
        qdrant_service = QdrantConnectionService()
        retrieval_service = RetrievalService(qdrant_service)
        agent_service = AgentService(retrieval_service)
        
        # Connect to Qdrant
        connected = qdrant_service.connect(
            url=config["QDRANT_URL"],
            api_key=config["QDRANT_API_KEY"],
            collection_name=config["QDRANT_COLLECTION_NAME"]
        )
        
        if not connected:
            logger.error("Cannot validate agent service - Qdrant connection failed")
            return False
        
        # Initialize the agent
        agent_service.initialize_agent()
        
        # Test agent with a simple query
        test_query = "What is artificial intelligence?"
        result = agent_service.process_message(test_query, session_id="validation_test")
        
        logger.info(f"Agent response length: {len(result['response'])} characters")
        logger.info(f"Sources found: {len(result['sources'])}")
        
        if result['response'] and len(result['response']) > 10:  # Check for a meaningful response
            logger.info("✓ Agent service validation successful")
            logger.info(f"  Response preview: {result['response'][:100]}...")
            return True
        else:
            logger.warning("⚠ Agent service returned a short or empty response")
            return False
            
    except Exception as e:
        logger.error(f"✗ Agent service validation error: {str(e)}")
        return False


def main():
    """Main validation function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting RAG Chatbot Agent validation...")
    
    # Run all validations
    validations = [
        ("Qdrant Connection", validate_qdrant_connection),
        ("Retrieval Service", validate_retrieval_service),
        ("Agent Service", validate_agent_service)
    ]
    
    results = []
    for name, validation_func in validations:
        logger.info(f"Running {name} validation...")
        success = validation_func()
        results.append((name, success))
        logger.info(f"{name} validation: {'PASS' if success else 'FAIL'}")
        print()
    
    # Summary
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info(f"Validation Summary: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All validations passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())