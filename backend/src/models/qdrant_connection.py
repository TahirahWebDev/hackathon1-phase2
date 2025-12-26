"""
Model for a Qdrant connection configuration.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from backend.src.lib.base_entity import BaseEntity


@dataclass
class QdrantConnection(BaseEntity):
    """
    Represents configuration and state for connecting to the Qdrant vector database.
    """
    url: str = ""
    api_key: str = ""
    collection_name: str = ""
    connected_at: Optional[datetime] = None
    status: str = "disconnected"  # Default status

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        super().__post_init__()
        if self.connected_at is None:
            self.connected_at = datetime.now()