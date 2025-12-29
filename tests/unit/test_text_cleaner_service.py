"""
Unit tests for the TextCleanerService.
"""
import pytest
from backend.src.services.text_cleaner_service import TextCleanerService


class TestTextCleanerService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.text_cleaner_service = TextCleanerService()
    
    def test_clean_content_basic(self):
        """Test basic content cleaning."""
        # Arrange
        raw_content = "<html><head><title>Test Page</title></head><body><p>Test content</p></body></html>"
        
        # Act
        result = self.text_cleaner_service.clean_content(raw_content, "https://example.com")
        
        # Assert
        assert "Test content" in result
        assert "Test Page" not in result  # Title should not be in main content
        assert "<p>" not in result  # HTML tags should be removed
        assert "<html>" not in result  # HTML tags should be removed
    
    def test_clean_content_with_code_blocks(self):
        """Test content cleaning preserves code blocks."""
        # Arrange
        raw_content = "<html><body><p>Here is some code:</p><pre><code>print('Hello, world!')</code></pre></body></html>"
        
        # Act
        result = self.text_cleaner_service.clean_content(raw_content, "https://example.com")
        
        # Assert
        assert "print('Hello, world!')" in result
        assert "```" in result  # Code block markers should be preserved
    
    def test_clean_content_with_headings(self):
        """Test content cleaning preserves headings."""
        # Arrange
        raw_content = "<html><body><h1>Main Heading</h1><h2>Sub Heading</h2><p>Some text</p></body></html>"
        
        # Act
        result = self.text_cleaner_service.clean_content(raw_content, "https://example.com")
        
        # Assert
        assert "Main Heading" in result
        assert "Sub Heading" in result
    
    def test_clean_content_empty(self):
        """Test cleaning empty content."""
        # Arrange
        raw_content = ""
        
        # Act
        result = self.text_cleaner_service.clean_content(raw_content, "https://example.com")
        
        # Assert
        assert result == ""
    
    def test_clean_content_with_scripts_and_styles(self):
        """Test content cleaning removes script and style elements."""
        # Arrange
        raw_content = "<html><head><style>body { color: red; }</style></head><body><script>alert('test');</script><p>Test content</p></body></html>"
        
        # Act
        result = self.text_cleaner_service.clean_content(raw_content, "https://example.com")
        
        # Assert
        assert "Test content" in result
        assert "alert('test')" not in result  # Script content should be removed
        assert "color: red" not in result  # Style content should be removed