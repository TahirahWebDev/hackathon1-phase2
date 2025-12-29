"""
Unit tests for the QdrantConnectionService.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.models.qdrant_connection import QdrantConnection


class TestQdrantConnectionService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = QdrantConnectionService()
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_connect_success(self, mock_qdrant_client):
        """Test successful connection to Qdrant."""
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        
        # Mock the get_collections method to return a collection list
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="documents")]
        mock_client_instance.get_collections.return_value = mock_collections
        
        test_url = "https://test-qdrant-cluster.com"
        test_api_key = "test_api_key"
        test_collection_name = "documents"
        
        # Act
        result = self.service.connect(test_url, test_api_key, test_collection_name)
        
        # Assert
        assert result is True
        assert self.service.client is not None
        assert self.service.connection is not None
        assert self.service.connection.url == test_url
        assert self.service.connection.collection_name == test_collection_name
        assert self.service.connection.status == "connected"
        
        # Verify that the QdrantClient was called with the correct parameters
        mock_qdrant_client.assert_called_once_with(
            url=test_url,
            api_key=test_api_key,
            prefer_grpc=False
        )
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_connect_collection_not_found(self, mock_qdrant_client):
        """Test connection when the specified collection doesn't exist."""
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        
        # Mock the get_collections method to return an empty collection list
        mock_collections = Mock()
        mock_collections.collections = []
        mock_client_instance.get_collections.return_value = mock_collections
        
        test_url = "https://test-qdrant-cluster.com"
        test_api_key = "test_api_key"
        test_collection_name = "nonexistent_collection"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.connect(test_url, test_api_key, test_collection_name)
        
        assert "does not exist in Qdrant" in str(exc_info.value)
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_is_connected_when_connected(self, mock_qdrant_client):
        """Test is_connected method when connected."""
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        
        # Mock the get_collections method to simulate a working connection
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="documents")]
        mock_client_instance.get_collections.return_value = mock_collections
        
        # Establish a connection first
        self.service.connect("https://test-qdrant-cluster.com", "test_api_key", "documents")
        
        # Act
        result = self.service.is_connected()
        
        # Assert
        assert result is True
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_is_connected_when_not_connected(self, mock_qdrant_client):
        """Test is_connected method when not connected."""
        # Arrange
        # Don't establish a connection
        
        # Act
        result = self.service.is_connected()
        
        # Assert
        assert result is False
    
    def test_get_client_when_connected(self):
        """Test get_client method when connected."""
        # Arrange
        # Manually set the client to simulate a connection
        mock_client = Mock()
        self.service.client = mock_client
        
        # Act
        result = self.service.get_client()
        
        # Assert
        assert result is mock_client
    
    def test_get_client_when_not_connected(self):
        """Test get_client method when not connected."""
        # Arrange
        # Don't set the client
        
        # Act
        result = self.service.get_client()
        
        # Assert
        assert result is None