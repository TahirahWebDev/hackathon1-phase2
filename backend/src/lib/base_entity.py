"""
Base entity model for the RAG Retrieval Validation system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class BaseEntity:
    """
    Base entity class for all entities in the system.
    """
    id: str = ""
    created_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        if self.created_at is None:
            from datetime import datetime
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}