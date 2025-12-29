"""
Integration test for the retrieval pipeline functionality.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.models.retrieval_query import RetrievalQuery


class TestRetrievalIntegration:
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_complete_retrieval_flow(self, mock_get_config, mock_cohere_client):
        """
        Test the complete retrieval flow from connection to search results.
        """
        # Arrange
        mock_get_config.return_value = {
            'COHERE_API_KEY': 'test_key',
            'QDRANT_COLLECTION_NAME': 'documents'
        }
        
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]  # Mock embedding
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Create a mock Qdrant client
        mock_qdrant_client = Mock()
        
        # Mock the QdrantConnectionService
        connection_service = Mock(spec=QdrantConnectionService)
        connection_service.get_client.return_value = mock_qdrant_client
        
        # Mock search results
        mock_search_result = Mock()
        mock_search_result.id = "test_chunk_id"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "content": "This is a test content chunk",
            "source_url": "https://example.com/doc1",
            "title": "Test Document",
            "metadata": {"author": "Test Author"}
        }
        mock_qdrant_client.search.return_value = [mock_search_result]
        
        # Create the retrieval service
        retrieval_service = RetrievalService(connection_service)
        
        # Act
        results = retrieval_service.search("test query", top_k=5)
        
        # Assert
        assert len(results) == 1
        assert results[0].content == "This is a test content chunk"
        assert results[0].source_url == "https://example.com/doc1"
        assert results[0].title == "Test Document"
        assert results[0].score == 0.9
        
        # Verify that the search was called with the correct parameters
        mock_qdrant_client.search.assert_called_once()
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_retrieval_validation_integration(self, mock_get_config, mock_cohere_client):
        """
        Test the integration between retrieval and validation.
        """
        # Arrange
        mock_get_config.return_value = {
            'COHERE_API_KEY': 'test_key',
            'QDRANT_COLLECTION_NAME': 'documents'
        }
        
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]  # Mock embedding
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Create a mock Qdrant client
        mock_qdrant_client = Mock()
        
        # Mock the QdrantConnectionService
        connection_service = Mock(spec=QdrantConnectionService)
        connection_service.get_client.return_value = mock_qdrant_client
        
        # Mock search results
        mock_search_result = Mock()
        mock_search_result.id = "test_chunk_id"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "content": "This is a test content chunk",
            "source_url": "https://example.com/doc1",
            "title": "Test Document",
            "metadata": {"author": "Test Author"}
        }
        mock_qdrant_client.search.return_value = [mock_search_result]
        
        # Create the retrieval service
        retrieval_service = RetrievalService(connection_service)
        
        # Perform search
        results = retrieval_service.search("test query", top_k=5)
        
        # Create a query for validation
        from datetime import datetime
        query = RetrievalQuery(
            id="test_query_id",
            text="test query",
            created_at=datetime.now()
        )
        
        # Perform validation
        validation_result = retrieval_service.validate_results(query, results)
        
        # Assert validation results
        assert validation_result["query_id"] == "test_query_id"
        assert validation_result["retrieved_count"] == 1
        assert validation_result["relevant_count"] == 0  # Placeholder value
        assert "accuracy_score" in validation_result
        assert "validation_passed" in validation_result