"""
Unit tests for input validation and sanitization.
"""

import pytest
from core.validators import InputValidator, validate_input, validate_agent_name
from core.exceptions import InputValidationError
from core.constants import MAX_INPUT_LENGTH, MAX_CONTEXT_SIZE


class TestInputValidator:
    """Test suite for InputValidator class."""

    @pytest.fixture
    def validator(self):
        """Create an InputValidator instance."""
        return InputValidator()

    def test_valid_input(self, validator):
        """Test validation of valid input."""
        result = validator.validate_and_sanitize("Hello, world!")
        assert result == "Hello, world!"

    def test_none_input(self, validator):
        """Test that None input raises error."""
        with pytest.raises(InputValidationError, match="cannot be None"):
            validator.validate_and_sanitize(None)

    def test_non_string_input(self, validator):
        """Test that non-string input raises error."""
        with pytest.raises(InputValidationError, match="must be string"):
            validator.validate_and_sanitize(123)

    def test_empty_input(self, validator):
        """Test that empty input raises error."""
        with pytest.raises(InputValidationError, match="too short"):
            validator.validate_and_sanitize("")

        with pytest.raises(InputValidationError, match="too short"):
            validator.validate_and_sanitize("   ")  # Only whitespace

    def test_too_long_input(self, validator):
        """Test that excessively long input raises error."""
        long_string = "a" * (MAX_INPUT_LENGTH + 1)
        with pytest.raises(InputValidationError, match="too long"):
            validator.validate_and_sanitize(long_string)

    def test_max_length_input(self, validator):
        """Test input at maximum length is accepted."""
        max_string = "a" * MAX_INPUT_LENGTH
        result = validator.validate_and_sanitize(max_string)
        assert result == max_string

    def test_dangerous_script_tag(self, validator):
        """Test that script tags are rejected."""
        with pytest.raises(InputValidationError, match="dangerous content"):
            validator.validate_and_sanitize("<script>alert('xss')</script>")

    def test_dangerous_javascript_protocol(self, validator):
        """Test that javascript: protocol is rejected."""
        with pytest.raises(InputValidationError, match="dangerous content"):
            validator.validate_and_sanitize("javascript:alert(1)")

    def test_dangerous_event_handler(self, validator):
        """Test that event handlers are rejected."""
        with pytest.raises(InputValidationError, match="dangerous content"):
            validator.validate_and_sanitize('<div onclick="malicious()"></div>')

    def test_dangerous_iframe(self, validator):
        """Test that iframe tags are rejected."""
        with pytest.raises(InputValidationError, match="dangerous content"):
            validator.validate_and_sanitize('<iframe src="evil.com"></iframe>')

    def test_context_validation(self, validator):
        """Test context size validation."""
        large_context = "c" * (MAX_CONTEXT_SIZE + 1)
        with pytest.raises(InputValidationError, match="Context too large"):
            validator.validate_and_sanitize("valid input", context=large_context)

    def test_whitespace_stripping(self, validator):
        """Test that leading/trailing whitespace is stripped."""
        result = validator.validate_and_sanitize("  hello  ")
        assert result == "hello"

    def test_sql_safe_validation(self, validator):
        """Test SQL injection pattern detection."""
        # Valid SQL-safe strings
        assert validator.validate_sql_safe("normal text") == "normal text"
        assert validator.validate_sql_safe("user@email.com") == "user@email.com"

        # SQL injection attempts
        with pytest.raises(InputValidationError, match="SQL injection"):
            validator.validate_sql_safe("'; DROP TABLE users--")

        with pytest.raises(InputValidationError, match="SQL injection"):
            validator.validate_sql_safe("1 UNION SELECT password FROM users")

        with pytest.raises(InputValidationError, match="SQL injection"):
            validator.validate_sql_safe("1; DELETE FROM users")

    def test_filename_validation(self, validator):
        """Test filename validation."""
        # Valid filenames
        assert validator.validate_filename("document.pdf") == "document.pdf"
        assert validator.validate_filename("my-file_v2.txt") == "my-file_v2.txt"

        # Invalid filenames
        with pytest.raises(InputValidationError, match="path traversal"):
            validator.validate_filename("../../../etc/passwd")

        with pytest.raises(InputValidationError, match="path traversal"):
            validator.validate_filename("subdir/file.txt")

        with pytest.raises(InputValidationError, match="null bytes"):
            validator.validate_filename("file\x00.txt")

        with pytest.raises(InputValidationError, match="too long"):
            validator.validate_filename("a" * 256 + ".txt")

        with pytest.raises(InputValidationError, match="invalid characters"):
            validator.validate_filename("file with spaces.txt")

    def test_agent_name_validation(self, validator):
        """Test agent name validation."""
        # Valid agent names
        assert validator.validate_agent_name("Alpha") == "Alpha"
        assert validator.validate_agent_name("Beta") == "Beta"
        assert validator.validate_agent_name("Gamma") == "Gamma"
        assert validator.validate_agent_name("Delta") == "Delta"
        assert validator.validate_agent_name("Epsilon") == "Epsilon"
        assert validator.validate_agent_name("Zeta") == "Zeta"
        assert validator.validate_agent_name("Eta") == "Eta"

        # Invalid agent names
        with pytest.raises(InputValidationError, match="Invalid agent name"):
            validator.validate_agent_name("InvalidAgent")

        with pytest.raises(InputValidationError, match="Invalid agent name"):
            validator.validate_agent_name("alpha")  # Wrong case

    def test_context_validation_dict(self, validator):
        """Test context dictionary validation."""
        # Valid context
        valid_context = {"key": "value", "num": 123}
        result = validator.validate_context(valid_context)
        assert result == valid_context

        # None context is allowed
        assert validator.validate_context(None) is None

        # Non-dict context raises error
        with pytest.raises(InputValidationError, match="must be dict"):
            validator.validate_context("not a dict")

        # Non-serializable context
        class NonSerializable:
            pass

        with pytest.raises(InputValidationError, match="not JSON serializable"):
            validator.validate_context({"obj": NonSerializable()})

        # Too large context
        large_context = {"data": "x" * MAX_CONTEXT_SIZE}
        with pytest.raises(InputValidationError, match="too large"):
            validator.validate_context(large_context)

    def test_sanitize_for_display(self, validator):
        """Test HTML escaping for display."""
        # HTML characters should be escaped
        result = validator.sanitize_for_display("<script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result

        # Special characters
        result = validator.sanitize_for_display("Text with <>&\"'")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result

        # Non-string input
        result = validator.sanitize_for_display(123)
        assert result == "123"

    def test_custom_max_length(self):
        """Test validator with custom max length."""
        validator = InputValidator(max_length=50)

        # Should accept up to 50 chars
        short_text = "a" * 50
        assert validator.validate_and_sanitize(short_text) == short_text

        # Should reject 51 chars
        long_text = "a" * 51
        with pytest.raises(InputValidationError, match="too long"):
            validator.validate_and_sanitize(long_text)


class TestConvenienceFunctions:
    """Test convenience functions for validation."""

    def test_validate_input_function(self):
        """Test the validate_input convenience function."""
        result = validate_input("Hello, world!")
        assert result == "Hello, world!"

        with pytest.raises(InputValidationError):
            validate_input("")

    def test_validate_agent_name_function(self):
        """Test the validate_agent_name convenience function."""
        assert validate_agent_name("Alpha") == "Alpha"

        with pytest.raises(InputValidationError):
            validate_agent_name("InvalidAgent")


@pytest.mark.parametrize("dangerous_input,pattern_name", [
    ("<script>alert(1)</script>", "script tag"),
    ("javascript:void(0)", "javascript protocol"),
    ('<img onerror="alert(1)">', "event handler"),
    ('<iframe src="evil"></iframe>', "iframe"),
    ('<embed src="evil">', "embed"),
    ('<object data="evil"></object>', "object tag"),
])
def test_dangerous_patterns(dangerous_input, pattern_name):
    """Parametrized test for various dangerous patterns."""
    validator = InputValidator()
    with pytest.raises(InputValidationError, match="dangerous content"):
        validator.validate_and_sanitize(dangerous_input)


@pytest.mark.parametrize("sql_injection,pattern_name", [
    ("'; DROP TABLE users--", "drop table"),
    ("1 UNION SELECT * FROM passwords", "union select"),
    ("1; DELETE FROM users", "delete from"),
    ("' OR '1'='1", "sql comment"),
])
def test_sql_injection_patterns(sql_injection, pattern_name):
    """Parametrized test for SQL injection patterns."""
    validator = InputValidator()
    with pytest.raises(InputValidationError, match="SQL injection"):
        validator.validate_sql_safe(sql_injection)
