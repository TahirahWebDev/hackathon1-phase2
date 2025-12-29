"""
Service for storing embeddings in Qdrant vector database.
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.src.models.embedding_vector import EmbeddingVector
from backend.src.models.document_chunk import DocumentChunk
from backend.src.lib.exceptions import StorageError


class StorageService:
    """
    Service class for storing embeddings in Qdrant vector database.
    """

    def __init__(self, url: str, api_key: str, collection_name: str = "documents", timeout: int = 60):
        """
        Initialize the storage service.

        Args:
            url: Qdrant cluster URL
            api_key: Qdrant API key
            collection_name: Name of the collection to store embeddings in (default: "documents")
            timeout: Request timeout in seconds (default: 60)
        """
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=False,  # Using HTTP for compatibility
            timeout=timeout
        )
        self.collection_name = collection_name

        # Ensure the collection exists
        self._ensure_collection()
    
    def _ensure_collection(self):
        """
        Ensure that the collection exists in Qdrant.
        If it doesn't exist, create it with appropriate configuration.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name not in collection_names:
                # Create the collection
                # For Cohere embeddings, the default dimension is 1024 for multilingual model
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
                )
            else:
                # If the collection exists, clear it to avoid duplicate entries
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[]
                        )
                    )
                )
        except Exception as e:
            raise StorageError(f"Error ensuring collection exists: {str(e)}")

    def store_embeddings(self, embeddings: List[EmbeddingVector], batch_size: int = 50) -> bool:
        """
        Stores embeddings in the vector database.

        Args:
            embeddings: List of EmbeddingVector objects to store
            batch_size: Number of embeddings to store in each batch (default: 50)

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Process embeddings in batches to avoid timeout issues
            for i in range(0, len(embeddings), batch_size):
                batch = embeddings[i:i + batch_size]

                # Prepare points for insertion
                points = []
                for emb in batch:
                    # Get the content from the metadata or elsewhere if available
                    content = emb.metadata.get("content", "")
                    source_url = emb.metadata.get("source_url", "")
                    section_title = emb.metadata.get("section_title", "")

                    point = models.PointStruct(
                        id=emb.id,
                        vector=emb.vector,
                        payload={
                            "content": content,
                            "source_url": source_url,
                            "title": section_title,
                            "document_chunk_id": emb.document_chunk_id,
                            "created_at": emb.created_at.isoformat() if emb.created_at else None
                        }
                    )
                    points.append(point)

                # Upload points to Qdrant
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                print(f"Stored batch {i//batch_size + 1}/{(len(embeddings) - 1)//batch_size + 1}")

            return True

        except Exception as e:
            raise StorageError(f"Error storing embeddings: {str(e)}")

    def search_embeddings(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the vector database.

        Args:
            query_vector: The vector to search for similar embeddings
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of dictionaries containing search results
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "vector": result.vector
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            raise StorageError(f"Error searching embeddings: {str(e)}")