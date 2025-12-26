"""
Unit tests for the ValidationService.
"""
import pytest
from unittest.mock import Mock
from backend.src.services.validation_service import ValidationService
from backend.src.models.retrieved_chunk import RetrievedChunk


class TestValidationService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a mock QdrantConnectionService
        self.mock_qdrant_service = Mock()
        self.service = ValidationService(self.mock_qdrant_service)
    
    def test_validate_retrieval_accuracy_valid_inputs(self):
        """Test validation with valid inputs."""
        # Arrange
        query = "test query"
        expected_sources = ["https://example.com/doc1", "https://example.com/doc2"]
        top_k = 5
        
        # Act
        result = self.service.validate_retrieval_accuracy(query, expected_sources, top_k)
        
        # Assert
        assert result.query_id == str(hash(query))
        assert result.expected_chunks == expected_sources
        assert result.total_retrieved == 0  # Placeholder implementation
        assert result.accuracy_score == 0.0  # Placeholder implementation
        assert result.notes == "This is a placeholder implementation - extend with actual validation logic"
    
    def test_validate_retrieval_accuracy_empty_query(self):
        """Test validation with empty query raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_retrieval_accuracy("", ["https://example.com"], 5)
        
        assert "Query text cannot be empty" in str(exc_info.value)
    
    def test_validate_retrieval_accuracy_empty_expected_sources(self):
        """Test validation with empty expected sources raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_retrieval_accuracy("test query", [], 5)
        
        assert "Expected sources list cannot be empty for validation" in str(exc_info.value)
    
    def test_calculate_relevance_score(self):
        """Test relevance scoring calculation."""
        # Arrange
        query = "machine learning algorithm"
        chunk_content = "This document discusses machine learning and various algorithms used in AI"
        
        # Act
        score = self.service.calculate_relevance_score(query, chunk_content)
        
        # Assert
        assert 0.0 <= score <= 1.0
        # At least "machine" and "learning" should match
        assert score > 0.0
    
    def test_calculate_relevance_score_no_match(self):
        """Test relevance scoring when there's no match."""
        # Arrange
        query = "machine learning"
        chunk_content = "This document is about cooking recipes"
        
        # Act
        score = self.service.calculate_relevance_score(query, chunk_content)
        
        # Assert
        assert score == 0.0
    
    def test_calculate_relevance_score_empty_query(self):
        """Test relevance scoring with empty query."""
        # Arrange
        query = ""
        chunk_content = "This document is about machine learning"
        
        # Act
        score = self.service.calculate_relevance_score(query, chunk_content)
        
        # Assert
        assert score == 0.0
    
    def test_validate_retrieved_chunks(self):
        """Test validation of retrieved chunks against expected sources."""
        # Arrange
        from datetime import datetime
        
        query = "test query"
        retrieved_chunks = [
            RetrievedChunk(
                id="chunk_1",
                content="Content of first chunk",
                source_url="https://example.com/doc1",
                title="Doc 1",
                score=0.9,
                created_at=datetime.now()
            ),
            RetrievedChunk(
                id="chunk_2",
                content="Content of second chunk",
                source_url="https://example.com/doc2",
                title="Doc 2",
                score=0.8,
                created_at=datetime.now()
            ),
            RetrievedChunk(
                id="chunk_3",
                content="Content of third chunk",
                source_url="https://example.com/doc3",
                title="Doc 3",
                score=0.7,
                created_at=datetime.now()
            )
        ]
        expected_sources = ["https://example.com/doc1", "https://example.com/doc2", "https://example.com/doc4"]
        
        # Act
        result = self.service.validate_retrieved_chunks(query, retrieved_chunks, expected_sources)
        
        # Assert
        assert result.query_id == str(hash(query))
        assert result.total_retrieved == 3
        assert result.relevant_count == 2  # doc1 and doc2 were retrieved
        assert result.accuracy_score == 2/3  # 2 out of 3 expected sources were retrieved
        assert result.validation_passed is False  # Less than 80% threshold
        assert "Matched 2 of 3 expected sources" in result.notes
    
    def test_validate_retrieved_chunks_all_match(self):
        """Test validation when all expected sources are retrieved."""
        # Arrange
        from datetime import datetime
        
        query = "test query"
        retrieved_chunks = [
            RetrievedChunk(
                id="chunk_1",
                content="Content of first chunk",
                source_url="https://example.com/doc1",
                title="Doc 1",
                score=0.9,
                created_at=datetime.now()
            ),
            RetrievedChunk(
                id="chunk_2",
                content="Content of second chunk",
                source_url="https://example.com/doc2",
                title="Doc 2",
                score=0.8,
                created_at=datetime.now()
            )
        ]
        expected_sources = ["https://example.com/doc1", "https://example.com/doc2"]
        
        # Act
        result = self.service.validate_retrieved_chunks(query, retrieved_chunks, expected_sources)
        
        # Assert
        assert result.total_retrieved == 2
        assert result.relevant_count == 2  # Both expected sources were retrieved
        assert result.accuracy_score == 1.0  # 100% accuracy
        assert result.validation_passed is True  # Greater than 80% threshold