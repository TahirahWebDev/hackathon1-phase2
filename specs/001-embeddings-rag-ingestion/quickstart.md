# Quickstart: RAG Content Ingestion Pipeline

## Overview
This guide will help you set up and run the RAG content ingestion pipeline to crawl Docusaurus documentation websites, generate embeddings, and store them in Qdrant.

## Prerequisites
- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)
- Qdrant Cloud account with API key
- Cohere API key

## Setup

### 1. Clone the Repository
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
# Initialize project with uv (if available) or use pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=your_collection_name_here  # Optional, defaults to "documents"
```

You can copy the example file to get started:
```bash
cp .env.example .env
```

## Usage

### Run the Full Ingestion Pipeline
To run the complete pipeline end-to-end:

```bash
python main.py --urls "https://example-docusaurus-site.com" "https://another-site.com" --chunk-size 512
```

### Run Individual Components
You can also run specific components of the pipeline:

```bash
# Just crawl and save pages
python -m backend.src.cli.main_cli crawl --urls "https://example.com" --output-dir ./crawled_data

# Process crawled data into chunks
python -m backend.src.cli.main_cli chunk --input-dir ./crawled_data --output-dir ./chunked_data

# Generate embeddings from chunks
python -m backend.src.cli.main_cli embed --input-dir ./chunked_data --output-dir ./embedded_data

# Store embeddings in Qdrant
python -m backend.src.cli.main_cli store --input-dir ./embedded_data
```

### Command Options
- `--urls`: One or more URLs to crawl (required)
- `--chunk-size`: Size of text chunks (default: 512)
- `--overlap`: Overlap between chunks (default: 20)
- `--output-dir`: Directory to save results (varies by command)
- `--config`: Path to config file (default: .env)

## Example Workflow
Here's a complete example of ingesting content from a Docusaurus site:

```bash
# 1. Run the full pipeline for a documentation site
python main.py --urls "https://docusaurus-example-site.com" --chunk-size 512

# 2. The pipeline will:
#    - Crawl all public pages from the site
#    - Extract and clean text content
#    - Split content into appropriately sized chunks
#    - Generate embeddings using Cohere
#    - Store embeddings in Qdrant with metadata

# 3. Verify the results
python -m backend.src.cli.main_cli verify
```

## Additional CLI Commands
The pipeline provides additional CLI commands for specific tasks:

```bash
# Run individual pipeline components
python -m backend.src.cli.main_cli crawl --urls "https://example.com"
python -m backend.src.cli.main_cli chunk --input-dir ./data
python -m backend.src.cli.main_cli embed --input-dir ./data
python -m backend.src.cli.main_cli store --input-dir ./data

# Run verification to check pipeline setup
python -m backend.src.cli.main_cli verify
```

## Testing
Run the tests to ensure everything is working correctly:

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=backend.src
```

## Troubleshooting
- If you get API rate limit errors, consider adding delays between requests or upgrading your API plan
- If pages aren't being crawled correctly, check if they require JavaScript rendering (not currently supported)
- For Qdrant connection issues, verify your URL and API key are correct