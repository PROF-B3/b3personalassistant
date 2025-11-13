"""
Input validation and sanitization for B3PersonalAssistant.
Protects against malicious input, SQL injection, and excessive resource usage.
"""

import re
import html
from typing import Optional, Dict, Any
from core.exceptions import InputValidationError

# Configuration constants
MAX_INPUT_LENGTH = 10000  # 10K characters
MAX_CONTEXT_SIZE = 50000  # 50K characters for context
MIN_INPUT_LENGTH = 1
ALLOWED_INPUT_PATTERN = re.compile(r'^[\s\S]*$', re.UNICODE)  # Allow all unicode
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',  # JavaScript protocol
    r'on\w+\s*=',  # Event handlers
    r'<iframe',  # Iframes
    r'<embed',  # Embeds
    r'<object',  # Objects
]


class InputValidator:
    """
    Validates and sanitizes user input for security and safety.

    Protects against:
    - Excessive input length (DoS)
    - Script injection (XSS)
    - SQL injection patterns
    - Malformed input
    - Resource exhaustion

    Example:
        >>> validator = InputValidator()
        >>> clean_input = validator.validate_and_sanitize("Hello world!")
        >>> print(clean_input)
        "Hello world!"
    """

    def __init__(self, max_length: int = MAX_INPUT_LENGTH):
        """
        Initialize input validator.

        Args:
            max_length: Maximum allowed input length
        """
        self.max_length = max_length
        self.dangerous_patterns = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

    def validate_and_sanitize(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Validate and sanitize user input.

        Args:
            user_input: Raw user input to validate
            context: Optional context string (also validated)

        Returns:
            Sanitized user input

        Raises:
            InputValidationError: If input fails validation

        Example:
            >>> validator = InputValidator()
            >>> clean = validator.validate_and_sanitize("<script>alert('xss')</script>")
            # Raises InputValidationError
        """
        if user_input is None:
            raise InputValidationError("Input cannot be None")

        if not isinstance(user_input, str):
            raise InputValidationError(f"Input must be string, got {type(user_input)}")

        # Check minimum length
        if len(user_input.strip()) < MIN_INPUT_LENGTH:
            raise InputValidationError("Input is too short (must be at least 1 character)")

        # Check maximum length
        if len(user_input) > self.max_length:
            raise InputValidationError(
                f"Input too long ({len(user_input)} chars). Maximum is {self.max_length} characters."
            )

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.search(user_input):
                raise InputValidationError(
                    f"Input contains potentially dangerous content matching pattern: {pattern.pattern}"
                )

        # Basic sanitization (preserve most content but escape HTML)
        sanitized = user_input.strip()

        # Validate context if provided
        if context and len(context) > MAX_CONTEXT_SIZE:
            raise InputValidationError(
                f"Context too large ({len(context)} chars). Maximum is {MAX_CONTEXT_SIZE} characters."
            )

        return sanitized

    def validate_sql_safe(self, value: str) -> str:
        """
        Validate that a string is safe for SQL operations.

        Args:
            value: String to validate

        Returns:
            Validated string

        Raises:
            InputValidationError: If string contains SQL injection patterns
        """
        if not isinstance(value, str):
            raise InputValidationError(f"Value must be string, got {type(value)}")

        # Check for common SQL injection patterns
        sql_patterns = [
            r";\s*DROP\s+TABLE",
            r";\s*DELETE\s+FROM",
            r";\s*UPDATE\s+",
            r"UNION\s+SELECT",
            r"--\s*$",
            r"/\*.*\*/",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise InputValidationError(
                    f"Value contains potential SQL injection pattern: {pattern}"
                )

        return value

    def validate_filename(self, filename: str) -> str:
        """
        Validate filename for safety.

        Args:
            filename: Filename to validate

        Returns:
            Validated filename

        Raises:
            InputValidationError: If filename is unsafe
        """
        if not isinstance(filename, str):
            raise InputValidationError(f"Filename must be string, got {type(filename)}")

        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise InputValidationError("Filename contains path traversal characters")

        # Check for null bytes
        if '\x00' in filename:
            raise InputValidationError("Filename contains null bytes")

        # Check length
        if len(filename) > 255:
            raise InputValidationError("Filename too long (max 255 characters)")

        # Check for valid characters (alphanumeric, dash, underscore, dot)
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            raise InputValidationError("Filename contains invalid characters")

        return filename

    def validate_agent_name(self, agent_name: str) -> str:
        """
        Validate agent name.

        Args:
            agent_name: Agent name to validate

        Returns:
            Validated agent name

        Raises:
            InputValidationError: If agent name is invalid
        """
        valid_agents = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta']

        if agent_name not in valid_agents:
            raise InputValidationError(
                f"Invalid agent name: {agent_name}. Must be one of {valid_agents}"
            )

        return agent_name

    def validate_context(self, context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate context dictionary.

        Args:
            context: Context dictionary to validate

        Returns:
            Validated context

        Raises:
            InputValidationError: If context is invalid
        """
        if context is None:
            return None

        if not isinstance(context, dict):
            raise InputValidationError(f"Context must be dict, got {type(context)}")

        # Check context size (serialized)
        import json
        try:
            serialized = json.dumps(context)
            if len(serialized) > MAX_CONTEXT_SIZE:
                raise InputValidationError(
                    f"Context too large ({len(serialized)} chars). Maximum is {MAX_CONTEXT_SIZE}."
                )
        except (TypeError, ValueError) as e:
            raise InputValidationError(f"Context is not JSON serializable: {e}")

        return context

    def sanitize_for_display(self, text: str) -> str:
        """
        Sanitize text for safe display (HTML escape).

        Args:
            text: Text to sanitize

        Returns:
            HTML-escaped text
        """
        if not isinstance(text, str):
            return str(text)

        return html.escape(text)


# Global validator instance
_default_validator = InputValidator()


def validate_input(user_input: str, context: Optional[str] = None) -> str:
    """
    Convenience function for input validation using default validator.

    Args:
        user_input: User input to validate
        context: Optional context

    Returns:
        Validated input

    Raises:
        InputValidationError: If validation fails
    """
    return _default_validator.validate_and_sanitize(user_input, context)


def validate_agent_name(agent_name: str) -> str:
    """
    Convenience function for agent name validation.

    Args:
        agent_name: Agent name to validate

    Returns:
        Validated agent name

    Raises:
        InputValidationError: If validation fails
    """
    return _default_validator.validate_agent_name(agent_name)
