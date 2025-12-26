"""
Unit tests for the StorageService.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.src.services.storage_service import StorageService
from backend.src.models.embedding_vector import EmbeddingVector


class TestStorageService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.url = "https://test-qdrant-cluster.com"
        self.api_key = "test_api_key"
        self.collection_name = "test_documents"
        
        # Patch QdrantClient to avoid actual network calls
        with patch('backend.src.services.storage_service.QdrantClient') as mock_qdrant_client:
            self.mock_client_instance = Mock()
            mock_qdrant_client.return_value = self.mock_client_instance
            
            # Mock the get_collections method to return an empty list
            mock_collections = Mock()
            mock_collections.collections = []
            self.mock_client_instance.get_collections.return_value = mock_collections
            
            # Initialize the storage service
            self.storage_service = StorageService(
                url=self.url,
                api_key=self.api_key,
                collection_name=self.collection_name
            )
    
    def test_store_embeddings_success(self):
        """Test storing embeddings successfully."""
        # Arrange
        embeddings = [
            EmbeddingVector(
                id="emb_1",
                vector=[0.1, 0.2, 0.3],
                document_chunk_id="chunk_1",
                metadata={"source_url": "https://example.com/page1"}
            ),
            EmbeddingVector(
                id="emb_2",
                vector=[0.4, 0.5, 0.6],
                document_chunk_id="chunk_2",
                metadata={"source_url": "https://example.com/page2"}
            )
        ]
        
        # Act
        result = self.storage_service.store_embeddings(embeddings)
        
        # Assert
        assert result is True
        # Verify that upsert was called with the correct parameters
        self.mock_client_instance.upsert.assert_called_once()
        call_args = self.mock_client_instance.upsert.call_args
        assert call_args[1]['collection_name'] == self.collection_name
        assert len(call_args[1]['points']) == 2
    
    def test_store_embeddings_error(self):
        """Test storing embeddings when an error occurs."""
        # Arrange
        embeddings = [
            EmbeddingVector(
                id="emb_1",
                vector=[0.1, 0.2, 0.3],
                document_chunk_id="chunk_1",
                metadata={"source_url": "https://example.com/page1"}
            )
        ]
        
        # Make the upsert method raise an exception
        self.mock_client_instance.upsert.side_effect = Exception("Storage Error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.storage_service.store_embeddings(embeddings)
        
        assert "Error storing embeddings" in str(exc_info.value)
    
    def test_search_embeddings_success(self):
        """Test searching embeddings successfully."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3]
        limit = 5
        
        # Mock the search response
        mock_result = Mock()
        mock_result.id = "result_1"
        mock_result.score = 0.9
        mock_result.payload = {"source_url": "https://example.com/result1"}
        mock_result.vector = [0.1, 0.2, 0.3]
        
        self.mock_client_instance.search.return_value = [mock_result]
        
        # Act
        result = self.storage_service.search_embeddings(query_vector, limit)
        
        # Assert
        assert len(result) == 1
        assert result[0]["id"] == "result_1"
        assert result[0]["score"] == 0.9
        assert result[0]["payload"]["source_url"] == "https://example.com/result1"
        
        # Verify that search was called with correct parameters
        self.mock_client_instance.search.assert_called_once_with(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
    
    def test_search_embeddings_error(self):
        """Test searching embeddings when an error occurs."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3]
        limit = 5
        
        # Make the search method raise an exception
        self.mock_client_instance.search.side_effect = Exception("Search Error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.storage_service.search_embeddings(query_vector, limit)
        
        assert "Error searching embeddings" in str(exc_info.value)