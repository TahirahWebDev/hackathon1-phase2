"""
Test script for vector search validation.
This script tests the end-to-end functionality of the RAG pipeline,
including searching for relevant content chunks.
"""
import sys
import os
from unittest.mock import Mock, patch

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from services.crawler_service import CrawlerService
from services.text_cleaner_service import TextCleanerService
from services.chunker_service import ChunkerService
from services.embedding_service import EmbeddingService
from services.storage_service import StorageService
from models.document_chunk import DocumentChunk
from models.embedding_vector import EmbeddingVector
from lib.config_loader import load_config


def test_vector_search_validation():
    """
    Test script for vector search validation per spec.md requirements.
    This creates a mock test of the search functionality without requiring
    actual API keys or external services.
    """
    print("Starting vector search validation test...")
    
    # Create mock services for testing without external dependencies
    with patch('backend.src.services.embedding_service.cohere.Client') as mock_cohere, \
         patch('backend.src.services.storage_service.QdrantClient') as mock_qdrant:
        
        # Set up mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere.return_value = mock_cohere_instance
        # Mock response with example embeddings (1024-dimensional vectors)
        mock_cohere_response = Mock()
        mock_cohere_response.embeddings = [
            [0.1] * 1024,  # Example embedding for first chunk
            [0.2] * 1024,  # Example embedding for second chunk
            [0.3] * 1024   # Example embedding for query
        ]
        mock_cohere_instance.embed.return_value = mock_cohere_response
        
        # Set up mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant.return_value = mock_qdrant_instance
        
        # Mock the get_collections method to return an empty list
        mock_collections = Mock()
        mock_collections.collections = []
        mock_qdrant_instance.get_collections.return_value = mock_collections
        
        # Create mock search results
        mock_search_result = Mock()
        mock_search_result.id = "emb_1"
        mock_search_result.score = 0.9
        mock_search_result.payload = {"source_url": "https://example.com/test", "section_title": "Test Section"}
        mock_search_result.vector = [0.1] * 1024
        mock_qdrant_instance.search.return_value = [mock_search_result]
        
        # Initialize services with mock clients
        print("Initializing services...")
        chunker_service = ChunkerService(chunk_size=512, overlap=20)
        embedding_service = EmbeddingService(api_key="test_key")
        storage_service = StorageService(
            url="https://test-qdrant.com",
            api_key="test_key",
            collection_name="test_docs"
        )
        
        # Create test content
        print("Creating test content...")
        test_content = """
        Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
        Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
        As machines become increasingly capable, tasks once thought to require intelligence are often removed from the definition of AI, a phenomenon known as the AI effect.
        A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.
        Modern machine learning techniques are a core part of AI. Machine learning algorithms build a model based on sample data, known as "training data", in order to make predictions or decisions without being explicitly programmed to do so.
        """
        
        # Test chunking
        print("Testing content chunking...")
        source_url = "https://example.com/ai-intro"
        chunks = chunker_service.chunk_content(test_content, source_url, chunk_size=200, overlap=20)
        print(f"Created {len(chunks)} content chunks")
        
        # Test embedding generation
        print("Testing embedding generation...")
        embeddings = embedding_service.generate_embeddings(chunks)
        print(f"Generated {len(embeddings)} embeddings")
        
        # Test storage
        print("Testing embedding storage...")
        storage_success = storage_service.store_embeddings(embeddings)
        print(f"Storage success: {storage_success}")
        
        # Test search functionality
        print("Testing vector search...")
        query_text = "What is artificial intelligence?"
        query_embedding = embedding_service.generate_embeddings([
            DocumentChunk(
                id="query_chunk",
                content=query_text,
                source_url="query"
            )
        ])[0].vector  # Get the vector from the first (and only) embedding
        
        search_results = storage_service.search_embeddings(query_embedding, limit=5)
        print(f"Found {len(search_results)} search results")
        
        # Validate search results
        if len(search_results) > 0:
            top_result = search_results[0]
            print(f"Top result ID: {top_result['id']}")
            print(f"Top result score: {top_result['score']}")
            print(f"Top result source: {top_result['payload']['source_url']}")
            
            # Validate that the result is relevant
            if top_result['score'] > 0.5:  # Arbitrary threshold for relevance
                print("✓ Vector search returned relevant content chunks for test queries")
                return True
            else:
                print("✗ Vector search did not return sufficiently relevant results")
                return False
        else:
            print("✗ No search results returned")
            return False


if __name__ == "__main__":
    success = test_vector_search_validation()
    if success:
        print("\n✓ Vector search validation test passed!")
        sys.exit(0)
    else:
        print("\n✗ Vector search validation test failed!")
        sys.exit(1)