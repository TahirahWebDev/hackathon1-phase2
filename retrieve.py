#!/usr/bin/env python3
"""
RAG Retrieval Validation Script

This script connects to Qdrant vector database, performs similarity search
with user queries, and validates the retrieved results.
"""
import argparse
import sys
from typing import List, Dict, Any
from backend.src.lib.config_loader import get_config
from backend.src.lib.logging_config import setup_logging, get_logger
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.validation_service import ValidationService


def main():
    """Main function to run the RAG retrieval validation."""
    parser = argparse.ArgumentParser(description="RAG Retrieval Validation")
    parser.add_argument("--query", type=str, required=True, help="Query text for retrieval validation")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top results to retrieve (default: 5)")
    parser.add_argument("--collection", type=str, help="Qdrant collection name (optional, defaults to environment)")
    parser.add_argument("--expected-sources", nargs="*", help="Expected source URLs for validation (optional)")

    args = parser.parse_args()

    # Set up logging
    config = get_config()
    log_level = config.get('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    logger = get_logger(__name__)

    logger.info(f"Starting RAG retrieval validation for query: '{args.query}'")
    logger.info(f"Top-K: {args.top_k}")

    try:
        # Load configuration
        config = get_config()

        # Get collection name from args or config
        collection_name = args.collection or config.get('QDRANT_COLLECTION_NAME', 'documents')

        # Connect to Qdrant
        logger.info("Attempting to connect to Qdrant...")
        connection_service = QdrantConnectionService()
        connection_result = connection_service.connect(
            url=config['QDRANT_URL'],
            api_key=config['QDRANT_API_KEY'],
            collection_name=collection_name
        )

        if connection_result:
            logger.info("Successfully connected to Qdrant")
            print("Connection to Qdrant established successfully!")
        else:
            logger.error("Failed to connect to Qdrant")
            print("Failed to connect to Qdrant")
            return 1

        # Perform retrieval
        logger.info("Performing retrieval based on the query...")
        retrieval_service = RetrievalService(connection_service)
        retrieved_chunks = retrieval_service.retrieve_content(args.query, args.top_k)

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
        print(f"Retrieved {len(retrieved_chunks)} relevant chunks:")

        for i, chunk in enumerate(retrieved_chunks, 1):
            print(f"{i}. Content: {chunk.content[:100]}..." if len(chunk.content) > 100 else f"{i}. Content: {chunk.content}")
            print(f"   Source: {chunk.source_url}")
            print(f"   Score: {chunk.score}")
            print()

        # Perform validation if expected sources are provided
        if args.expected_sources:
            logger.info("Validating retrieved results against expected sources...")
            validation_service = ValidationService(connection_service)
            validation_result = validation_service.validate_retrieved_chunks(
                args.query,
                retrieved_chunks,
                args.expected_sources
            )

            logger.info(f"Validation result: {'PASSED' if validation_result.validation_passed else 'FAILED'}")
            print(f"\nValidation Result:")
            print(f"  Accuracy Score: {validation_result.accuracy_score:.2f}")
            print(f"  Relevant Count: {validation_result.relevant_count}")
            print(f"  Total Retrieved: {validation_result.total_retrieved}")
            print(f"  Validation Passed: {validation_result.validation_passed}")
            print(f"  Notes: {validation_result.notes}")
        else:
            print("\nNo expected sources provided for validation. Skipping validation step.")

        return 0

    except Exception as e:
        logger.error(f"Error during RAG retrieval validation: {str(e)}", exc_info=True)
        print(f"Error during RAG retrieval validation: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())