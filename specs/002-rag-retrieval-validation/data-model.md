# Data Model: RAG Retrieval Validation

## Overview
This document defines the key data entities for the RAG retrieval validation system, based on the feature specification requirements.

## Entity: Retrieval Query
**Description**: A text query submitted to the system for semantic search in the vector database.

**Attributes**:
- `id` (string): Unique identifier for the query
- `text` (string): The actual query text
- `created_at` (datetime): Timestamp when the query was created
- `expected_results` (list): Optional list of expected result identifiers for validation

**Relationships**:
- Associated with multiple `Retrieved Chunk` entities as results
- Belongs to a specific validation test case

## Entity: Retrieved Chunk
**Description**: A text segment returned by the system as relevant to the query, containing the actual content and metadata.

**Attributes**:
- `id` (string): Unique identifier for the chunk
- `content` (string): The actual text content of the chunk
- `source_url` (string): URL of the original document
- `title` (string): Title of the original document
- `score` (float): Similarity score from the vector search
- `metadata` (dict): Additional metadata associated with the chunk
- `retrieved_at` (datetime): Timestamp when the chunk was retrieved

**Relationships**:
- Associated with one `Retrieval Query` that generated it
- Belongs to a specific validation result

## Entity: Validation Result
**Description**: The outcome of comparing retrieved content against expected results, indicating relevance and accuracy.

**Attributes**:
- `id` (string): Unique identifier for the validation result
- `query_id` (string): Reference to the original query
- `retrieved_chunks` (list): List of retrieved chunks
- `expected_chunks` (list): List of expected chunks for comparison
- `accuracy_score` (float): Calculated accuracy score (0.0 to 1.0)
- `relevant_count` (int): Number of relevant chunks retrieved
- `total_retrieved` (int): Total number of chunks retrieved
- `validation_passed` (bool): Whether the validation passed
- `notes` (string): Additional notes about the validation
- `validated_at` (datetime): Timestamp when validation was performed

**Relationships**:
- Associated with one `Retrieval Query`
- Contains multiple `Retrieved Chunk` entities

## Entity: Qdrant Connection
**Description**: Configuration and state for connecting to the Qdrant vector database.

**Attributes**:
- `id` (string): Unique identifier for the connection configuration
- `url` (string): Qdrant cluster URL
- `api_key` (string): Qdrant API key
- `collection_name` (string): Name of the collection to query
- `connected_at` (datetime): Timestamp when connection was established
- `status` (string): Current connection status (connected, failed, etc.)

**Relationships**:
- Used by multiple `Retrieval Query` operations

## Validation Rules

### Retrieval Query Validation
- Text must not be empty
- Expected results must reference valid chunk IDs if provided
- ID must be unique

### Retrieved Chunk Validation
- Content must not be empty
- Score must be between 0 and 1
- Source URL must be a valid URL format
- ID must be unique

### Validation Result Validation
- Accuracy score must be between 0 and 1
- Relevant count must not exceed total retrieved
- Query ID must reference an existing query
- ID must be unique

### Qdrant Connection Validation
- URL must be a valid URL format
- API key must not be empty
- Collection name must not be empty
- ID must be unique