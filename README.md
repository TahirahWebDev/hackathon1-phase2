# RAG Chatbot Agent

This system implements a RAG (Retrieval-Augmented Generation) chatbot agent that allows users to ask questions about book content and receive context-aware responses based on retrieved information. The system uses Google's Gemini API for natural language processing and Qdrant vector database for efficient content retrieval.

## Overview

The RAG Chatbot Agent connects to the Qdrant vector database, retrieves relevant book content based on user queries, and generates context-aware responses using the Gemini API. This system supports conversation history management, source attribution, and robust error handling.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)
- Qdrant Cloud account with API key
- Google Gemini API key
- Cohere API key (for embeddings)
- Access to the vector database with existing book content embeddings

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the project root with the following variables:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_cluster_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_COLLECTION_NAME=documents  # Optional, defaults to "documents"
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   You can copy the example file to get started:
   ```bash
   cp .env.example .env
   ```

## Usage

### Running the Server

To start the chatbot API server:

```bash
python main.py --urls "https://example.com/book1" "https://example.com/book2" --host 127.0.0.1 --port 8000
```

### API Endpoints

Once the server is running, you can interact with the chatbot using the following API endpoint:

- **POST** `/api/v1/chat`
  - Request body: `{"message": "your question here", "session_id": "optional session id", "options": {"top_k": 5}}`
  - Response: JSON with the response, sources, and session information

### Command Line Interface

The system provides a command-line interface for individual component execution:

#### Test Qdrant Connection
```bash
python -m backend.src.cli.main_cli test-qdrant
```

#### Test Retrieval Component
```bash
python -m backend.src.cli.main_cli test-retrieval --urls "https://example.com/book" --query "your question" --top-k 5
```

#### Test Agent Component
```bash
python -m backend.src.cli.main_cli test-agent --query "your question" --session-id "optional_session_id"
```

### Examples

1. **Start the server with book URLs:**
   ```bash
   python main.py --urls "https://example.com/book1" "https://example.com/book2" --host 0.0.0.0 --port 8000
   ```

2. **Test the retrieval component:**
   ```bash
   python -m backend.src.cli.main_cli test-retrieval --urls "https://en.wikipedia.org/wiki/Artificial_intelligence" --query "What is machine learning?" --top-k 3
   ```

3. **Test the agent component:**
   ```bash
   python -m backend.src.cli.main_cli test-agent --query "Explain neural networks" --session-id "session_123"
   ```

4. **Query the API:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "What is the main concept of this book?", "session_id": "session_456"}'
   ```

## Architecture

The system is organized into several layers:

- **API Layer**: FastAPI endpoints for chat interactions
- **Service Layer**: Business logic for agent and retrieval services
- **Model Layer**: Data structures for chat messages, conversation context, and retrieval results
- **Library Layer**: Configuration, logging, retry utilities, and exception handling

## Configuration

The system uses environment variables for configuration. The following variables are required:

- `COHERE_API_KEY`: API key for Cohere embeddings
- `QDRANT_URL`: URL of your Qdrant cluster
- `QDRANT_API_KEY`: API key for your Qdrant cluster
- `GEMINI_API_KEY`: API key for Google's Gemini

The following variables are optional:

- `QDRANT_COLLECTION_NAME`: Name of the collection to query (defaults to "documents")
- `TOP_K_DEFAULT`: Default number of results to retrieve (defaults to 5)
- `LOG_LEVEL`: Logging level (defaults to "INFO")

## Troubleshooting

- **Connection Issues**: Verify your Qdrant URL, API keys, and Gemini API key are correct in your `.env` file
- **No Results Returned**: Check that your collection contains embeddings and the collection name is correct
- **API Errors**: Ensure your Gemini API key has sufficient quota and access
- **Timeout Issues**: Check your network connection to Qdrant and the Gemini API

## Development

To extend the system:

1. Add new models in the `backend/src/models/` directory
2. Add new services in the `backend/src/services/` directory
3. Add new CLI commands in the `backend/src/cli/` module
4. Add tests in the respective test directories
5. Update the documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.