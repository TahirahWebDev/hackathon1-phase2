"""
Service for connecting to Qdrant vector database.
"""
import logging
from typing import Dict, Any
from qdrant_client import QdrantClient
from backend.src.models.qdrant_connection import QdrantConnection
from backend.src.lib.exceptions import ConnectionError


class QdrantConnectionService:
    """
    Service class for connecting to the Qdrant vector database.
    """

    def __init__(self):
        """
        Initialize the Qdrant connection service.
        """
        self.client = None
        self.connection = None
        self.logger = logging.getLogger(__name__)

    def connect(self, url: str, api_key: str, collection_name: str) -> bool:
        """
        Establishes a connection to the Qdrant vector database.

        Args:
            url: Qdrant cluster URL
            api_key: Qdrant API key
            collection_name: Name of the collection to connect to

        Returns:
            True if connection is successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        self.logger.info(f"Attempting to connect to Qdrant at {url} with collection '{collection_name}'")

        try:
            # Create the Qdrant client
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                prefer_grpc=False  # Using HTTP for compatibility
            )

            # Test the connection by getting collections
            self.logger.debug("Testing connection by retrieving collections")
            collections = self.client.get_collections()

            # Check if the specified collection exists
            collection_names = [collection.name for collection in collections.collections]
            self.logger.debug(f"Available collections: {collection_names}")

            if collection_name not in collection_names:
                self.logger.error(f"Collection '{collection_name}' does not exist in Qdrant")
                raise ConnectionError(f"Collection '{collection_name}' does not exist in Qdrant")

            # Create a QdrantConnection entity to track the connection
            from datetime import datetime
            self.connection = QdrantConnection(
                id=f"conn_{hash(url)}",
                url=url,
                api_key=api_key,
                collection_name=collection_name,
                created_at=datetime.now(),
                connected_at=datetime.now(),
                status="connected"
            )

            self.logger.info(f"Successfully connected to Qdrant collection '{collection_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant: {str(e)}", exc_info=True)
            raise ConnectionError(f"Failed to connect to Qdrant: {str(e)}")

    def is_connected(self) -> bool:
        """
        Checks if the service is currently connected to Qdrant.

        Returns:
            True if connected, False otherwise
        """
        if self.client is None:
            self.logger.debug("No Qdrant client available, not connected")
            return False

        try:
            # Test the connection by performing a simple operation
            self.logger.debug("Testing Qdrant connection with get_collections")
            self.client.get_collections()
            self.logger.debug("Qdrant connection test successful")
            return True
        except Exception as e:
            self.logger.warning(f"Qdrant connection test failed: {str(e)}")
            return False

    def get_client(self):
        """
        Returns the Qdrant client if connected.

        Returns:
            QdrantClient instance if connected, None otherwise
        """
        if self.is_connected():
            self.logger.debug("Returning Qdrant client")
            return self.client
        else:
            self.logger.debug("Qdrant client not available, not connected")
            return None

    def test_connection(self) -> bool:
        """
        Tests the connection to Qdrant.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Test the connection by performing a simple operation
            collections = self.client.get_collections()
            self.logger.info(f"Connection test successful. Available collections: {[c.name for c in collections.collections]}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False