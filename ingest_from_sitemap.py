#!/usr/bin/env python3
"""
Script to ingest content from sitemap into Qdrant for the RAG Chatbot Agent.
"""
import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import time
import logging
import re
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get configuration from environment
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not all([qdrant_url, qdrant_api_key, cohere_api_key]):
    print("Error: QDRANT_URL, QDRANT_API_KEY, and COHERE_API_KEY must be set in your .env file")
    exit(1)

def fetch_sitemap(sitemap_url: str) -> List[str]:
    """Fetch URLs from a sitemap.xml file."""
    logger.info(f"Fetching sitemap from {sitemap_url}")
    response = requests.get(sitemap_url)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    
    # Handle both regular sitemap and sitemap index formats
    urls = []
    for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        urls.append(url_elem.text.strip())
    
    # Also handle sitemap index files (if they contain other sitemaps)
    for sitemap_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        nested_sitemap_url = sitemap_elem.text.strip()
        logger.info(f"Found nested sitemap: {nested_sitemap_url}")
        urls.extend(fetch_sitemap(nested_sitemap_url))
    
    logger.info(f"Found {len(urls)} URLs in sitemap")
    return urls

def extract_content_from_page(url: str) -> Dict[str, Any]:
    """Extract main content from a webpage."""
    logger.info(f"Extracting content from {url}")

    try:
        response = requests.get(url, timeout=10)  # 10-second timeout
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove navigation, footers, and other non-content elements
        for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()

        # Try to find main content area - common selectors for main content
        main_content = (soup.find('main') or
                       soup.find('article') or
                       soup.find('div', class_=re.compile(r'content|main|article', re.I)) or
                       soup.find('div', id=re.compile(r'content|main|article', re.I)) or
                       soup)

        # Extract headings and text content
        headings = []
        for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append(heading.get_text().strip())

        # Extract code blocks
        code_blocks = []
        for code in main_content.find_all(['code', 'pre']):
            code_text = code.get_text().strip()
            if code_text:
                code_blocks.append(code_text)

        # Get the main text content, excluding code blocks
        # Remove code blocks temporarily to avoid duplication
        for code in main_content.find_all(['code', 'pre']):
            code.decompose()

        text_content = main_content.get_text(separator=' ', strip=True)

        # Log successful extraction
        logger.info(f"Successfully extracted {len(text_content)} characters from {url}")

        # Get page title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else urlparse(url).path.split('/')[-1] or 'Untitled'

        return {
            'url': url,
            'title': title_text,
            'content': text_content,
            'headings': headings,
            'code_blocks': code_blocks
        }
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return {
            'url': url,
            'title': 'Error',
            'content': '',
            'headings': [],
            'code_blocks': []
        }

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)

        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)

        # Move start by chunk_size - overlap to achieve overlap
        # Ensure we don't get stuck in an infinite loop
        if chunk_size > overlap:
            start += chunk_size - overlap
        else:
            start = end  # If overlap >= chunk_size, just move to end to avoid infinite loop

    return chunks

def create_qdrant_collection(client: QdrantClient, collection_name: str):
    """Create or recreate the Qdrant collection."""
    # Delete collection if it exists
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection: {collection_name}")
    except Exception as e:
        logger.info(f"Collection {collection_name} doesn't exist yet, creating new one")
    
    # Create new collection with appropriate vector size (Cohere embeddings are 1024-dim for embed-english-v3.0)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )
    logger.info(f"Created new collection: {collection_name}")

def store_chunks_in_qdrant(chunks: List[Dict], collection_name: str, qdrant_client: QdrantClient):
    """Store chunks in Qdrant with embeddings."""
    logger.info(f"Storing {len(chunks)} chunks in Qdrant collection: {collection_name}")

    # Initialize Cohere client
    co = cohere.Client(cohere_api_key)

    # Process in batches to avoid API limits
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

        # Extract text content for embedding
        texts = [chunk['content'] for chunk in batch]

        try:
            # Generate embeddings
            response = co.embed(
                texts=texts,
                model="embed-english-v3.0",
                input_type="search_document"
            )
            embeddings = response.embeddings

            # Prepare points for Qdrant
            points = []
            for idx, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                point = models.PointStruct(
                    id=i + idx,  # Unique ID for each chunk
                    vector=embedding,
                    payload={
                        "content": chunk['content'],
                        "source_url": chunk['source_url'],
                        "title": chunk['title']
                    }
                )
                points.append(point)

            # Upload batch to Qdrant
            qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(f"Uploaded batch of {len(points)} points to Qdrant")

        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            # Continue with next batch even if this one fails

def main():
    sitemap_url = "https://physical-ai-humanoid-robotics-epnr.vercel.app/sitemap.xml"
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    
    logger.info("Starting sitemap-based content ingestion...")
    
    # Initialize Qdrant client
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        prefer_grpc=False
    )
    
    # Create or recreate the collection
    create_qdrant_collection(client, collection_name)
    
    # Fetch URLs from sitemap
    urls = fetch_sitemap(sitemap_url)
    
    # Extract content from each URL
    all_chunks = []
    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
        
        content_data = extract_content_from_page(url)
        
        if content_data['content']:
            # Create chunks from the content
            content_chunks = chunk_text(content_data['content'], chunk_size=500, overlap=50)
            
            # Add metadata to each chunk
            for chunk_content in content_chunks:
                chunk = {
                    'content': chunk_content,
                    'source_url': content_data['url'],
                    'title': content_data['title']
                }
                all_chunks.append(chunk)
        
        # Add a small delay to be respectful to the server and avoid rate limiting
        time.sleep(1)
    
    logger.info(f"Extracted {len(all_chunks)} total chunks from {len(urls)} URLs")
    
    # Store chunks in Qdrant
    if all_chunks:
        store_chunks_in_qdrant(all_chunks, collection_name, client)
        logger.info("Content ingestion completed successfully!")
    else:
        logger.warning("No content was extracted from the URLs")

if __name__ == "__main__":
    main()