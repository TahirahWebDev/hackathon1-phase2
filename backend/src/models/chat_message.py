"""
Model for a chat message exchanged between user and agent.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from backend.src.lib.base_entity import BaseEntity


@dataclass
class ChatMessage(BaseEntity):
    """
    Represents a message exchanged between the user and the agent, containing the text content and metadata about the exchange.
    """
    content: str = ""
    sender_type: str = ""  # 'user' or 'agent'
    timestamp: datetime = None
    conversation_id: str = ""
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Initialize any additional attributes after construction and perform validation."""
        super().__post_init__()
        if self.timestamp is None:
            self.timestamp = datetime.now()

        # Validation
        if not self.content.strip():
            raise ValueError("Content must not be empty or consist only of whitespace")

        if self.sender_type not in ["user", "agent"]:
            raise ValueError("sender_type must be 'user' or 'agent'")

        if not self.conversation_id:
            raise ValueError("Conversation ID must be provided")