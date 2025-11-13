"""
Custom exception hierarchy for B3PersonalAssistant.
Provides specific exception types for better error handling and debugging.
"""


class B3Exception(Exception):
    """Base exception for all B3PersonalAssistant errors."""
    pass


class AgentException(B3Exception):
    """Base exception for agent-related errors."""
    pass


class InputValidationError(AgentException):
    """Raised when user input fails validation."""
    pass


class ModelNotAvailableError(AgentException):
    """Raised when required AI model is not available."""
    pass


class OllamaConnectionError(AgentException):
    """Raised when cannot connect to Ollama server."""
    pass


class OllamaTimeoutError(AgentException):
    """Raised when Ollama request times out."""
    pass


class CircuitBreakerOpenError(AgentException):
    """Raised when circuit breaker is open (too many failures)."""
    pass


class AgentCommunicationError(AgentException):
    """Raised when agent-to-agent communication fails."""
    pass


class DatabaseException(B3Exception):
    """Base exception for database-related errors."""
    pass


class ConversationStorageError(DatabaseException):
    """Raised when conversation storage fails."""
    pass


class ConfigurationException(B3Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ResourceLimitExceededError(B3Exception):
    """Raised when system resource limits are exceeded."""
    pass


class KnowledgeException(B3Exception):
    """Base exception for knowledge management errors."""
    pass


class TaskException(B3Exception):
    """Base exception for task management errors."""
    pass


class VideoProcessingException(B3Exception):
    """Base exception for video processing errors."""
    pass
