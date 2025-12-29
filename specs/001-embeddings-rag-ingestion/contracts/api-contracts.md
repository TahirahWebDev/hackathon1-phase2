# API Contracts: RAG Content Ingestion Pipeline

## Overview
This document defines the API contracts for the RAG content ingestion pipeline. Since this is primarily a command-line application, these contracts represent the internal service interfaces that can be used programmatically.

## Service Contracts

### 1. Crawler Service Contract

#### Interface: CrawlerService
```python
class CrawlerService:
    def crawl_urls(self, urls: List[str]) -> List[CrawledPage]:
        """
        Crawls a list of URLs and returns the crawled page data.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of CrawledPage objects with content and metadata
            
        Raises:
            CrawlerError: If crawling fails for any URL
        """
        pass
```

#### Input Validation
- URLs must be valid and accessible
- Maximum 100 URLs per request (configurable)
- Each URL must be less than 2048 characters

#### Output Schema
```json
{
  "id": "unique-identifier",
  "url": "https://example.com",
  "raw_content": "HTML content string",
  "clean_content": "Clean text content",
  "title": "Page title",
  "status_code": 200,
  "crawled_at": "2025-12-25T10:00:00Z",
  "error_message": null
}
```

### 2. Text Cleaner Service Contract

#### Interface: TextCleanerService
```python
class TextCleanerService:
    def clean_content(self, raw_content: str, source_url: str) -> str:
        """
        Cleans raw HTML content and extracts clean text.
        
        Args:
            raw_content: Raw HTML content string
            source_url: Source URL for context
            
        Returns:
            Clean text content with preserved formatting
        """
        pass
```

#### Input Validation
- Raw content must not be empty
- Source URL must be valid

#### Output Schema
```json
{
  "clean_content": "Clean text content with preserved formatting"
}
```

### 3. Chunker Service Contract

#### Interface: ChunkerService
```python
class ChunkerService:
    def chunk_content(self, content: str, source_url: str, chunk_size: int = 512, overlap: int = 20) -> List[DocumentChunk]:
        """
        Splits content into appropriately sized chunks.
        
        Args:
            content: Content to be chunked
            source_url: Source URL for the content
            chunk_size: Target size of chunks in tokens
            overlap: Overlap between chunks in tokens
            
        Returns:
            List of DocumentChunk objects
        """
        pass
```

#### Input Validation
- Content must not be empty
- Chunk size must be between 100 and 2000 tokens
- Overlap must be less than chunk_size

#### Output Schema
```json
{
  "id": "unique-identifier",
  "content": "Text content of the chunk",
  "source_url": "https://example.com",
  "section_title": "Section title",
  "metadata": {},
  "created_at": "2025-12-25T10:00:00Z"
}
```

### 4. Embedding Service Contract

#### Interface: EmbeddingService
```python
class EmbeddingService:
    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        """
        Generates embeddings for document chunks.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            List of EmbeddingVector objects with embedding vectors
        """
        pass
```

#### Input Validation
- Chunks list must not be empty
- Each chunk must have content

#### Output Schema
```json
{
  "id": "unique-identifier",
  "vector": [0.1, 0.3, 0.5, ...],
  "document_chunk_id": "reference-to-source-chunk",
  "metadata": {
    "source_url": "https://example.com",
    "section_title": "Section title"
  },
  "created_at": "2025-12-25T10:00:00Z"
}
```

### 5. Storage Service Contract

#### Interface: StorageService
```python
class StorageService:
    def store_embeddings(self, embeddings: List[EmbeddingVector]) -> bool:
        """
        Stores embeddings in the vector database.
        
        Args:
            embeddings: List of EmbeddingVector objects to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        pass
```

#### Input Validation
- Embeddings list must not be empty
- Each embedding must have a valid vector

#### Output Schema
```json
{
  "success": true,
  "stored_count": 50,
  "error_count": 0
}
```

## Error Contract

### Standard Error Response
```json
{
  "error": {
    "type": "ErrorType",
    "message": "Human-readable error message",
    "details": "Additional error details",
    "timestamp": "2025-12-25T10:00:00Z"
  }
}
```

### Common Error Types
- `CrawlerError`: Issues with crawling web pages
- `ParsingError`: Issues with parsing content
- `EmbeddingError`: Issues with generating embeddings
- `StorageError`: Issues with storing embeddings
- `ValidationError`: Issues with input validation