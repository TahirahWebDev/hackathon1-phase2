"""
Service for generating embeddings using Cohere models.
"""
from typing import List
from backend.src.models.document_chunk import DocumentChunk
from backend.src.models.embedding_vector import EmbeddingVector
from backend.src.lib.exceptions import EmbeddingError


class EmbeddingService:
    """
    Service class for generating vector embeddings using Cohere models.
    """
    
    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        """
        Initialize the embedding service.
        
        Args:
            api_key: Cohere API key
            model: The embedding model to use (default: embed-english-v3.0)
        """
        self.api_key = api_key
        self.model = model
        
    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        """
        Generates embeddings for document chunks.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            List of EmbeddingVector objects with embedding vectors
            
        Raises:
            EmbeddingError: If there's an error generating embeddings
        """
        import cohere
        from datetime import datetime
        import os
        
        try:
            # Set the API key as an environment variable or use directly
            os.environ["COHERE_API_KEY"] = self.api_key
            
            # Initialize the Cohere client
            co = cohere.Client(self.api_key)
            
            # Extract text content from chunks for embedding
            texts = [chunk.content for chunk in chunks]
            
            # Generate embeddings using Cohere
            response = co.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"  # Using search_document as default input type
            )
            
            # Create EmbeddingVector objects from the response
            import uuid
            embeddings = []
            for i, embedding_vector in enumerate(response.embeddings):
                chunk = chunks[i]
                embedding = EmbeddingVector(
                    id=str(uuid.uuid4()),  # Use UUID for Qdrant compatibility
                    vector=embedding_vector,
                    document_chunk_id=chunk.id,
                    created_at=datetime.now(),
                    metadata={
                        "content": chunk.content,  # Include the actual content
                        "source_url": chunk.source_url,
                        "section_title": chunk.section_title
                    }
                )
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            raise EmbeddingError(f"Error generating embeddings: {str(e)}")