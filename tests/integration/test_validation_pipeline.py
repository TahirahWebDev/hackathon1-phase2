"""
End-to-end integration test for the full validation pipeline.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.validation_service import ValidationService


class TestValidationPipelineIntegration:
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_end_to_end_validation_pipeline(self, mock_get_config, mock_cohere_client):
        """
        Test the complete end-to-end validation pipeline from connection to validation.
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
            "content": "This is a test content chunk relevant to the query",
            "source_url": "https://example.com/doc1",
            "title": "Test Document",
            "metadata": {"author": "Test Author"}
        }
        mock_qdrant_client.search.return_value = [mock_search_result]
        
        # Create the retrieval service
        retrieval_service = RetrievalService(connection_service)
        
        # Create the validation service
        validation_service = ValidationService(connection_service)
        
        # Act - Perform retrieval
        retrieved_chunks = retrieval_service.search("test query about content", top_k=5)
        
        # Act - Perform validation
        expected_sources = ["https://example.com/doc1", "https://example.com/doc2"]
        validation_result = validation_service.validate_retrieved_chunks(
            "test query about content",
            retrieved_chunks,
            expected_sources
        )
        
        # Assert
        # Check retrieval results
        assert len(retrieved_chunks) == 1
        assert retrieved_chunks[0].content == "This is a test content chunk relevant to the query"
        assert retrieved_chunks[0].source_url == "https://example.com/doc1"
        assert retrieved_chunks[0].score == 0.9
        
        # Check validation results
        assert validation_result.total_retrieved == 1
        assert validation_result.relevant_count == 1  # Only 1 of the 2 expected sources was retrieved
        assert validation_result.accuracy_score == 1/2  # 50% accuracy (1 out of 2 expected sources)
        assert validation_result.validation_passed is False  # Below 80% threshold
        assert "Matched 1 of 2 expected sources" in validation_result.notes
        
        # Verify that the search was called
        mock_qdrant_client.search.assert_called_once()
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_validation_pipeline_with_perfect_match(self, mock_get_config, mock_cohere_client):
        """
        Test the validation pipeline when all expected sources are retrieved.
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
        
        # Mock search results with both expected sources
        mock_search_result_1 = Mock()
        mock_search_result_1.id = "test_chunk_id_1"
        mock_search_result_1.score = 0.9
        mock_search_result_1.payload = {
            "content": "This is a test content chunk relevant to the query",
            "source_url": "https://example.com/doc1",
            "title": "Test Document 1",
            "metadata": {"author": "Test Author"}
        }
        
        mock_search_result_2 = Mock()
        mock_search_result_2.id = "test_chunk_id_2"
        mock_search_result_2.score = 0.8
        mock_search_result_2.payload = {
            "content": "This is another test content chunk relevant to the query",
            "source_url": "https://example.com/doc2",
            "title": "Test Document 2",
            "metadata": {"author": "Test Author"}
        }
        
        mock_qdrant_client.search.return_value = [mock_search_result_1, mock_search_result_2]
        
        # Create the retrieval service
        retrieval_service = RetrievalService(connection_service)
        
        # Create the validation service
        validation_service = ValidationService(connection_service)
        
        # Act - Perform retrieval
        retrieved_chunks = retrieval_service.search("test query about content", top_k=5)
        
        # Act - Perform validation with both sources expected
        expected_sources = ["https://example.com/doc1", "https://example.com/doc2"]
        validation_result = validation_service.validate_retrieved_chunks(
            "test query about content",
            retrieved_chunks,
            expected_sources
        )
        
        # Assert
        # Check retrieval results
        assert len(retrieved_chunks) == 2
        
        # Check validation results
        assert validation_result.total_retrieved == 2
        assert validation_result.relevant_count == 2  # Both expected sources were retrieved
        assert validation_result.accuracy_score == 1.0  # 100% accuracy
        assert validation_result.validation_passed is True  # Above 80% threshold
        assert "Matched 2 of 2 expected sources" in validation_result.notes