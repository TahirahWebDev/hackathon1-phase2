# Quickstart: RAG Retrieval Validation

## Overview
This guide will help you set up and run the RAG retrieval validation system to test your vector database and retrieval pipeline.

## Prerequisites
- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)
- Qdrant Cloud account with API key
- Access to the vector database with existing embeddings from Spec-1

## Setup

### 1. Clone the Repository (if needed)
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=documents  # The collection with your embeddings from Spec-1
```

You can copy the example file to get started:
```bash
cp .env.example .env
```

## Usage

### Run Retrieval Validation
To run the retrieval validation with a test query:

```bash
python retrieve.py --query "your test query here" --top-k 5
```

### Run with Different Parameters
To run with different parameters:

```bash
python retrieve.py --query "What is artificial intelligence?" --top-k 10 --collection "my-documents"
```

### Command Options
- `--query`: The query text to validate against the vector database (required)
- `--top-k`: Number of top results to retrieve (default: 5)
- `--collection`: Name of the Qdrant collection to query (default: from environment)
- `--validate`: Whether to perform validation against expected results (default: true)

## Example Workflow
Here's a complete example of validating the retrieval pipeline:

```bash
# 1. Run validation for a specific query
python retrieve.py --query "How to implement RAG systems" --top-k 5

# 2. The script will:
#    - Connect to Qdrant using your credentials
#    - Load existing vector embeddings from the collection
#    - Perform similarity search for your query
#    - Return top-k most relevant text chunks
#    - Validate that retrieved content matches source URLs and metadata

# 3. Review the results and validation output
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
pytest --cov=.
```

## Troubleshooting
- If you get connection errors, verify your Qdrant URL and API key are correct
- If no results are returned, check that your collection contains embeddings
- If validation fails, verify that the embeddings in your collection match the expected content
- For timeout issues, check your network connection to Qdrant