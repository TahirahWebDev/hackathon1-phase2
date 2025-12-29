"""
Unit tests for the RetrievalService.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.retrieval_service import RetrievalService
from backend.src.models.retrieved_chunk import RetrievedChunk


class TestRetrievalService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock Qdrant client service
        self.mock_qdrant_client_service = Mock()
        self.retrieval_service = RetrievalService(self.mock_qdrant_client_service)
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_retrieve_content_success(self, mock_get_config, mock_cohere_client):
        """Test successful retrieval of content based on query."""
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
        
        # Mock Qdrant client
        mock_qdrant_client = Mock()
        self.mock_qdrant_client_service.get_client.return_value = mock_qdrant_client
        
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
        
        test_query = "test query about AI"
        test_top_k = 5
        
        # Act
        results = self.retrieval_service.retrieve_content(test_query, test_top_k)
        
        # Assert
        assert len(results) == 1
        assert isinstance(results[0], RetrievedChunk)
        assert results[0].content == "This is a test content chunk"
        assert results[0].source_url == "https://example.com/doc1"
        assert results[0].title == "Test Document"
        assert results[0].score == 0.9
        assert results[0].metadata == {"author": "Test Author"}
        
        # Verify that the Cohere client was called with the right parameters
        mock_cohere_instance.embed.assert_called_once()
        # Verify that the Qdrant client search was called with the right parameters
        mock_qdrant_client.search.assert_called_once_with(
            collection_name='documents',
            query_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            limit=5
        )
    
    def test_retrieve_content_empty_query(self):
        """Test that retrieving content with an empty query raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.retrieval_service.retrieve_content("")
        
        assert "Query text cannot be empty" in str(exc_info.value)
    
    def test_retrieve_content_whitespace_only_query(self):
        """Test that retrieving content with whitespace-only query raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.retrieval_service.retrieve_content("   \t\n  ")
        
        assert "Query text cannot be empty" in str(exc_info.value)
    
    def test_retrieve_content_invalid_top_k_zero(self):
        """Test that retrieving content with top_k=0 raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.retrieval_service.retrieve_content("test query", top_k=0)
        
        assert "Top-k value must be greater than 0" in str(exc_info.value)
    
    def test_retrieve_content_invalid_top_k_negative(self):
        """Test that retrieving content with negative top_k raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.retrieval_service.retrieve_content("test query", top_k=-1)
        
        assert "Top-k value must be greater than 0" in str(exc_info.value)
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    @patch('backend.src.services.retrieval_service.get_config')
    def test_retrieve_content_max_top_k_limit(self, mock_get_config, mock_cohere_client):
        """Test that retrieving content with top_k > 100 raises ValueError."""
        # Arrange
        mock_get_config.return_value = {
            'COHERE_API_KEY': 'test_key',
            'QDRANT_COLLECTION_NAME': 'documents'
        }
        
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.retrieval_service.retrieve_content("test query", top_k=101)
        
        assert "Top-k value should be reasonable" in str(exc_info.value)