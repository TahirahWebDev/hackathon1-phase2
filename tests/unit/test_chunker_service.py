"""
Unit tests for the ChunkerService.
"""
import pytest
from backend.src.services.chunker_service import ChunkerService
from backend.src.models.document_chunk import DocumentChunk


class TestChunkerService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.chunker_service = ChunkerService(chunk_size=50, overlap=10)
    
    def test_chunk_content_basic(self):
        """Test basic content chunking."""
        # Arrange
        content = "This is a test sentence. This is another sentence. And a third one. And finally a fourth."
        source_url = "https://example.com/test"
        
        # Act
        result = self.chunker_service.chunk_content(content, source_url)
        
        # Assert
        assert len(result) > 0
        for chunk in result:
            assert isinstance(chunk, DocumentChunk)
            assert len(chunk.content) <= 50  # Within chunk size
            assert chunk.source_url == source_url
    
    def test_chunk_content_with_defaults(self):
        """Test content chunking with default parameters."""
        # Arrange
        content = "This is a longer piece of content that will definitely need to be split into multiple chunks because it exceeds the default chunk size."
        source_url = "https://example.com/test"
        
        # Act
        result = self.chunker_service.chunk_content(content, source_url)
        
        # Assert
        assert len(result) > 1  # Should be split into multiple chunks
        for chunk in result:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.source_url == source_url
            assert len(chunk.content) > 0
    
    def test_chunk_content_with_custom_params(self):
        """Test content chunking with custom parameters."""
        # Arrange
        content = "This is a test sentence. This is another sentence. And a third one. And finally a fourth. And a fifth. And a sixth."
        source_url = "https://example.com/test"
        
        # Act
        result = self.chunker_service.chunk_content(content, source_url, chunk_size=30, overlap=5)
        
        # Assert
        assert len(result) > 0
        for chunk in result:
            assert isinstance(chunk, DocumentChunk)
            assert len(chunk.content) <= 30  # Within custom chunk size
            assert chunk.source_url == source_url
    
    def test_chunk_content_empty(self):
        """Test chunking empty content."""
        # Arrange
        content = ""
        source_url = "https://example.com/test"
        
        # Act
        result = self.chunker_service.chunk_content(content, source_url)
        
        # Assert
        assert len(result) == 0
    
    def test_chunk_content_shorter_than_chunk_size(self):
        """Test content that is shorter than the chunk size."""
        # Arrange
        content = "Short content"
        source_url = "https://example.com/test"
        
        # Act
        result = self.chunker_service.chunk_content(content, source_url, chunk_size=100)
        
        # Assert
        assert len(result) == 1
        assert result[0].content == content
        assert result[0].source_url == source_url
    
    def test_chunk_content_respects_sentence_boundaries(self):
        """Test that chunking tries to respect sentence boundaries."""
        # Arrange
        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        source_url = "https://example.com/test"
        
        # Use a chunk size that would split mid-sentence if we didn't respect boundaries
        # Act
        result = self.chunker_service.chunk_content(content, source_url, chunk_size=25, overlap=5)
        
        # Assert
        assert len(result) > 0
        for chunk in result:
            assert isinstance(chunk, DocumentChunk)
            # Check that chunks don't end mid-sentence when possible
            chunk_text = chunk.content.strip()
            if len(chunk_text) < len(content):  # Not the last chunk
                # If the chunk ends with a space, it likely broke mid-sentence
                # If it ends with punctuation, it respected the sentence boundary
                assert chunk_text.endswith(('.', '!', '?')) or ' ' not in chunk_text