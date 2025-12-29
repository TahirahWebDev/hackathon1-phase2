"""
Integration test for the end-to-end chat functionality.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.agent_service import AgentService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.api.chat_endpoint import chat_endpoint


class TestChatEndpointIntegration:
    
    @patch('backend.src.api.chat_endpoint.get_config')
    @patch('backend.src.api.chat_endpoint.AgentService')
    @patch('backend.src.api.chat_endpoint.RetrievalService')
    @patch('backend.src.api.chat_endpoint.QdrantConnectionService')
    def test_chat_endpoint_success(self, mock_qdrant_service, mock_retrieval_service, mock_agent_service, mock_get_config):
        """Test successful chat endpoint interaction."""
        # Arrange
        mock_get_config.return_value = {
            'OPENAI_API_KEY': 'test_key',
            'COHERE_API_KEY': 'test_cohere_key',
            'QDRANT_URL': 'https://test-qdrant-cluster.com',
            'QDRANT_API_KEY': 'test_api_key',
            'QDRANT_COLLECTION_NAME': 'documents'
        }
        
        # Mock services
        mock_qdrant_instance = Mock()
        mock_qdrant_service.return_value = mock_qdrant_instance
        
        mock_retrieval_instance = Mock()
        mock_retrieval_service.return_value = mock_retrieval_instance
        
        mock_agent_instance = Mock()
        mock_agent_service.return_value = mock_agent_instance
        mock_agent_instance.process_message.return_value = {
            "response": "This is a test response based on the book content.",
            "session_id": "test_session_123",
            "sources": [
                {
                    "title": "Test Document",
                    "url": "https://example.com/test-doc",
                    "confidence": 0.95
                }
            ],
            "timestamp": "2025-12-25T10:00:00Z"
        }
        
        test_message = "What is artificial intelligence?"
        test_session_id = "test_session_123"
        test_top_k = 5
        
        # Act
        result = chat_endpoint(
            message=test_message,
            session_id=test_session_id,
            top_k=test_top_k
        )
        
        # Assert
        assert result["response"] == "This is a test response based on the book content."
        assert result["session_id"] == "test_session_123"
        assert len(result["sources"]) == 1
        assert result["sources"][0]["title"] == "Test Document"
        assert result["sources"][0]["url"] == "https://example.com/test-doc"
        assert result["sources"][0]["confidence"] == 0.95
        assert "timestamp" in result
        
        # Verify that the agent service process_message was called
        mock_agent_instance.process_message.assert_called_once_with(
            message=test_message,
            session_id=test_session_id,
            options={"top_k": test_top_k}
        )
    
    def test_chat_endpoint_empty_message(self):
        """Test that chat endpoint with empty message raises HTTPException."""
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            chat_endpoint(message="", session_id="test_session", top_k=5)
        
        assert exc_info.value.status_code == 400
        assert "Message cannot be empty" in exc_info.value.detail
    
    def test_chat_endpoint_invalid_top_k(self):
        """Test that chat endpoint with invalid top_k raises HTTPException."""
        from fastapi import HTTPException
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            chat_endpoint(message="test message", session_id="test_session", top_k=0)
        
        assert exc_info.value.status_code == 400
        assert "top_k must be between 1 and 100" in exc_info.value.detail
        
        with pytest.raises(HTTPException) as exc_info:
            chat_endpoint(message="test message", session_id="test_session", top_k=150)
        
        assert exc_info.value.status_code == 400
        assert "top_k must be between 1 and 100" in exc_info.value.detail