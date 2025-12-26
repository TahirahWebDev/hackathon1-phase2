"""
Service for retrieving content from the Qdrant vector database based on similarity search.
"""
import logging
from typing import List, Dict, Any
from backend.src.models.retrieved_chunk import RetrievedChunk
from backend.src.lib.exceptions import RetrievalError, ConfigurationError
from backend.src.lib.retry_utils import retry_with_backoff


class RetrievalService:
    """
    Service class for performing similarity search in the Qdrant vector database.
    """

    def __init__(self, qdrant_client_service):
        """
        Initialize the retrieval service with a Qdrant client service.

        Args:
            qdrant_client_service: An instance of QdrantConnectionService
        """
        self.qdrant_client_service = qdrant_client_service
        self.logger = logging.getLogger(__name__)

    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
        exceptions=(Exception,),
        logger=logging.getLogger(__name__)
    )
    def retrieve_content(self, query_text: str, top_k: int = 5) -> List[RetrievedChunk]:
        """
        Performs a similarity search in the vector database.

        Args:
            query_text: The text query to search for
            top_k: Number of top results to return (default: 5)

        Returns:
            List of RetrievedChunk objects with content and metadata

        Raises:
            RetrievalError: If there's an error during retrieval
            ValueError: If query text is empty
        """
        self.logger.info(f"Starting content retrieval for query: '{query_text[:50]}...' with top_k={top_k}")

        try:
            if not query_text.strip():
                self.logger.warning("Query text is empty")
                raise ValueError("Query text cannot be empty")

            if top_k <= 0:
                self.logger.warning(f"Invalid top_k value: {top_k}")
                raise ValueError("Top-k value must be greater than 0")

            if top_k > 100:
                self.logger.warning(f"Top-k value {top_k} is too large, should be less than 100")
                raise ValueError("Top-k value should be reasonable (less than 100)")

            # Get the Qdrant client
            client = self.qdrant_client_service.get_client()
            if client is None:
                self.logger.error("Not connected to Qdrant database")
                raise RetrievalError("Not connected to Qdrant database")

            # Import cohere client to generate embeddings for the query
            import cohere
            from backend.src.lib.config_loader import get_config

            config = get_config()
            co = cohere.Client(config.get("COHERE_API_KEY"))

            self.logger.debug(f"Generating embedding for query: '{query_text[:100]}...'")
            # Generate embedding for the query text
            response = co.embed(
                texts=[query_text],
                model="embed-english-v3.0",
                input_type="search_query"
            )
            query_embedding = response.embeddings[0]

            # Get collection name from config
            collection_name = config.get("QDRANT_COLLECTION_NAME", "documents")
            self.logger.debug(f"Using collection: {collection_name}")

            # Perform similarity search in Qdrant using the new query_points method
            self.logger.debug(f"Performing similarity search with query embedding of length {len(query_embedding)}")
            search_results = client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=top_k
            ).points

            # Convert search results to RetrievedChunk objects
            retrieved_chunks = []
            from datetime import datetime
            for result in search_results:
                # Ensure we extract all relevant metadata from the result
                payload = result.payload if result.payload else {}

                # Extract source information with fallbacks
                content = payload.get("content", "") or payload.get("text", "") or payload.get("body", "")
                source_url = payload.get("source_url", "") or payload.get("url", "") or payload.get("source", "")
                title = payload.get("title", "") or payload.get("heading", "") or payload.get("header", "")

                chunk = RetrievedChunk(
                    id=str(result.id),
                    content=content,
                    source_url=source_url,
                    title=title,
                    score=result.score,
                    metadata=payload.get("metadata", {}) or {},
                    created_at=datetime.now(),
                    retrieved_at=datetime.now()
                )
                retrieved_chunks.append(chunk)

            self.logger.info(f"Successfully retrieved {len(retrieved_chunks)} chunks for query: '{query_text[:30]}...'")
            return retrieved_chunks

        except ValueError as ve:
            self.logger.warning(f"Validation error during retrieval: {str(ve)}")
            # Re-raise value errors as they're validation issues
            raise ve
        except Exception as e:
            self.logger.error(f"Error retrieving content: {str(e)}", exc_info=True)
            # Return empty list instead of raising to allow graceful degradation
            return []

    def validate_results(self, query_text: str, results: List[RetrievedChunk], expected_sources: List[str] = None) -> Dict[str, Any]:
        """
        Validates the retrieved results against expected sources or quality metrics.

        Args:
            query_text: The original query text
            results: List of retrieved chunks to validate
            expected_sources: Optional list of expected source URLs for validation

        Returns:
            Dictionary containing validation metrics and results
        """
        self.logger.info(f"Validating results for query: '{query_text[:50]}...'")

        if expected_sources is None:
            expected_sources = []

        # Count how many of the expected sources were actually retrieved
        retrieved_source_urls = [chunk.source_url for chunk in results if chunk.source_url]
        relevant_count = sum(1 for source in expected_sources if source in retrieved_source_urls)

        # Calculate accuracy score
        total_expected = len(expected_sources)
        total_retrieved = len(results)

        accuracy_score = relevant_count / total_expected if total_expected > 0 else 0.0
        validation_passed = accuracy_score >= 0.5  # 50% threshold for validation

        validation_result = {
            "query": query_text,
            "total_retrieved": total_retrieved,
            "relevant_count": relevant_count,
            "total_expected": total_expected,
            "accuracy_score": accuracy_score,
            "validation_passed": validation_passed,
            "expected_sources_found": [source for source in expected_sources if source in retrieved_source_urls]
        }

        self.logger.info(f"Validation completed: {validation_result}")
        return validation_result