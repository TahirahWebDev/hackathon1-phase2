"""
Integration test for the crawling and cleaning pipeline.
"""
import pytest
from backend.src.services.crawler_service import CrawlerService
from backend.src.services.text_cleaner_service import TextCleanerService


class TestCrawlingAndCleaningPipeline:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.crawler_service = CrawlerService()
        self.text_cleaner_service = TextCleanerService()
    
    def test_crawling_and_cleaning_pipeline(self):
        """
        Test the end-to-end crawling and cleaning pipeline with a mock page.
        Note: This test uses a simple HTML string instead of actual web requests
        for reliable testing without network dependencies.
        """
        # Arrange - Create mock HTML content similar to a Docusaurus page
        mock_html_content = """
        <html>
            <head>
                <title>Mock Docusaurus Page</title>
            </head>
            <body>
                <main>
                    <article>
                        <h1>Getting Started Guide</h1>
                        <p>This is a guide to help you get started with our product.</p>
                        <h2>Installation</h2>
                        <p>To install, run:</p>
                        <pre><code>npm install our-product</code></pre>
                        <p>Then configure as needed.</p>
                        <h2>Usage</h2>
                        <p>After installation, you can use the product as follows:</p>
                        <pre><code>import { Product } from 'our-product';
const instance = new Product();
instance.doSomething();</code></pre>
                    </article>
                </main>
            </body>
        </html>
        """
        
        # Mock the crawler service to return our test content
        from unittest.mock import patch
        with patch.object(self.crawler_service, '_crawl_single_url') as mock_crawl:
            # Create a mock CrawledPage
            from backend.src.models.crawled_page import CrawledPage
            from datetime import datetime
            mock_page = CrawledPage(
                id="test_page_1",
                url="https://example.com/test",
                raw_content=mock_html_content,
                clean_content="",
                title="Mock Docusaurus Page",
                status_code=200,
                created_at=datetime.now(),
                crawled_at=datetime.now()
            )
            mock_crawl.return_value = mock_page
            
            # Act - Crawl the URL (using our mocked response)
            crawled_pages = self.crawler_service.crawl_urls(["https://example.com/test"])
            
            # Clean the content
            for page in crawled_pages:
                page.clean_content = self.text_cleaner_service.clean_content(page.raw_content, page.url)
            
            # Assert
            assert len(crawled_pages) == 1
            page = crawled_pages[0]
            
            # Check that the crawled page has the expected content
            assert "Getting Started Guide" in page.clean_content
            assert "npm install our-product" in page.clean_content
            assert "import { Product } from 'our-product'" in page.clean_content
            assert "Installation" in page.clean_content
            assert "Usage" in page.clean_content
            
            # Check that HTML tags are removed
            assert "<p>" not in page.clean_content
            assert "<h1>" not in page.clean_content
            assert "<pre>" not in page.clean_content
            
            print(f"Cleaned content: {page.clean_content}")