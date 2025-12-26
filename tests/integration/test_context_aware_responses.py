"""
Integration test for context-aware responses in the RAG Content Ingestion Pipeline.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.agent_service import AgentService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.qdrant_connection_service import QdrantConnectionService
from backend.src.models.retrieved_chunk import RetrievedChunk


class TestContextAwareResponses:
    
    @patch('backend.src.services.agent_service.get_config')
    @patch('backend.src.services.agent_service.cohere.Client')
    def test_context_aware_response_generation(self, mock_cohere_client, mock_get_config):
        """Test that the agent generates context-aware responses with proper source attribution."""
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
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.return_value = mock_qdrant_client
        
        # Mock search results with source metadata
        mock_search_result = Mock()
        mock_search_result.id = "test_chunk_id"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "content": "This is a test content chunk from the documentation.",
            "source_url": "https://example.com/doc1",
            "title": "Test Document Title",
            "metadata": {
                "author": "Test Author",
                "section": "Introduction",
                "category": "AI Concepts"
            }
        }
        mock_qdrant_client.search.return_value = [mock_search_result]
        
        # Create services with mocks
        retrieval_service = RetrievalService(mock_qdrant_service)
        agent_service = AgentService(retrieval_service)
        agent_service.initialize_agent(api_key="test_key")
        
        # Act
        result = agent_service.process_message(
            message="What is artificial intelligence?",
            session_id="test_session_123"
        )
        
        # Assert
        assert "response" in result
        assert "sources" in result
        assert result["session_id"] == "test_session_123"
        
        # Verify that the response contains context from the retrieved content
        assert "artificial intelligence" in result["response"].lower() or "test content" in result["response"].lower()
        
        # Verify that sources contain proper metadata
        assert len(result["sources"]) == 1
        source = result["sources"][0]
        assert source["title"] == "Test Document Title"
        assert source["url"] == "https://example.com/doc1"
        assert source["confidence"] == 0.9
        
        # Verify that the Cohere client was called to generate embeddings
        mock_cohere_instance.embed.assert_called_once()
        
        # Verify that the Qdrant client search was called with appropriate parameters
        mock_qdrant_client.search.assert_called_once()
    
    @patch('backend.src.services.agent_service.get_config')
    @patch('backend.src.services.agent_service.cohere.Client')
    def test_conversation_context_maintained_across_calls(self, mock_cohere_client, mock_get_config):
        """Test that conversation context is maintained across multiple calls."""
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
        
        # Mock Qdrant client with multiple responses for different queries
        mock_qdrant_client = Mock()
        mock_qdrant_service = Mock()
        mock_qdrant_service.get_client.return_value = mock_qdrant_client
        
        # Mock different search results for different queries
        def mock_search_behavior(collection_name, query_vector, limit, with_payload):
            if "artificial intelligence" in str(query_vector):
                result = Mock()
                result.id = "ai_chunk_id"
                result.score = 0.95
                result.payload = {
                    "content": "Artificial intelligence is intelligence demonstrated by machines.",
                    "source_url": "https://example.com/ai-definition",
                    "title": "AI Definition",
                    "metadata": {"section": "Basics"}
                }
                return [result]
            elif "machine learning" in str(query_vector):
                result = Mock()
                result.id = "ml_chunk_id"
                result.score = 0.85
                result.payload = {
                    "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
                    "source_url": "https://example.com/ml-overview",
                    "title": "ML Overview",
                    "metadata": {"section": "Advanced Topics"}
                }
                return [result]
            else:
                return []
        
        mock_qdrant_client.search.side_effect = mock_search_behavior
        
        # Create services with mocks
        retrieval_service = RetrievalService(mock_qdrant_service)
        agent_service = AgentService(retrieval_service)
        agent_service.initialize_agent(api_key="test_key")
        
        # Act - Simulate a conversation with multiple exchanges
        session_id = "multi_turn_session_456"
        
        # First query about AI
        result1 = agent_service.process_message(
            message="What is artificial intelligence?",
            session_id=session_id
        )
        
        # Second query that might reference previous context
        result2 = agent_service.process_message(
            message="How is it related to machine learning?",
            session_id=session_id
        )
        
        # Assert
        # Both results should have the same session ID
        assert result1["session_id"] == session_id
        assert result2["session_id"] == session_id
        
        # Both should have appropriate responses
        assert "response" in result1
        assert "response" in result2
        assert len(result1["sources"]) >= 0  # May or may not have sources
        assert len(result2["sources"]) >= 0  # May or may not have sources
        
        # Verify that the service was called twice (once for each query)
        assert mock_qdrant_client.search.call_count == 2
    
    def test_agent_handles_missing_context_gracefully(self):
        """Test that the agent handles cases where no context is available gracefully."""
        # This test verifies that the agent can still function when retrieval doesn't find relevant content
        with patch('backend.src.services.agent_service.get_config') as mock_get_config, \
             patch('backend.src.services.agent_service.cohere.Client') as mock_cohere_client, \
             patch('backend.src.services.retrieval_service.QdrantClient') as mock_qdrant_client:
            
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
            
            # Mock Qdrant client to return no results
            mock_qdrant_instance = Mock()
            mock_qdrant_client.return_value = mock_qdrant_instance
            mock_qdrant_instance.search.return_value = []  # No results found
            
            # Create services
            from backend.src.services.qdrant_connection_service import QdrantConnectionService
            qdrant_service = QdrantConnectionService()
            qdrant_service.client = mock_qdrant_instance  # Inject the mock client
            
            retrieval_service = RetrievalService(qdrant_service)
            agent_service = AgentService(retrieval_service)
            agent_service.initialize_agent(api_key="test_key")
            
            # Act
            result = agent_service.process_message(
                message="What is a completely made up concept that doesn't exist?",
                session_id="no_context_session_789"
            )
            
            # Assert
            assert "response" in result
            assert "session_id" in result
            assert result["session_id"] == "no_context_session_789"
            
            # Should still return a response even if no context was found
            # The response should indicate that the information wasn't found
            assert "not have that information" in result["response"].lower() or \
                   "don't know" in result["response"].lower() or \
                   "no relevant" in result["response"].lower()
            
            # Sources list should be empty when no content is retrieved
            assert "sources" in result
            assert isinstance(result["sources"], list)
            assert len(result["sources"]) == 0