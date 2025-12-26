"""
Model for a retrieval tool response from the Qdrant vector database.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.src.lib.base_entity import BaseEntity


@dataclass
class RetrievalToolResponse(BaseEntity):
    """
    Represents the structured response from the retrieval service containing relevant book content fragments.
    """
    query: str = ""
    retrieved_chunks: List[Dict[str, Any]] = None  # List of content chunks retrieved from the vector database
    retrieval_metadata: Optional[Dict[str, Any]] = None  # Metadata about the retrieval process (timing, confidence scores, etc.)
    timestamp: datetime = None
    source_context: str = ""  # Context information about where the content came from

    def __post_init__(self):
        """Initialize any additional attributes after construction and perform validation."""
        super().__post_init__()
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.retrieved_chunks is None:
            self.retrieved_chunks = []
        if self.retrieval_metadata is None:
            self.retrieval_metadata = {}

        # Validation
        if not self.query.strip():
            raise ValueError("Query must not be empty")

        # Check that retrieved chunks contain content
        for chunk in self.retrieved_chunks:
            if not chunk.get('content', '').strip():
                raise ValueError("Retrieved chunks must contain content")