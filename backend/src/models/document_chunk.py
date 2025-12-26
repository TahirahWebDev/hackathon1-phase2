"""
Model for a document chunk that has been prepared for embedding.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .base_entity import BaseEntity


@dataclass
class DocumentChunk(BaseEntity):
    """
    Represents a segment of documentation content that has been cleaned and prepared for embedding.
    """
    content: str = ""
    source_url: str = ""
    section_title: Optional[str] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        super().__post_init__()
        if self.section_title is None:
            self.section_title = ""