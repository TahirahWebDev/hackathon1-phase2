# Data Model: RAG Chatbot Agent

## Overview
This document defines the key data entities for the RAG Chatbot Agent, based on the feature specification requirements.

## Entity: ChatMessage
**Description**: A message exchanged between the user and the agent, containing the text content and metadata about the exchange.

**Attributes**:
- `id` (string): Unique identifier for the message
- `content` (string): The actual text content of the message
- `sender_type` (string): Type of sender ('user' or 'agent')
- `timestamp` (datetime): When the message was sent
- `conversation_id` (string): ID of the conversation this message belongs to
- `metadata` (dict): Additional metadata associated with the message

**Relationships**:
- Belongs to one `ConversationContext`
- Part of a sequence of messages in a conversation

## Entity: ConversationContext
**Description**: Information about the ongoing conversation that helps the agent maintain context across multiple exchanges.

**Attributes**:
- `id` (string): Unique identifier for the conversation
- `session_id` (string): Session identifier for the conversation
- `created_at` (datetime): When the conversation started
- `last_activity_at` (datetime): When the last message was exchanged
- `message_history` (list[ChatMessage]): List of messages in the conversation
- `metadata` (dict): Additional metadata about the conversation

**Relationships**:
- Contains multiple `ChatMessage` entities
- Associated with one or more `RetrievalToolResponse` entities

## Entity: RetrievalToolResponse
**Description**: The structured response from the retrieval service containing relevant book content fragments.

**Attributes**:
- `id` (string): Unique identifier for the retrieval response
- `query` (string): The original query that triggered the retrieval
- `retrieved_chunks` (list[dict]): List of content chunks retrieved from the vector database
- `retrieval_metadata` (dict): Metadata about the retrieval process (timing, confidence scores, etc.)
- `timestamp` (datetime): When the retrieval was performed
- `source_context` (string): Context information about where the content came from

**Relationships**:
- Generated in response to a `ChatMessage` query
- Used by the agent to form a response in a `ChatMessage`
- Associated with a `ConversationContext`

## Validation Rules

### ChatMessage Validation
- Content must not be empty or consist only of whitespace
- Sender type must be either 'user' or 'agent'
- Conversation ID must reference an existing conversation
- ID must be unique

### ConversationContext Validation
- Session ID must be unique for active conversations
- Message history should not exceed a reasonable size (e.g., 50 messages) to prevent memory issues
- ID must be unique

### RetrievalToolResponse Validation
- Query must not be empty
- Retrieved chunks must contain content
- Source context should be properly formatted
- ID must be unique

## State Transitions

### ConversationContext States
- `NEW`: A new conversation has been initiated
- `ACTIVE`: Messages are being exchanged in the conversation
- `INACTIVE`: No activity for a certain period (e.g., 30 minutes)
- `ENDED`: Conversation has been explicitly ended or timed out