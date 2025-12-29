"""
Integration test for the embedding pipeline.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.embedding_service import EmbeddingService
from backend.src.services.storage_service import StorageService
from backend.src.models.document_chunk import DocumentChunk
from backend.src.models.embedding_vector import EmbeddingVector


class TestEmbeddingPipeline:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.qdrant_url = "https://test-qdrant-cluster.com"
        self.qdrant_api_key = "test_qdrant_api_key"
        self.collection_name = "test_documents"
    
    @patch('backend.src.services.embedding_service.cohere.Client')
    @patch('backend.src.services.storage_service.QdrantClient')
    def test_embedding_and_storage_pipeline(self, mock_qdrant_client, mock_cohere_client):
        """
        Test the end-to-end embedding and storage pipeline.
        """
        # Arrange
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [
            [0.1, 0.2, 0.3, 0.4, 0.5] * 205,  # Example 1025-dim vector
            [0.6, 0.7, 0.8, 0.9, 1.0] * 205   # Another example 1025-dim vector
        ]
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_client.return_value = mock_qdrant_instance
        
        # Mock the get_collections method to return an empty list
        mock_collections = Mock()
        mock_collections.collections = []
        mock_qdrant_instance.get_collections.return_value = mock_collections
        
        # Create document chunks
        chunks = [
            DocumentChunk(
                id="chunk_1",
                content="This is the first test document chunk with some meaningful content.",
                source_url="https://example.com/page1",
                section_title="Section 1"
            ),
            DocumentChunk(
                id="chunk_2",
                content="This is the second test document chunk with different but related content.",
                source_url="https://example.com/page2",
                section_title="Section 2"
            )
        ]
        
        # Initialize services
        embedding_service = EmbeddingService(api_key=self.api_key)
        storage_service = StorageService(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            collection_name=self.collection_name
        )
        
        # Act - Generate embeddings
        embeddings = embedding_service.generate_embeddings(chunks)
        
        # Store embeddings
        store_success = storage_service.store_embeddings(embeddings)
        
        # Assert
        assert len(embeddings) == 2
        assert isinstance(embeddings[0], EmbeddingVector)
        assert embeddings[0].document_chunk_id == "chunk_1"
        assert embeddings[1].document_chunk_id == "chunk_2"
        assert len(embeddings[0].vector) == 1025  # 5 * 205 elements
        assert len(embeddings[1].vector) == 1025  # 5 * 205 elements
        assert store_success is True
        
        # Verify that the Cohere client was called with the right parameters
        mock_cohere_instance.embed.assert_called_once()
        
        # Verify that the Qdrant client upsert was called
        mock_qdrant_instance.upsert.assert_called_once()
        call_args = mock_qdrant_instance.upsert.call_args
        assert call_args[1]['collection_name'] == self.collection_name
        assert len(call_args[1]['points']) == 2