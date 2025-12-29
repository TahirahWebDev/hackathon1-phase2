"""
Integration test for the Qdrant connection functionality.
"""
import pytest
from unittest.mock import patch
from backend.src.services.qdrant_connection_service import QdrantConnectionService


class TestConnectionIntegration:
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_complete_connection_flow(self, mock_qdrant_client):
        """
        Test the complete connection flow from initialization to connection.
        """
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        
        # Mock the get_collections method to return a collection list
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="documents")]
        mock_client_instance.get_collections.return_value = mock_collections
        
        service = QdrantConnectionService()
        test_url = "https://test-qdrant-cluster.com"
        test_api_key = "test_api_key"
        test_collection_name = "documents"
        
        # Act
        connect_result = service.connect(test_url, test_api_key, test_collection_name)
        is_connected_result = service.is_connected()
        client = service.get_client()
        
        # Assert
        assert connect_result is True
        assert is_connected_result is True
        assert client is not None
        assert service.connection is not None
        assert service.connection.url == test_url
        assert service.connection.collection_name == test_collection_name
        assert service.connection.status == "connected"
        
        # Verify that the client was properly set
        assert service.client == mock_client_instance
    
    @patch('backend.src.services.qdrant_connection_service.QdrantClient')
    def test_connection_with_retriever_script(self, mock_qdrant_client):
        """
        Test that the connection functionality works with the retrieve.py script.
        """
        # Arrange
        from retrieve import main
        import sys
        from io import StringIO
        
        # Mock the Qdrant client
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance
        
        # Mock the get_collections method to return a collection list
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="documents")]
        mock_client_instance.get_collections.return_value = mock_collections
        
        # Mock the config loader to return test values
        with patch('retrieve.get_config') as mock_config:
            mock_config.return_value = {
                'QDRANT_URL': 'https://test-qdrant-cluster.com',
                'QDRANT_API_KEY': 'test_api_key',
                'QDRANT_COLLECTION_NAME': 'documents',
                'LOG_LEVEL': 'INFO'
            }
            
            # Capture stdout
            captured_output = StringIO()
            sys.stdout = captured_output
            
            # Simulate command line arguments
            with patch('sys.argv', ['retrieve.py', '--query', 'test query']):
                # Act
                result = main()
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            # Assert
            assert result == 0  # The script should return 0 (success)
            output = captured_output.getvalue()
            assert "Connection to Qdrant established successfully!" in output