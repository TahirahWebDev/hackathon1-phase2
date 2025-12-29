"""
Model for a retrieval query submitted to the system for semantic search.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from backend.src.lib.base_entity import BaseEntity


@dataclass
class RetrievalQuery(BaseEntity):
    """
    Represents a text query submitted to the system for semantic search in the vector database.
    """
    text: str = ""
    expected_results: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        super().__post_init__()
        if self.expected_results is None:
            self.expected_results = []