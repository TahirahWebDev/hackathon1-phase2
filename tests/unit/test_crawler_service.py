"""
Unit tests for the CrawlerService.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.crawler_service import CrawlerService
from backend.src.models.crawled_page import CrawledPage


class TestCrawlerService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.crawler_service = CrawlerService()
    
    @patch('backend.src.services.crawler_service.requests.get')
    def test_crawl_single_url_success(self, mock_get):
        """Test crawling a single URL successfully."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test Page</title></head><body><p>Test content</p></body></html>'
        mock_get.return_value = mock_response
        test_url = "https://example.com"
        
        # Act
        result = self.crawler_service._crawl_single_url(test_url)
        
        # Assert
        assert isinstance(result, CrawledPage)
        assert result.url == test_url
        assert result.status_code == 200
        assert result.title == "Test Page"
        assert "Test content" in result.clean_content
        assert result.raw_content == mock_response.text
    
    @patch('backend.src.services.crawler_service.requests.get')
    def test_crawl_single_url_http_error(self, mock_get):
        """Test crawling a URL that returns an HTTP error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        test_url = "https://example.com/nonexistent"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.crawler_service._crawl_single_url(test_url)
        
        assert "HTTP 404 error" in str(exc_info.value)
    
    @patch('backend.src.services.crawler_service.requests.get')
    def test_crawl_urls_success(self, mock_get):
        """Test crawling multiple URLs successfully."""
        # Arrange
        urls = ["https://example1.com", "https://example2.com"]
        
        # Mock responses for each URL
        def mock_get_side_effect(url, *args, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = f'<html><head><title>Test Page</title></head><body><p>Content for {url}</p></body></html>'
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Act
        results = self.crawler_service.crawl_urls(urls)
        
        # Assert
        assert len(results) == 2
        for i, result in enumerate(results):
            assert isinstance(result, CrawledPage)
            assert result.url == urls[i]
            assert result.status_code == 200
            assert f"Content for {urls[i]}" in result.clean_content
    
    @patch('backend.src.services.crawler_service.requests.get')
    def test_crawl_urls_with_errors(self, mock_get):
        """Test crawling multiple URLs where some fail."""
        # Arrange
        urls = ["https://example1.com", "https://example2.com"]
        
        # Mock first succeeds, second fails
        def mock_get_side_effect(url, *args, **kwargs):
            if "example1" in url:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '<html><head><title>Test Page</title></head><body><p>Content for example1</p></body></html>'
                return mock_response
            else:
                mock_response = Mock()
                mock_response.status_code = 404
                return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Act
        results = self.crawler_service.crawl_urls(urls)
        
        # Assert
        assert len(results) == 2
        # First result should be successful
        assert isinstance(results[0], CrawledPage)
        assert results[0].url == urls[0]
        assert results[0].status_code == 200
        # Second result should be an error record
        assert isinstance(results[1], CrawledPage)
        assert results[1].url == urls[1]
        assert results[1].error_message is not None
        assert "404" in results[1].error_message