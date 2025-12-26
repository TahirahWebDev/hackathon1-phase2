"""
Model for conversation context to maintain state across multiple exchanges.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from backend.src.lib.base_entity import BaseEntity
from .chat_message import ChatMessage


@dataclass
class ConversationContext(BaseEntity):
    """
    Information about the ongoing conversation that helps the agent maintain context across multiple exchanges.
    """
    session_id: str = ""
    created_at: datetime = None
    last_activity_at: datetime = None
    message_history: List[ChatMessage] = field(default_factory=list)
    metadata: Optional[dict] = field(default_factory=dict)
    active: bool = True

    def __post_init__(self):
        """Initialize any additional attributes after construction and perform validation."""
        super().__post_init__()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity_at is None:
            self.last_activity_at = datetime.now()
        if self.message_history is None:
            self.message_history = []
        if self.metadata is None:
            self.metadata = {}

        # Validation
        if not self.session_id:
            raise ValueError("Session ID must be provided")

        # Check message history size to prevent memory issues
        if len(self.message_history) > 50:
            raise ValueError("Message history should not exceed 50 messages to prevent memory issues")