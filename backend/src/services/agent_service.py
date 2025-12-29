"""
Service for the RAG chatbot agent using the Google Gemini API.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from backend.src.models.chat_message import ChatMessage
from backend.src.models.conversation_context import ConversationContext
from backend.src.models.retrieval_tool_response import RetrievalToolResponse
from backend.src.lib.exceptions import RetrievalError, ConfigurationError
from backend.src.lib.retry_utils import retry_with_backoff


class AgentService:
    """
    Service class for the conversational agent that uses the Google Gemini API.
    The agent has access to a retrieval service as a tool for accessing book content.
    """

    def __init__(self, retrieval_service):
        """
        Initialize the agent service with a retrieval service.

        Args:
            retrieval_service: An instance of RetrievalService
        """
        self.retrieval_service = retrieval_service
        self.client = None  # Will be initialized with Gemini client
        self.conversation_contexts = {}  # Store conversation contexts by session ID
        self.logger = logging.getLogger(__name__)

    def initialize_agent(self, api_key: str = None):
        """
        Initializes the Gemini agent with the specified API key.

        Args:
            api_key: Gemini API key (optional, will use config if not provided)
        """
        # Import inside the method to avoid dependency issues if openai package is not available
        try:
            from openai import OpenAI
            from backend.src.lib.config_loader import get_config

            # Get API key from parameter or config
            if api_key is None:
                config = get_config()
                api_key = config.get("GEMINI_API_KEY")

            if not api_key:
                raise ConfigurationError("GEMINI_API_KEY is required to initialize the agent")

            # Initialize the OpenAI-compatible client with Gemini endpoint
            self.client = OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=api_key
            )

            # Create an agent with access to the retrieval tool
            # For now, we'll implement a simplified version that uses the retrieval service directly
            print("Agent initialized with retrieval tool access using Gemini API")

        except ImportError:
            # If openai package is not available, implement a mock version for testing
            print("OpenAI package not available, initializing mock agent")
            self.client = None

    def process_message(self, message: str, session_id: str = None, options: dict = None) -> Dict[str, Any]:
        """
        Processes a user message and returns the agent's response.

        Args:
            message: The user's message or question
            session_id: Session identifier for maintaining conversation context (optional)
            options: Additional options for response generation (optional)

        Returns:
            Dictionary containing the response, sources, and session information

        Raises:
            AgentError: If there's an error processing the message
        """
        self.logger.info(f"Processing message: '{message[:50]}...' with session_id: {session_id}")

        try:
            if not message.strip():
                self.logger.warning("Message is empty")
                raise ValueError("Message cannot be empty")

            # Get or create conversation context
            session_id = session_id or f"session_{hash(message)}"
            conversation_context = self._get_or_create_conversation_context(session_id)

            # Add the user's message to the conversation history
            user_message = ChatMessage(
                id=f"msg_user_{len(conversation_context.message_history)}_{hash(message)}",
                content=message,
                sender_type="user",
                timestamp=datetime.now(),
                conversation_id=session_id,
                metadata={}
            )
            conversation_context.message_history.append(user_message)

            # If we have a real OpenAI client, use it; otherwise, implement a mock version
            if self.client:
                self.logger.debug("Using real Gemini agent implementation")
                # Use the real OpenAI agent implementation
                result = self._process_with_openai_agent(message, session_id, options)
            else:
                self.logger.warning("Using mock agent implementation (client not initialized)")
                # Use a mock implementation that demonstrates the functionality
                result = self._process_with_mock_agent(message, session_id, options)

            # Add the agent's response to the conversation history
            agent_message = ChatMessage(
                id=f"msg_agent_{len(conversation_context.message_history)}_{hash(str(result['response']))}",
                content=result["response"],
                sender_type="agent",
                timestamp=datetime.now(),
                conversation_id=session_id,
                metadata={}
            )
            conversation_context.message_history.append(agent_message)

            # Update the last activity time
            conversation_context.last_activity_at = datetime.now()

            self.logger.info(f"Successfully processed message, response length: {len(result['response'])}")
            return result

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # Return a structured error response instead of raising
            return {
                "response": "An error occurred while processing your request. Please try again later.",
                "session_id": session_id or f"session_{hash(message)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _get_or_create_conversation_context(self, session_id: str) -> ConversationContext:
        """
        Gets an existing conversation context or creates a new one.

        Args:
            session_id: The session identifier

        Returns:
            ConversationContext object
        """
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(
                id=f"ctx_{session_id}",
                session_id=session_id
            )

        return self.conversation_contexts[session_id]

    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
        exceptions=(Exception,),
        logger=logging.getLogger(__name__)
    )
    def _process_with_openai_agent(self, message: str, session_id: str, options: dict) -> Dict[str, Any]:
        """
        Process message using the real Gemini API.
        """
        # Retrieve relevant content based on the query
        top_k = (options or {}).get("top_k", 5)
        retrieved_chunks = self.retrieval_service.retrieve_content(message, top_k)

        # Prepare context from retrieved content
        context_str = ""
        sources = []
        for chunk in retrieved_chunks:
            content = getattr(chunk, 'content', '')
            if content:
                context_str += f"{content}\n\n"
            sources.append({
                "title": getattr(chunk, 'title', ''),
                "url": getattr(chunk, 'source_url', ''),
                "confidence": getattr(chunk, 'score', 0.0)
            })

        # Prepare the prompt for the Gemini model
        if context_str:
            prompt = f"Based on the following book content, please answer the user's question:\n\n{context_str}\n\nUser question: {message}"
        else:
            prompt = f"Please answer the user's question: {message}"

        try:
            # Call the Gemini API to generate a response
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a standard model name that works with OpenAI-compatible endpoints
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Limit response length
                temperature=0.7  # Adjust creativity
            )

            # Extract the response from the completion
            response_text = completion.choices[0].message.content

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)

            # Fallback to mock implementation if API call fails
            response_text = self._generate_response(message, retrieved_chunks)

        return {
            "response": response_text,
            "session_id": session_id,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        }

    def _process_with_mock_agent(self, message: str, session_id: str, options: dict) -> Dict[str, Any]:
        """
        Process message using a mock agent implementation.
        """
        # In the mock version, we'll directly use the retrieval service
        top_k = (options or {}).get("top_k", 5)
        retrieved_chunks = self.retrieval_service.retrieve_content(message, top_k)

        # Generate response based on retrieved content
        response_text = self._generate_response(message, retrieved_chunks)

        # Format sources
        sources = []
        for chunk in retrieved_chunks:
            sources.append({
                "title": getattr(chunk, 'title', ''),
                "url": getattr(chunk, 'source_url', ''),
                "confidence": getattr(chunk, 'score', 0.0)
            })

        return {
            "response": response_text,
            "session_id": session_id,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_response(self, query: str, retrieved_chunks: List) -> str:
        """
        Generate a response based on the query and retrieved content.
        """
        if not retrieved_chunks:
            return "I don't have that information in the book content."

        # For now, we'll just concatenate the content of the top retrieved chunks
        # In a real implementation, this would use a more sophisticated approach
        response_parts = ["Based on the book content:"]
        for chunk in retrieved_chunks[:2]:  # Limit to top 2 chunks to keep response concise
            content = getattr(chunk, 'content', '')[:200]  # Limit content length
            response_parts.append(f"- {content}...")

        return " ".join(response_parts)