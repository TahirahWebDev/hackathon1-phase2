"""
Unit tests for the AgentService.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.agent_service import AgentService
from backend.src.models.retrieved_chunk import RetrievedChunk


class TestAgentService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock retrieval service
        self.mock_retrieval_service = Mock()
        self.agent_service = AgentService(self.mock_retrieval_service)
    
    @patch('backend.src.services.agent_service.OpenAI')
    def test_process_message_success(self, mock_openai_client):
        """Test successful processing of a message."""
        # Arrange
        test_message = "What is artificial intelligence?"
        test_session_id = "test_session_123"
        test_top_k = 5
        
        # Mock retrieval service response
        mock_chunk = Mock(spec=RetrievedChunk)
        mock_chunk.content = "Artificial intelligence is a branch of computer science..."
        mock_chunk.source_url = "https://example.com/ai-definition"
        mock_chunk.title = "Definition of AI"
        mock_chunk.score = 0.95
        self.mock_retrieval_service.retrieve_content.return_value = [mock_chunk]
        
        # Act
        result = self.agent_service.process_message(
            message=test_message,
            session_id=test_session_id,
            options={"top_k": test_top_k}
        )
        
        # Assert
        assert "response" in result
        assert "session_id" in result
        assert "sources" in result
        assert result["session_id"] == test_session_id
        assert len(result["sources"]) == 1
        assert result["sources"][0]["title"] == "Definition of AI"
        assert result["sources"][0]["url"] == "https://example.com/ai-definition"
        
        # Verify that the retrieval service was called with correct parameters
        self.mock_retrieval_service.retrieve_content.assert_called_once_with(
            test_message, test_top_k
        )
    
    def test_process_message_empty_query(self):
        """Test that processing an empty message raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.agent_service.process_message("")
        
        assert "Message cannot be empty" in str(exc_info.value)
    
    def test_process_message_whitespace_only_query(self):
        """Test that processing a whitespace-only message raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.agent_service.process_message("   \t\n  ")
        
        assert "Message cannot be empty" in str(exc_info.value)
    
    def test_process_message_no_results(self):
        """Test processing a message when no results are returned."""
        # Arrange
        test_message = "What is a non-existent concept?"
        
        # Mock retrieval service to return no results
        self.mock_retrieval_service.retrieve_content.return_value = []
        
        # Act
        result = self.agent_service.process_message(test_message)
        
        # Assert
        assert "response" in result
        assert "I don't have that information in the book content." in result["response"]
        assert "sources" in result
        assert result["sources"] == []