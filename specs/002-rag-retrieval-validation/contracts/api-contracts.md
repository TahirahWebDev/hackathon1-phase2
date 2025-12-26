# API Contracts: RAG Retrieval Validation

## Overview
This document defines the API contracts for the RAG retrieval validation system. Since this is primarily a command-line application, these contracts represent the internal service interfaces that can be used programmatically.

## Service Contracts

### 1. Qdrant Connection Service Contract

#### Interface: QdrantConnectionService
```python
class QdrantConnectionService:
    def connect(self, url: str, api_key: str, collection_name: str) -> bool:
        """
        Establishes a connection to the Qdrant vector database.
        
        Args:
            url: Qdrant cluster URL
            api_key: Qdrant API key
            collection_name: Name of the collection to connect to
            
        Returns:
            True if connection is successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Checks if the service is currently connected to Qdrant.
        
        Returns:
            True if connected, False otherwise
        """
        pass
```

#### Input Validation
- URL must be a valid URL format
- API key must not be empty
- Collection name must not be empty

#### Output Schema
```json
{
  "success": true,
  "connection_id": "unique-identifier",
  "connected_at": "2025-12-25T10:00:00Z"
}
```

### 2. Retrieval Service Contract

#### Interface: RetrievalService
```python
class RetrievalService:
    def search(self, query_text: str, top_k: int = 5) -> List[RetrievedChunk]:
        """
        Performs a similarity search in the vector database.
        
        Args:
            query_text: The text query to search for
            top_k: Number of top results to return (default: 5)
            
        Returns:
            List of RetrievedChunk objects with content and metadata
            
        Raises:
            ConnectionError: If not connected to the database
            ValueError: If query text is empty
        """
        pass
    
    def validate_results(self, query: RetrievalQuery, results: List[RetrievedChunk]) -> ValidationResult:
        """
        Validates that retrieved results match expected content and metadata.
        
        Args:
            query: The original retrieval query
            results: List of retrieved chunks to validate
            
        Returns:
            ValidationResult object with accuracy metrics
        """
        pass
```

#### Input Validation
- Query text must not be empty
- Top-k value must be greater than 0
- Top-k value should be reasonable (e.g., less than 100)

#### Output Schema
```json
{
  "retrieved_chunks": [
    {
      "id": "chunk-identifier",
      "content": "text content of the chunk",
      "source_url": "https://source-document-url.com",
      "title": "Document title",
      "score": 0.85,
      "metadata": {
        "additional": "metadata fields"
      },
      "retrieved_at": "2025-12-25T10:00:00Z"
    }
  ],
  "query_id": "query-identifier",
  "search_performed_at": "2025-12-25T10:00:00Z"
}
```

### 3. Validation Service Contract

#### Interface: ValidationService
```python
class ValidationService:
    def validate_retrieval_accuracy(self, query: str, expected_sources: List[str], top_k: int = 5) -> ValidationResult:
        """
        Validates the accuracy of retrieval for a given query.
        
        Args:
            query: The query text to validate
            expected_sources: List of source URLs that should be returned
            top_k: Number of top results to check (default: 5)
            
        Returns:
            ValidationResult with accuracy metrics
        """
        pass
    
    def calculate_relevance_score(self, query: str, chunk_content: str) -> float:
        """
        Calculates a relevance score between a query and chunk content.
        
        Args:
            query: The query text
            chunk_content: The content of a retrieved chunk
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        pass
```

#### Input Validation
- Query must not be empty
- Expected sources list must not be empty for validation
- Top-k must be greater than 0

#### Output Schema
```json
{
  "validation_result": {
    "id": "validation-result-id",
    "query_id": "query-identifier",
    "retrieved_chunks": ["chunk-1", "chunk-2"],
    "expected_chunks": ["chunk-1", "chunk-3"],
    "accuracy_score": 0.8,
    "relevant_count": 4,
    "total_retrieved": 5,
    "validation_passed": true,
    "notes": "Additional validation notes",
    "validated_at": "2025-12-25T10:00:00Z"
  }
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
- `ConnectionError`: Issues with connecting to Qdrant
- `RetrievalError`: Issues with performing the search
- `ValidationError`: Issues with validating results
- `ConfigurationError`: Issues with configuration parameters