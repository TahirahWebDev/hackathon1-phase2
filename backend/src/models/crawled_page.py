"""
Model for a crawled page from a Docusaurus website.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .base_entity import BaseEntity


@dataclass
class CrawledPage(BaseEntity):
    """
    Represents a page that has been crawled from a Docusaurus website.
    """
    url: str = ""
    raw_content: str = ""
    clean_content: str = ""
    title: str = ""
    status_code: int = 0
    crawled_at: datetime = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        super().__post_init__()
        if self.crawled_at is None:
            self.crawled_at = datetime.now()