# Quickstart: RAG Chatbot Agent

## Overview
This guide will help you set up and run the RAG Chatbot Agent to interact with the Physical AI & Humanoid Robotics book content.

## Prerequisites
- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)
- Google Gemini API key
- Qdrant Cloud account with API key and the book content already ingested
- Cohere API key (for embeddings)

## Setup

### 1. Clone the Repository (if needed)
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=your_collection_name_here  # Collection with book content
COHERE_API_KEY=your_cohere_api_key_here
```

You can copy the example file to get started:
```bash
cp .env.example .env
```

## Usage

### Start the Chatbot Server
To start the FastAPI server with the chat endpoint:

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

### Send a Chat Request
Once the server is running, you can interact with the chatbot using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are the key challenges in humanoid robotics?",
       "session_id": "test-session-123"
     }'
```

Or using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "What are the main approaches to locomotion in humanoid robots?",
        "session_id": "test-session-456"
    }
)

print(response.json()["response"])
```

### Command Options
The main application accepts the following command-line options:
- `--host`: Host address to bind to (default: "127.0.0.1")
- `--port`: Port to run the server on (default: 8000)
- `--reload`: Enable auto-reload on code changes (development only)

## Example Workflow
Here's a complete example of interacting with the RAG Chatbot:

```bash
# 1. Start the server
python main.py --port 8000

# 2. In another terminal, send a query about the book content
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Explain the concept of physical AI as described in the book"
     }'

# 3. The system will:
#    - Receive your query
#    - Use the Google Gemini agent with retrieval tool access
#    - Search the Qdrant vector database for relevant content
#    - Generate a response based only on the retrieved context
#    - Return the response with source information

# 4. Example response:
{
  "response": "According to the book, physical AI refers to the integration of artificial intelligence with physical systems...",
  "session_id": "session_abc123",
  "sources": [
    {
      "title": "Chapter 3: Foundations of Physical AI",
      "url": "https://book-url.com/chapter3",
      "confidence": 0.92
    }
  ],
  "timestamp": "2025-12-25T10:00:00Z"
}
```

## Testing
Run the tests to ensure everything is working correctly:

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=backend.src
```

## Troubleshooting
- If you get "I don't have that information in the book content" for all queries, verify that your Qdrant collection contains the book content
- If you get API key errors, verify your environment variables are set correctly
- If the server won't start, check that the required ports are available
- For timeout issues, check your network connection to Google Gemini API and Qdrant