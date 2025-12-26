# API Contracts: RAG Chatbot Agent

## Overview
This document defines the API contracts for the RAG Chatbot Agent, including request/response schemas and endpoint specifications.

## API Endpoint: Chat Endpoint

### POST /chat

**Description**: Accepts a user message and returns the agent's response based on the book content.

**Request**:
```json
{
  "message": "Your question about the book content",
  "session_id": "optional session identifier for maintaining conversation context",
  "options": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**Request Schema**:
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "The user's message or question",
      "minLength": 1,
      "maxLength": 10000
    },
    "session_id": {
      "type": "string",
      "description": "Session identifier for maintaining conversation context (optional)",
      "pattern": "^[a-zA-Z0-9-_]+$",
      "maxLength": 100
    },
    "options": {
      "type": "object",
      "properties": {
        "temperature": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "default": 0.7
        },
        "max_tokens": {
          "type": "integer",
          "minimum": 1,
          "maximum": 2000,
          "default": 500
        }
      },
      "additionalProperties": false
    }
  },
  "required": ["message"],
  "additionalProperties": false
}
```

**Response (Success)**:
```json
{
  "response": "The agent's response to the user's message",
  "session_id": "session identifier",
  "sources": [
    {
      "title": "Title of source document",
      "url": "URL of source document",
      "confidence": 0.95
    }
  ],
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Response Schema (Success)**:
```json
{
  "type": "object",
  "properties": {
    "response": {
      "type": "string",
      "description": "The agent's response to the user's query"
    },
    "session_id": {
      "type": "string",
      "description": "The session identifier"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Title of the source document"
          },
          "url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the source document"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confidence score of the source"
          }
        },
        "required": ["title", "url", "confidence"],
        "additionalProperties": false
      }
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp of the response"
    }
  },
  "required": ["response", "session_id", "sources", "timestamp"],
  "additionalProperties": false
}
```

**Response (Error)**:
```json
{
  "error": {
    "type": "string",
    "message": "Human-readable error message",
    "details": "Additional error details (optional)"
  },
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Error Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "object",
      "properties": {
        "type": "string",
        "message": "string",
        "details": {
          "type": "string"
        }
      },
      "required": ["type", "message"],
      "additionalProperties": false
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["error", "timestamp"],
  "additionalProperties": false
}
```

**HTTP Status Codes**:
- `200`: Success - Response generated successfully
- `400`: Bad Request - Invalid request format
- `422`: Unprocessable Entity - Valid format but invalid values
- `500`: Internal Server Error - Server-side error occurred

## Service Contracts

### Agent Service Contract

#### Interface: AgentService
```python
class AgentService:
    def process_message(self, message: str, session_id: str = None, options: dict = None) -> dict:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: The user's message or question
            session_id: Session identifier for maintaining conversation context (optional)
            options: Additional options for response generation (optional)
            
        Returns:
            Dictionary containing the response, sources, and session information
            
        Raises:
            AgentError: If there's an error processing the message
        """
        pass
```

#### Input Validation
- Message must not be empty
- Session ID (if provided) must match the expected format
- Options (if provided) must conform to the specified schema

#### Output Schema
```json
{
  "response": "Agent's response to the query",
  "session_id": "Session identifier",
  "sources": [
    {
      "title": "Source document title",
      "url": "https://example.com/source",
      "confidence": 0.85
    }
  ],
  "timestamp": "2025-12-25T10:00:00Z"
}
```

### Retrieval Service Contract

#### Interface: RetrievalService
```python
class RetrievalService:
    def retrieve_content(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        """
        Retrieve relevant content chunks based on the query.
        
        Args:
            query: The query to search for in the vector database
            top_k: Number of top results to return (default: 5)
            
        Returns:
            List of RetrievedChunk objects with content and metadata
            
        Raises:
            RetrievalError: If there's an error during retrieval
        """
        pass
```

#### Input Validation
- Query must not be empty
- top_k must be a positive integer

#### Output Schema
```json
[
  {
    "id": "chunk_identifier",
    "content": "Content of the retrieved chunk",
    "source_url": "https://example.com/source",
    "title": "Title of the source",
    "score": 0.85,
    "metadata": {
      "additional": "metadata values"
    }
  }
]
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
- `InvalidRequestError`: Issues with request format or values
- `AgentProcessingError`: Issues with agent processing
- `RetrievalError`: Issues with content retrieval from vector database
- `ConnectionError`: Issues connecting to external services (OpenAI, Qdrant)
- `ConfigurationError`: Issues with environment configuration