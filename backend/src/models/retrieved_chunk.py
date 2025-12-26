"""
Model for a retrieved chunk returned by the system as relevant to a query.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from backend.src.lib.base_entity import BaseEntity


@dataclass
class RetrievedChunk(BaseEntity):
    """
    Represents a text segment returned by the system as relevant to the query, containing the actual content and metadata.
    """
    content: str = ""
    source_url: str = ""
    title: str = ""
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    retrieved_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction and perform validation."""
        super().__post_init__()
        if self.metadata is None:
            self.metadata = {}
        if self.retrieved_at is None:
            from datetime import datetime
            self.retrieved_at = datetime.now()

        # Validation
        if not self.content.strip():
            raise ValueError("Content must not be empty")