"""
End-to-end integration test for the full ingestion pipeline.
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.services.crawler_service import CrawlerService
from backend.src.services.text_cleaner_service import TextCleanerService
from backend.src.services.chunker_service import ChunkerService
from backend.src.services.embedding_service import EmbeddingService
from backend.src.services.storage_service import StorageService
from backend.src.models.crawled_page import CrawledPage
from datetime import datetime


class TestFullIngestionPipeline:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.qdrant_url = "https://test-qdrant-cluster.com"
        self.qdrant_api_key = "test_qdrant_api_key"
        self.collection_name = "test_documents"
    
    @patch('backend.src.services.crawler_service.requests.get')
    @patch('backend.src.services.embedding_service.cohere.Client')
    @patch('backend.src.services.storage_service.QdrantClient')
    def test_full_ingestion_pipeline(self, mock_qdrant_client, mock_cohere_client, mock_requests_get):
        """
        Test the complete end-to-end ingestion pipeline:
        1. Crawl URLs
        2. Clean content
        3. Chunk content
        4. Generate embeddings
        5. Store embeddings
        """
        # Arrange - Mock all external dependencies
        
        # Mock HTTP response for crawler
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <main>
                    <article>
                        <h1>AI Introduction</h1>
                        <p>Artificial Intelligence (AI) is intelligence demonstrated by machines.</p>
                        <p>Leading AI textbooks define the field as the study of "intelligent agents".</p>
                        <p>Modern machine learning techniques are a core part of AI.</p>
                    </article>
                </main>
            </body>
        </html>
        '''
        mock_requests_get.return_value = mock_response
        
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_client.return_value = mock_cohere_instance
        # Mock response with example embeddings (using 10-dim vectors for simplicity in test)
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1],
            [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2]
        ]
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_client.return_value = mock_qdrant_instance
        
        # Mock the get_collections method to return an empty list
        mock_collections = Mock()
        mock_collections.collections = []
        mock_qdrant_instance.get_collections.return_value = mock_collections
        
        # Initialize services
        crawler_service = CrawlerService()
        cleaner_service = TextCleanerService()
        chunker_service = ChunkerService(chunk_size=100, overlap=10)
        embedding_service = EmbeddingService(api_key=self.api_key)
        storage_service = StorageService(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            collection_name=self.collection_name
        )
        
        # Act - Run the full pipeline
        urls = ["https://example.com/ai-intro"]
        
        # Step 1: Crawl URLs
        crawled_pages = crawler_service.crawl_urls(urls)
        
        # Step 2: Clean content
        for page in crawled_pages:
            if page.raw_content:
                page.clean_content = cleaner_service.clean_content(page.raw_content, page.url)
        
        # Step 3: Chunk content
        all_chunks = []
        for page in crawled_pages:
            if page.clean_content:
                chunks = chunker_service.chunk_content(
                    content=page.clean_content,
                    source_url=page.url,
                    chunk_size=100,
                    overlap=10
                )
                all_chunks.extend(chunks)
        
        # Step 4: Generate embeddings
        embeddings = embedding_service.generate_embeddings(all_chunks)
        
        # Step 5: Store embeddings
        storage_success = storage_service.store_embeddings(embeddings)
        
        # Assert
        # Verify crawling worked
        assert len(crawled_pages) == 1
        assert crawled_pages[0].status_code == 200
        assert "Artificial Intelligence" in crawled_pages[0].clean_content
        
        # Verify chunking worked
        assert len(all_chunks) > 0
        for chunk in all_chunks:
            assert len(chunk.content) <= 100  # Within chunk size
        
        # Verify embedding generation worked
        assert len(embeddings) == len(all_chunks)  # Should have one embedding per chunk
        for emb in embeddings:
            assert len(emb.vector) == 10  # 10-dimensional vectors as mocked
        
        # Verify storage worked
        assert storage_success is True
        
        # Verify that all services were called appropriately
        mock_requests_get.assert_called_once()
        mock_cohere_instance.embed.assert_called_once()
        mock_qdrant_instance.upsert.assert_called_once()
        
        print(f"Pipeline processed {len(crawled_pages)} pages, created {len(all_chunks)} chunks, generated {len(embeddings)} embeddings")