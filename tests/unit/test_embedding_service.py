"""
Unit tests for the EmbeddingService.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.embedding_service import EmbeddingService
from backend.src.models.document_chunk import DocumentChunk


class TestEmbeddingService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.embedding_service = EmbeddingService(api_key=self.api_key)
    
    @patch('backend.src.services.embedding_service.cohere.Client')
    def test_generate_embeddings_success(self, mock_cohere_client):
        """Test generating embeddings successfully."""
        # Arrange
        mock_client_instance = Mock()
        mock_cohere_client.return_value = mock_client_instance
        
        # Mock the embed response
        mock_response = Mock()
        mock_response.embeddings = [
            [0.1, 0.2, 0.3, 0.4],  # Example embedding vector
            [0.5, 0.6, 0.7, 0.8]   # Another example embedding vector
        ]
        mock_client_instance.embed.return_value = mock_response
        
        # Create test document chunks
        chunks = [
            DocumentChunk(
                id="chunk_1",
                content="This is the first test document chunk.",
                source_url="https://example.com/page1",
                section_title="Section 1"
            ),
            DocumentChunk(
                id="chunk_2",
                content="This is the second test document chunk.",
                source_url="https://example.com/page2",
                section_title="Section 2"
            )
        ]
        
        # Act
        result = self.embedding_service.generate_embeddings(chunks)
        
        # Assert
        assert len(result) == 2
        assert result[0].document_chunk_id == "chunk_1"
        assert result[1].document_chunk_id == "chunk_2"
        assert result[0].vector == [0.1, 0.2, 0.3, 0.4]
        assert result[1].vector == [0.5, 0.6, 0.7, 0.8]
        assert result[0].metadata["source_url"] == "https://example.com/page1"
        assert result[1].metadata["source_url"] == "https://example.com/page2"
        
        # Verify the cohere client was called correctly
        mock_client_instance.embed.assert_called_once()
    
    @patch('backend.src.services.embedding_service.cohere.Client')
    def test_generate_embeddings_error(self, mock_cohere_client):
        """Test generating embeddings when an error occurs."""
        # Arrange
        mock_client_instance = Mock()
        mock_cohere_client.return_value = mock_client_instance
        
        # Mock the embed method to raise an exception
        mock_client_instance.embed.side_effect = Exception("API Error")
        
        # Create test document chunk
        chunks = [
            DocumentChunk(
                id="chunk_1",
                content="This is a test document chunk.",
                source_url="https://example.com/page1",
                section_title="Section 1"
            )
        ]
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.embedding_service.generate_embeddings(chunks)
        
        assert "Error generating embeddings" in str(exc_info.value)