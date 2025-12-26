"""
Base entity model for the RAG Content Ingestion Pipeline.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class BaseEntity:
    """
    Base entity class for all entities in the system.
    """
    id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        if self.metadata is None:
            self.metadata = {}