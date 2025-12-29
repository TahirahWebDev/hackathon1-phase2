"""
Custom exception classes for the RAG Content Ingestion Pipeline.
"""


class ConnectionError(Exception):
    """Exception raised when there's an error during connection."""
    pass


class RetrievalError(Exception):
    """Exception raised when there's an error during retrieval."""
    pass


class ValidationError(Exception):
    """Exception raised when there's a validation error."""
    pass


class ConfigurationError(Exception):
    """Exception raised when there's a configuration error."""
    pass


class QdrantError(Exception):
    """Exception raised when there's an error with Qdrant operations."""
    pass


# Additional exceptions needed for compatibility with other modules
class CrawlerError(Exception):
    """Exception raised when there's an error during crawling."""
    pass


class EmbeddingError(Exception):
    """Exception raised when there's an error during embedding."""
    pass


class StorageError(Exception):
    """Exception raised when there's an error during storage operations."""
    pass


class ParsingError(Exception):
    """Exception raised when there's an error during parsing."""
    pass