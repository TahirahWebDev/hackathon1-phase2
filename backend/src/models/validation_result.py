"""
Model for a validation result comparing retrieved content against expected results.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.src.lib.base_entity import BaseEntity


@dataclass
class ValidationResult(BaseEntity):
    """
    Represents the outcome of comparing retrieved content against expected results, indicating relevance and accuracy.
    """
    query_id: str = ""
    retrieved_chunks: List[str] = None  # List of retrieved chunk IDs
    expected_chunks: List[str] = None  # List of expected chunk IDs for comparison
    accuracy_score: float = 0.0  # Calculated accuracy score (0.0 to 1.0)
    relevant_count: int = 0  # Number of relevant chunks retrieved
    total_retrieved: int = 0  # Total number of chunks retrieved
    validation_passed: bool = False  # Whether the validation passed
    notes: str = ""  # Additional notes about the validation
    validated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction."""
        super().__post_init__()
        if self.retrieved_chunks is None:
            self.retrieved_chunks = []
        if self.expected_chunks is None:
            self.expected_chunks = []
        if self.validated_at is None:
            self.validated_at = datetime.now()