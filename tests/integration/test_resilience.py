"""
Integration tests for resilience and failure scenarios in the RAG Content Ingestion Pipeline.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the backend source to the path
sys.path.insert(0, os.path.abspath('.'))

from backend.src.services.agent_service import AgentService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.models.retrieval_query import RetrievalQuery
from backend.src.models.retrieved_chunk import RetrievedChunk
from datetime import datetime


class TestResilience:
    """Tests for system resilience under failure conditions."""
    
    def test_agent_service_with_unavailable_retrieval_service(self):
        """Test that AgentService handles unavailable retrieval service gracefully."""
        # Create a mock retrieval service that always fails
        mock_retrieval_service = Mock()
        mock_retrieval_service.retrieve_content.side_effect = Exception("Retrieval service unavailable")
        
        agent_service = AgentService(mock_retrieval_service)
        
        # When the retrieval service is unavailable, the agent should handle it gracefully
        result = agent_service.process_message("test query", "test_session")
        
        # The result should contain a graceful error response
        assert "response" in result
        assert "session_id" in result
        assert "sources" in result
        # Should not raise an exception and should return a structured response
        assert isinstance(result, dict)
    
    def test_retrieval_service_with_network_failures(self):
        """Test that RetrievalService handles network failures gracefully."""
        # Create a mock Qdrant service that simulates network failures
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.side_effect = Exception("Network connection failed")
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # When network fails, the retrieval service should return an empty list gracefully
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # Should return an empty list instead of raising an exception
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    def test_retrieval_service_with_api_rate_limiting(self, mock_cohere_client):
        """Test that RetrievalService handles API rate limiting gracefully."""
        # Mock the Cohere client to simulate rate limit error
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_instance.embed.side_effect = Exception("Rate limit exceeded")
        
        # Create a mock Qdrant service
        mock_qdrant_service = Mock()
        mock_client = Mock()
        mock_qdrant_service.get_client.return_value = mock_client
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # When API rate limit is exceeded, the service should handle it gracefully
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # Should return an empty list instead of raising an exception
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_qdrant_connection_resilience_to_temporary_outage(self):
        """Test that the system can handle temporary Qdrant outages."""
        # Create a Qdrant service that simulates a temporary outage
        qdrant_service = QdrantConnectionService()
        
        # Mock the client creation to fail temporarily
        with patch.object(qdrant_service, '_create_client', side_effect=Exception("Temporary outage")):
            # When Qdrant is temporarily unavailable, get_client should return None
            client = qdrant_service.get_client()
            assert client is None
    
    @patch('backend.src.services.agent_service.cohere.Client')
    def test_agent_service_with_partial_failure_in_pipeline(self, mock_cohere_client):
        """Test that AgentService can handle partial failures in the pipeline."""
        # Mock Cohere client to work properly
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]  # Mock embedding
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Create a mock retrieval service that returns some results but with missing metadata
        mock_retrieval_service = Mock()
        incomplete_chunk = RetrievedChunk(
            id="partial_chunk_1",
            content="Partial content without complete metadata",
            source_url="",
            title="",
            score=0.7,
            metadata={},
            created_at=datetime.now(),
            retrieved_at=datetime.now()
        )
        mock_retrieval_service.retrieve_content.return_value = [incomplete_chunk]
        
        agent_service = AgentService(mock_retrieval_service)
        
        # Even with partial/incomplete results, the agent should handle it gracefully
        result = agent_service.process_message("test query", "test_session")
        
        # The result should still be a proper response structure
        assert "response" in result
        assert "session_id" in result
        assert "sources" in result
        assert isinstance(result["sources"], list)
    
    def test_system_resilience_to_invalid_queries(self):
        """Test that the system handles invalid or malicious queries gracefully."""
        # Create a mock retrieval service
        mock_qdrant_service = Mock()
        mock_client = Mock()
        mock_qdrant_service.get_client.return_value = mock_client
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # Test with various problematic queries
        problematic_queries = [
            "",  # Empty query
            "   ",  # Whitespace only
            "\n\t",  # Control characters only
            "a" * 10000,  # Extremely long query
        ]
        
        for query in problematic_queries:
            try:
                # For empty/whitespace queries, we expect a ValueError
                if not query.strip():
                    with pytest.raises(ValueError):
                        retrieval_service.retrieve_content(query, top_k=5)
                else:
                    # For other queries, it should handle gracefully (may return empty results)
                    result = retrieval_service.retrieve_content(query, top_k=5)
                    assert isinstance(result, list)
            except ValueError:
                # ValueError for empty queries is expected behavior
                assert not query.strip()
    
    @patch('backend.src.services.retrieval_service.cohere.Client')
    def test_pipeline_resilience_with_multiple_simultaneous_failures(self, mock_cohere_client):
        """Test resilience when multiple components fail simultaneously."""
        # Mock Cohere to fail
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        mock_cohere_instance.embed.side_effect = Exception("Cohere service unavailable")
        
        # Mock Qdrant service to also fail
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.side_effect = Exception("Qdrant service unavailable")
        
        retrieval_service = RetrievalService(mock_qdrant_service)
        
        # When both Cohere and Qdrant services fail, retrieval should handle gracefully
        result = retrieval_service.retrieve_content("test query", top_k=5)
        
        # Should return empty list instead of propagating the exception
        assert isinstance(result, list)
        assert len(result) == 0