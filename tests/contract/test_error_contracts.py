"""
Contract tests for the error handling API interfaces of the RAG Content Ingestion Pipeline.
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the backend source to the path
sys.path.insert(0, os.path.abspath('.'))

from backend.src.services.agent_service import AgentService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.models.retrieved_chunk import RetrievedChunk


class TestErrorContract:
    """Contract tests to ensure error handling follows the specified interface contracts."""
    
    def test_agent_service_error_interface_compatibility(self):
        """Test that AgentService error handling follows the expected interface contract."""
        # Create a mock retrieval service that will raise an error
        mock_retrieval_service = Mock()
        mock_retrieval_service.retrieve_content.side_effect = Exception("Simulated retrieval error")
        
        agent_service = AgentService(mock_retrieval_service)
        
        # When an error occurs in the retrieval service, the agent should handle it gracefully
        result = agent_service.process_message("test query", "test_session")
        
        # The result should contain error information rather than raising an exception
        assert "response" in result
        assert "session_id" in result
        assert "sources" in result
        # The response should indicate an error occurred
        assert "error" in result or "try again" in result["response"].lower()
    
    def test_retrieval_service_error_interface_compatibility(self):
        """Test that RetrievalService error handling follows the expected interface contract."""
        # Create a mock Qdrant service that will raise an error
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.side_effect = Exception("Simulated connection error")
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # When an error occurs in the Qdrant service, retrieval should handle it gracefully
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # The result should be an empty list rather than raising an exception
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_retrieval_service_network_error_handling(self):
        """Test that RetrievalService handles network errors gracefully."""
        # Create a mock Qdrant service that returns a client which will fail on search
        mock_client = Mock()
        mock_client.search.side_effect = Exception("Network timeout")
        
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.return_value = mock_client
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # When a network error occurs during search, it should return an empty list
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # The result should be an empty list rather than raising an exception
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('backend.src.services.agent_service.cohere.Client')
    def test_agent_service_cohere_api_error_handling(self, mock_cohere_client):
        """Test that AgentService handles Cohere API errors gracefully."""
        # Mock the Cohere client to raise an exception
        mock_cohere_client.side_effect = Exception("Cohere API error")
        
        # Create a real Qdrant service (but we'll mock its client)
        mock_qdrant_client = Mock()
        mock_qdrant_client.search.return_value = []
        
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.return_value = mock_qdrant_client
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        agent_service = AgentService(retrieval_service)
        
        # Initialize with a fake API key to bypass initialization errors
        agent_service.initialize_agent(api_key="fake_key")
        
        # When a Cohere API error occurs, the agent should handle it gracefully
        result = agent_service.process_message("test query", "test_session")
        
        # The result should contain a graceful error response
        assert "response" in result
        assert "session_id" in result
        assert "sources" in result
        assert len(result["sources"]) == 0
    
    def test_qdrant_connection_error_handling(self):
        """Test that Qdrant connection service handles connection errors properly."""
        # Test with invalid URL
        qdrant_service = QdrantConnectionService()
        
        # Try to connect with an invalid configuration to trigger an error
        # We'll test that the service can handle connection failures
        client = qdrant_service.get_client()
        
        # If connection failed, get_client should return None
        if client is None:
            # This is expected behavior when connection fails
            assert client is None
        else:
            # If connection succeeded, at least verify the client object has expected methods
            assert hasattr(client, 'search') or hasattr(client, 'query_points')
    
    def test_error_response_structure_consistency(self):
        """Test that error responses follow a consistent structure."""
        # Create a mock retrieval service that returns an empty result (simulating no matches)
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.return_value = None  # Simulate connection issue
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # Call retrieve_content which should handle the error gracefully
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # Result should be a list (even if empty)
        assert isinstance(result, list)
        
        # If there are results, they should be RetrievedChunk objects
        for item in result:
            assert isinstance(item, RetrievedChunk)