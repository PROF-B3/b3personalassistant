"""
Base Agent Class for B3PersonalAssistant

This module contains the AgentBase class which provides the foundation for
all AI agents in the B3PersonalAssistant system.
"""

import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import ollama

from core.constants import (
    CONVERSATIONS_DB_PATH,
    MAX_INPUT_LENGTH,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
    CIRCUIT_BREAKER_TIMEOUT,
    DEFAULT_CONVERSATION_HISTORY_LIMIT,
)
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from core.validators import InputValidator
from core.resilience import (
    CircuitBreakerConfig,
    retry_with_backoff,
    get_circuit_breaker,
)


class AgentBase:
    """
    Base class for all AI agents in the B3PersonalAssistant system.

    This class provides the foundation for agent functionality including:
    - Ollama model integration
    - Conversation storage in SQLite
    - Inter-agent communication
    - User profile adaptation
    - Error handling and logging
    - Performance tracking

    Attributes:
        name (str): The agent's name (e.g., 'Alpha', 'Beta')
        orchestrator: Reference to the orchestrator for inter-agent communication
        user_profile (dict): User preferences and settings
        logger: Logging instance for the agent
        resource_monitor: Resource monitoring instance
        ollama_client: Ollama client for AI model interactions
        db_path (str): Path to the SQLite conversation database

    Example:
        >>> agent = AgentBase("TestAgent")
        >>> response = agent.act("Hello")
        >>> print(response)
        "TestAgent processed: Hello"
    """

    def __init__(
        self,
        name: str,
        orchestrator=None,
        user_profile: Optional[Dict] = None,
        resource_monitor=None
    ):
        """
        Initialize the base agent.

        Args:
            name: The agent's name (e.g., 'Alpha', 'Beta', 'Gamma', 'Delta')
            orchestrator: Reference to the orchestrator for inter-agent communication
            user_profile: Dictionary containing user preferences and settings
            resource_monitor: Resource monitoring instance for performance tracking

        Note:
            The agent will automatically create the conversation database if it doesn't exist.
        """
        self.name = name
        self.orchestrator = orchestrator
        self.user_profile = user_profile or {}
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.resource_monitor = resource_monitor
        self.ollama_client = ollama.Client()
        self.db_path = CONVERSATIONS_DB_PATH

        # Input validation and resilience
        self.validator = InputValidator(max_length=MAX_INPUT_LENGTH)
        self.circuit_breaker = get_circuit_breaker(
            f"ollama_{self.name.lower()}",
            CircuitBreakerConfig(
                failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                success_threshold=CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
                timeout=CIRCUIT_BREAKER_TIMEOUT,
            )
        )

        # Agent communication
        from core.agent_communication import (
            get_message_broker,
            AgentMessage,
            MessageType,
            MessagePriority,
        )
        self.message_broker = get_message_broker()
        self.message_broker.register_agent(self.name)
        self.MessageType = MessageType
        self.MessagePriority = MessagePriority
        self.AgentMessage = AgentMessage

        self._ensure_db()

    def _ensure_db(self):
        """
        Ensure the SQLite conversation database exists with proper schema.

        Creates the conversations table if it doesn't exist, with columns for:
        - id: Primary key
        - agent: Agent name
        - user_input: User's input text
        - agent_response: Agent's response
        - timestamp: ISO format timestamp
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                user_input TEXT,
                agent_response TEXT,
                timestamp TEXT
            )''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"DB init error: {e}")

    def store_conversation(self, user_input: str, agent_response: str):
        """
        Store a conversation exchange in the SQLite database.

        Args:
            user_input: The user's input text
            agent_response: The agent's response text

        Note:
            Conversations are stored with timestamps for analysis and debugging.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                '''INSERT INTO conversations (agent, user_input, agent_response, timestamp)
                   VALUES (?, ?, ?, ?)''',
                (self.name, user_input, agent_response, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error(f"DB store error: {e}")

    def save_conversation(self, role: str, message: str):
        """
        Save a conversation message (can be 'user' or 'assistant').

        Args:
            role: Either 'user' or 'assistant'
            message: The message content
        """
        self.logger.debug(f"{self.name} - {role}: {message[:100]}...")

    def get_conversation_history(self, limit: int = DEFAULT_CONVERSATION_HISTORY_LIMIT) -> List[Dict[str, str]]:
        """
        Retrieve recent conversation history from database.

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages with role and content
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                '''SELECT user_input, agent_response FROM conversations
                   WHERE agent = ? ORDER BY id DESC LIMIT ?''',
                (self.name, limit // 2)
            )
            rows = c.fetchall()
            conn.close()

            history = []
            for user_input, agent_response in reversed(rows):
                if user_input:
                    history.append({'role': 'user', 'message': user_input})
                if agent_response:
                    history.append({'role': 'assistant', 'message': agent_response})

            return history[-limit:]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            return []

    def send_message(self, to_agent: str, message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Send a message to another agent via the orchestrator.

        Args:
            to_agent: Name of the target agent
            message: Message content to send
            context: Optional context dictionary

        Returns:
            Response from the target agent, or None if communication fails
        """
        if self.orchestrator:
            try:
                return self.orchestrator.agent_communicate(
                    self.name, to_agent, message, context or {}
                )
            except Exception as e:
                self.logger.error(f"Failed to send message to {to_agent}: {e}")
                return f"[Error: Could not deliver message to {to_agent}]"
        else:
            self.logger.warning("No orchestrator for agent communication.")
            return None

    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Main agent action method - must be overridden in subclasses.

        Args:
            input_data: User input text
            context: Optional context dictionary

        Returns:
            Agent's response text

        Raises:
            NotImplementedError: If not overridden in subclass
        """
        raise NotImplementedError

    def communicate(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Agent-to-agent communication method - processes incoming messages.

        Args:
            message: Message received from another agent
            context: Optional context dictionary

        Returns:
            Response to the received message
        """
        self.logger.debug(f"{self.name} received message: {message[:100]}...")
        return f"{self.name} acknowledged: {message[:50]}..."

    def send_message_to(
        self,
        to_agent: str,
        content: str,
        message_type: Optional[str] = None,
        priority: Optional[str] = None,
        requires_response: bool = False,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Send a message to another agent.

        Args:
            to_agent: Target agent name
            content: Message content
            message_type: Type of message (request, notification, etc.)
            priority: Message priority (low, normal, high, urgent)
            requires_response: Whether a response is required
            context: Optional context dictionary

        Returns:
            True if message was sent successfully
        """
        msg_type = (
            self.MessageType.REQUEST
            if message_type is None
            else getattr(self.MessageType, message_type.upper(), self.MessageType.REQUEST)
        )
        msg_priority = (
            self.MessagePriority.NORMAL
            if priority is None
            else getattr(self.MessagePriority, priority.upper(), self.MessagePriority.NORMAL)
        )

        message = self.AgentMessage(
            message_id="",
            message_type=msg_type,
            from_agent=self.name,
            to_agent=to_agent,
            content=content,
            context=context or {},
            priority=msg_priority,
            requires_response=requires_response
        )

        success = self.message_broker.send_message(message)
        if success:
            self.logger.info(f"Sent message to {to_agent}: {content[:50]}...")
        else:
            self.logger.error(f"Failed to send message to {to_agent}")

        return success

    def broadcast_message(self, content: str, message_type: Optional[str] = None) -> bool:
        """
        Broadcast a message to all agents.

        Args:
            content: Message content
            message_type: Type of message

        Returns:
            True if broadcast was successful
        """
        return self.send_message_to("all", content, message_type=message_type or "broadcast")

    def check_messages(self) -> List:
        """
        Check for pending messages.

        Returns:
            List of pending messages
        """
        messages = []
        while True:
            msg = self.message_broker.receive_message(self.name, timeout=0)
            if msg is None:
                break
            messages.append(msg)

        if messages:
            self.logger.info(f"{self.name} has {len(messages)} pending messages")

        return messages

    def request_help_from(
        self,
        agent_name: str,
        request: str,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Request help from another agent.

        Args:
            agent_name: Agent to request help from
            request: Description of what help is needed
            context: Optional context

        Returns:
            True if request was sent
        """
        return self.send_message_to(
            to_agent=agent_name,
            content=request,
            message_type="REQUEST",
            priority="HIGH",
            requires_response=True,
            context=context
        )

    def think(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Agent's internal reasoning method - can be overridden in subclasses.

        Args:
            input_data: Input to think about
            context: Optional context dictionary

        Returns:
            Internal reasoning text
        """
        return f"{self.name} is thinking..."

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> str:
        """
        Handle errors gracefully and return user-friendly error message.

        Args:
            error: The exception that occurred
            context: Optional context dictionary

        Returns:
            User-friendly error message
        """
        self.logger.error(f"Error: {error}")
        return f"[Agent {self.name} encountered an error: {error}]"

    def adapt_to_user(self, text: str) -> str:
        """
        Modify output based on user profile preferences.

        Adapts the agent's communication style based on user preferences:
        - 'concise': Returns only the first sentence
        - 'friendly': Adds emoji
        - 'formal': Adds formal greeting
        - 'casual': Uses casual language

        Args:
            text: Original response text

        Returns:
            Adapted response text
        """
        style = self.user_profile.get('communication_style', '').lower()
        if style == 'concise':
            return text.split(". ")[0] + "."
        elif style == 'friendly':
            return text + " 😊"
        elif style == 'formal':
            return "Dear user, " + text
        elif style == 'casual':
            return text.replace("you", "ya")
        return text

    def estimate_complexity(self, prompt: str) -> str:
        """
        Simple heuristic to choose model based on prompt characteristics.

        Args:
            prompt: User input prompt

        Returns:
            'simple' or 'complex' based on prompt analysis
        """
        complexity_keywords = ["analyze", "research", "summarize", "plan", "connect"]
        if len(prompt) > 200 or any(word in prompt.lower() for word in complexity_keywords):
            return "complex"
        return "simple"

    def fallback_response(self, prompt: str) -> str:
        """
        Provide fallback response when normal processing fails.

        Args:
            prompt: Original user prompt

        Returns:
            Fallback response text
        """
        return f"[Fallback] Sorry, {self.name} could not process your request right now."

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate agent-specific system prompt for Ollama.

        Args:
            context: Optional context dictionary

        Returns:
            System prompt string for the AI model
        """
        return f"You are {self.name}, a helpful assistant."

    def check_model_availability(self, model: str) -> bool:
        """
        Check if a model is available in Ollama.

        Args:
            model: Model name to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = self.ollama_client.list()
            available_models = [m['name'] for m in models.get('models', [])]

            for available in available_models:
                if model in available or available in model:
                    return True

            self.logger.warning(f"Model {model} not found. Available: {available_models}")
            return False

        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"Failed to check model availability: {e}")
            return True

    def call_ollama_with_resilience(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Call Ollama API with retry logic, circuit breaker, and timeout.

        Args:
            model: Model name to use
            messages: List of message dictionaries
            timeout: Timeout in seconds

        Returns:
            Ollama API response

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            OllamaConnectionError: If cannot connect to Ollama
            OllamaTimeoutError: If request times out
        """
        if not self.check_model_availability(model):
            self.logger.warning(f"Model {model} may not be available, proceeding anyway")

        @self.circuit_breaker.call
        @retry_with_backoff(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            exceptions=(Exception,)
        )
        def _call():
            try:
                self.logger.debug(f"{self.name}: Calling Ollama model {model}")
                response = self.ollama_client.chat(
                    model=model,
                    messages=messages,
                    options={"timeout": timeout}
                )
                self.logger.debug(f"{self.name}: Ollama call successful")
                return response

            except ConnectionError as e:
                self.logger.error(f"{self.name}: Ollama connection error: {e}")
                raise OllamaConnectionError(f"Cannot connect to Ollama server: {e}") from e

            except TimeoutError as e:
                self.logger.error(f"{self.name}: Ollama timeout: {e}")
                raise OllamaTimeoutError(f"Ollama request timed out after {timeout}s") from e

        return _call()
