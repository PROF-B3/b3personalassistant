"""
Property-Based Tests for B3PersonalAssistant

Uses Hypothesis to generate random test inputs and find edge cases
that traditional unit tests might miss.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, example
from hypothesis import HealthCheck
import string

from core.validators import InputValidator
from core.exceptions import InputValidationError
from core.constants import MAX_INPUT_LENGTH, MAX_CONTEXT_SIZE, MAX_FILENAME_LENGTH


# Custom strategies for common patterns
@st.composite
def valid_email(draw):
    """Generate valid email addresses."""
    local = draw(st.text(
        alphabet=string.ascii_letters + string.digits + "._-",
        min_size=1,
        max_size=64
    ).filter(lambda x: x[0] not in ".-" and x[-1] not in ".-"))

    domain = draw(st.text(
        alphabet=string.ascii_letters + string.digits + "-",
        min_size=1,
        max_size=63
    ).filter(lambda x: x[0] != "-" and x[-1] != "-"))

    tld = draw(st.sampled_from(["com", "org", "net", "edu", "io", "dev"]))

    return f"{local}@{domain}.{tld}"


@st.composite
def safe_filename(draw):
    """Generate safe filenames."""
    name = draw(st.text(
        alphabet=string.ascii_letters + string.digits + "_-",
        min_size=1,
        max_size=50
    ))
    ext = draw(st.sampled_from(["txt", "pdf", "doc", "md", "py", "json"]))
    return f"{name}.{ext}"


class TestInputValidatorProperties:
    """Property-based tests for InputValidator."""

    @given(st.text(min_size=1, max_size=MAX_INPUT_LENGTH))
    @settings(max_examples=200)
    def test_valid_length_strings_are_accepted(self, text):
        """
        Property: Any string within length limits should be accepted.

        This test generates random strings and verifies they pass validation.
        """
        # Assume no dangerous patterns (we test those separately)
        assume(not any(pattern in text.lower() for pattern in [
            "<script", "javascript:", "onclick", "<iframe", "<embed", "<object"
        ]))

        validator = InputValidator()
        result = validator.validate_and_sanitize(text)

        # Result should be a string (stripped)
        assert isinstance(result, str)
        # Length should not exceed original
        assert len(result) <= len(text)

    @given(st.text(min_size=MAX_INPUT_LENGTH + 1, max_size=MAX_INPUT_LENGTH + 1000))
    def test_too_long_strings_are_rejected(self, text):
        """Property: Strings exceeding max length should always be rejected."""
        validator = InputValidator()

        with pytest.raises(InputValidationError, match="too long"):
            validator.validate_and_sanitize(text)

    @given(st.text(max_size=0))
    def test_empty_strings_are_rejected(self, text):
        """Property: Empty strings should always be rejected."""
        validator = InputValidator()

        with pytest.raises(InputValidationError, match="too short"):
            validator.validate_and_sanitize(text)

    @given(st.text(
        alphabet=string.whitespace,
        min_size=1,
        max_size=100
    ))
    def test_whitespace_only_strings_are_rejected(self, text):
        """Property: Strings with only whitespace should be rejected."""
        validator = InputValidator()

        with pytest.raises(InputValidationError, match="too short"):
            validator.validate_and_sanitize(text)

    @given(st.text(min_size=1, max_size=100))
    def test_stripped_output_has_no_leading_trailing_whitespace(self, text):
        """Property: Validated output should never have leading/trailing whitespace."""
        # Skip dangerous patterns and very short strings
        assume(not any(pattern in text.lower() for pattern in [
            "<script", "javascript:", "onclick"
        ]))
        assume(len(text.strip()) > 0)

        validator = InputValidator()

        try:
            result = validator.validate_and_sanitize(text)
            # Should not start or end with whitespace
            assert result == result.strip()
        except InputValidationError:
            # It's okay to reject some inputs
            pass

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    @example(["<script>", "alert(1)", "</script>"])
    def test_sql_injection_patterns_are_always_rejected(self, parts):
        """Property: SQL injection patterns should always be rejected."""
        # Create SQL injection attempts
        sql_patterns = [
            "'; DROP TABLE",
            "UNION SELECT",
            "DELETE FROM",
            "'; --",
            "' OR '1'='1",
        ]

        validator = InputValidator()

        for pattern in sql_patterns:
            text = " ".join(parts) + " " + pattern

            with pytest.raises(InputValidationError, match="SQL injection"):
                validator.validate_sql_safe(text)

    @given(st.text(min_size=1, max_size=100))
    def test_xss_patterns_are_rejected(self, text):
        """Property: XSS patterns should be detected and rejected."""
        xss_patterns = [
            "<script>",
            "javascript:",
            "onclick=",
            "<iframe",
            "onerror=",
        ]

        validator = InputValidator()

        # Add XSS pattern to text
        for pattern in xss_patterns:
            dangerous_text = text + pattern + "malicious"

            with pytest.raises(InputValidationError, match="dangerous content"):
                validator.validate_and_sanitize(dangerous_text)

    @given(safe_filename())
    def test_safe_filenames_are_accepted(self, filename):
        """Property: Filenames without special characters should be accepted."""
        validator = InputValidator()

        result = validator.validate_filename(filename)
        assert result == filename
        assert "/" not in result
        assert "\\" not in result
        assert ".." not in result

    @given(st.text(min_size=1, max_size=50))
    def test_filenames_with_path_traversal_are_rejected(self, filename):
        """Property: Filenames with path traversal should be rejected."""
        validator = InputValidator()

        # Add path traversal patterns
        dangerous_patterns = ["../", "..\\", "/etc/", "C:\\"]

        for pattern in dangerous_patterns:
            dangerous_filename = pattern + filename

            with pytest.raises(InputValidationError):
                validator.validate_filename(dangerous_filename)

    @given(st.text(min_size=MAX_FILENAME_LENGTH + 1, max_size=MAX_FILENAME_LENGTH + 100))
    def test_too_long_filenames_are_rejected(self, filename):
        """Property: Filenames exceeding max length should be rejected."""
        validator = InputValidator()

        with pytest.raises(InputValidationError, match="too long"):
            validator.validate_filename(filename)

    @given(valid_email())
    @settings(max_examples=100)
    def test_valid_emails_pass_sql_safe_validation(self, email):
        """Property: Valid email addresses should pass SQL-safe validation."""
        validator = InputValidator()

        result = validator.validate_sql_safe(email)
        assert result == email
        assert "@" in result

    @given(st.dictionaries(
        keys=st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
        values=st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none()
        ),
        max_size=10
    ))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_json_serializable_contexts_are_accepted(self, context):
        """Property: JSON-serializable dictionaries should be accepted as context."""
        # Skip if context would be too large when serialized
        import json
        try:
            serialized = json.dumps(context)
            assume(len(serialized) <= MAX_CONTEXT_SIZE)
        except (TypeError, ValueError):
            # Not serializable, skip
            assume(False)

        validator = InputValidator()

        result = validator.validate_context(context)
        assert result == context

    @given(st.text(min_size=1, max_size=50))
    def test_agent_names_validation_is_strict(self, agent_name):
        """Property: Only specific agent names should be accepted."""
        validator = InputValidator()
        valid_agents = {"Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta"}

        if agent_name in valid_agents:
            result = validator.validate_agent_name(agent_name)
            assert result == agent_name
        else:
            with pytest.raises(InputValidationError, match="Invalid agent name"):
                validator.validate_agent_name(agent_name)

    @given(st.text())
    def test_sanitize_for_display_never_contains_raw_html(self, text):
        """Property: Sanitized output should never contain raw HTML tags."""
        validator = InputValidator()

        result = validator.sanitize_for_display(text)

        # Should not contain literal < or >
        if "<" in text:
            assert "&lt;" in result or "<" not in result
        if ">" in text:
            assert "&gt;" in result or ">" not in result

    @given(st.integers(min_value=1, max_value=1000000))
    def test_custom_max_length_is_respected(self, max_length):
        """Property: Custom max_length parameter should always be respected."""
        validator = InputValidator(max_length=max_length)

        # String at exactly max_length should be accepted
        text_at_limit = "a" * max_length
        result = validator.validate_and_sanitize(text_at_limit)
        assert len(result) == max_length

        # String over max_length should be rejected
        if max_length < 1000000:  # Avoid memory issues
            text_over_limit = "a" * (max_length + 1)
            with pytest.raises(InputValidationError, match="too long"):
                validator.validate_and_sanitize(text_over_limit)


class TestStringValidationProperties:
    """Property-based tests for string validation edge cases."""

    @given(st.text(
        alphabet=string.printable,
        min_size=1,
        max_size=1000
    ))
    def test_validation_never_crashes(self, text):
        """Property: Validation should never crash, regardless of input."""
        validator = InputValidator()

        try:
            # Should either succeed or raise InputValidationError
            validator.validate_and_sanitize(text)
        except InputValidationError:
            # This is expected for invalid input
            pass
        except Exception as e:
            # Any other exception is a bug
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")

    @given(st.text(min_size=1))
    def test_validation_is_deterministic(self, text):
        """Property: Validation should always return the same result for same input."""
        assume(len(text) <= MAX_INPUT_LENGTH)

        validator = InputValidator()

        try:
            result1 = validator.validate_and_sanitize(text)
            result2 = validator.validate_and_sanitize(text)
            assert result1 == result2
        except InputValidationError as e1:
            # Should raise same error message
            with pytest.raises(InputValidationError) as e2:
                validator.validate_and_sanitize(text)
            assert str(e1) == str(e2.value)

    @given(st.text(
        alphabet=string.ascii_letters + string.digits,
        min_size=1,
        max_size=100
    ))
    def test_alphanumeric_strings_are_always_safe(self, text):
        """Property: Purely alphanumeric strings should always be safe."""
        validator = InputValidator()

        # Should pass all validation
        result = validator.validate_and_sanitize(text)
        assert result == text

        result_sql = validator.validate_sql_safe(text)
        assert result_sql == text

    @given(st.text(min_size=1, max_size=100))
    def test_double_validation_is_idempotent(self, text):
        """Property: Validating twice should give same result as validating once."""
        assume(len(text) <= MAX_INPUT_LENGTH)
        assume(len(text.strip()) > 0)
        # Skip dangerous patterns
        assume(not any(p in text.lower() for p in [
            "<script", "javascript:", "onclick"
        ]))

        validator = InputValidator()

        try:
            result1 = validator.validate_and_sanitize(text)
            result2 = validator.validate_and_sanitize(result1)
            assert result1 == result2
        except InputValidationError:
            # If first validation fails, that's okay
            pass


class TestNumericValidationProperties:
    """Property-based tests for numeric validation."""

    @given(st.integers())
    def test_integers_convert_to_string_safely(self, number):
        """Property: Integers should convert to strings safely."""
        validator = InputValidator()

        text = str(number)
        result = validator.validate_and_sanitize(text)

        # Should preserve the number when stripped
        assert result.strip() == text.strip()

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_floats_convert_to_string_safely(self, number):
        """Property: Finite floats should convert to strings safely."""
        validator = InputValidator()

        text = str(number)
        assume(len(text) <= MAX_INPUT_LENGTH)

        result = validator.validate_and_sanitize(text)
        assert result.strip() == text.strip()


class TestContextValidationProperties:
    """Property-based tests for context validation."""

    @given(st.dictionaries(
        keys=st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
        values=st.just(None),
        max_size=100
    ))
    def test_dictionaries_with_none_values_are_serializable(self, context):
        """Property: Dictionaries with None values should be JSON-serializable."""
        import json
        validator = InputValidator()

        serialized = json.dumps(context)
        assume(len(serialized) <= MAX_CONTEXT_SIZE)

        result = validator.validate_context(context)
        assert result == context

    @given(st.none())
    def test_none_context_is_always_accepted(self, context):
        """Property: None should always be an acceptable context."""
        validator = InputValidator()

        result = validator.validate_context(context)
        assert result is None


# Example of using Hypothesis to find bugs
class TestRegressionFromHypothesis:
    """Tests for bugs found through property-based testing."""

    def test_null_byte_in_filename(self):
        """
        Regression test: Null bytes in filenames should be rejected.

        Found by Hypothesis generating strings with \x00.
        """
        validator = InputValidator()

        with pytest.raises(InputValidationError, match="null bytes"):
            validator.validate_filename("file\x00.txt")

    def test_unicode_normalization(self):
        """
        Test Unicode normalization edge cases.

        Some Unicode characters can look like ASCII but aren't.
        """
        validator = InputValidator()

        # These look similar but are different Unicode characters
        normal_a = "a"  # U+0061
        fullwidth_a = "ａ"  # U+FF41

        # Both should be accepted (as they're not dangerous)
        result1 = validator.validate_and_sanitize(normal_a)
        result2 = validator.validate_and_sanitize(fullwidth_a)

        assert result1 == normal_a
        assert result2 == fullwidth_a


if __name__ == "__main__":
    # Run property-based tests with verbose output
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
