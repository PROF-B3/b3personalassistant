"""
Unit tests for structured logging configuration.
"""

import pytest
import logging
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from core.logging_config import (
    StructuredFormatter,
    HumanReadableFormatter,
    ContextFilter,
    PerformanceLogger,
    setup_logging,
    get_logger,
    log_with_context,
)


class TestStructuredFormatter:
    """Test suite for StructuredFormatter."""

    def test_formats_basic_message(self):
        """Test that basic messages are formatted as valid JSON."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        data = json.loads(result)  # Should not raise exception

        assert "timestamp" in data
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "location" in data
        assert data["location"]["file"] == "test.py"
        assert data["location"]["line"] == 10

    def test_includes_context(self):
        """Test that extra context is included in JSON output."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        # Add custom context
        record.user_id = 123
        record.request_id = "abc"

        result = formatter.format(record)
        data = json.loads(result)

        assert "context" in data
        assert data["context"]["user_id"] == 123
        assert data["context"]["request_id"] == "abc"

    def test_includes_exception_info(self):
        """Test that exception info is properly included."""
        formatter = StructuredFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert "Test error" in data["exception"]["message"]
        assert "traceback" in data["exception"]
        assert isinstance(data["exception"]["traceback"], list)


class TestHumanReadableFormatter:
    """Test suite for HumanReadableFormatter."""

    def test_formats_basic_message(self):
        """Test that messages are formatted in human-readable format."""
        formatter = HumanReadableFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)

        assert "INFO" in result
        assert "test" in result
        assert "Test message" in result

    def test_includes_context_in_output(self):
        """Test that context is included in human-readable format."""
        formatter = HumanReadableFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.user_id = 123

        result = formatter.format(record)

        assert "Context:" in result
        assert "user_id" in result
        assert "123" in result


class TestContextFilter:
    """Test suite for ContextFilter."""

    def test_adds_default_context(self):
        """Test that default context is added to all records."""
        context_filter = ContextFilter({"environment": "test", "version": "1.0.0"})

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = context_filter.filter(record)

        assert result is True
        assert hasattr(record, "environment")
        assert record.environment == "test"
        assert hasattr(record, "version")
        assert record.version == "1.0.0"

    def test_does_not_override_existing_attributes(self):
        """Test that existing attributes are not overridden."""
        context_filter = ContextFilter({"environment": "production"})

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.environment = "test"

        context_filter.filter(record)

        # Should not override
        assert record.environment == "test"


class TestSetupLogging:
    """Test suite for setup_logging function."""

    def test_configures_console_logging(self, caplog):
        """Test that console logging is configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                console_output=True
            )

            logger = logging.getLogger("test")
            logger.info("Test message")

            # Check that log file was created
            assert log_file.exists()

    def test_creates_log_directory(self):
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "nested" / "dir" / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                console_output=False
            )

            logger = logging.getLogger("test")
            logger.info("Test message")

            # Check that nested directory was created
            assert log_file.parent.exists()
            assert log_file.exists()

    def test_json_format_option(self):
        """Test that JSON format option works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                json_format=True,
                console_output=False
            )

            logger = logging.getLogger("test")
            logger.info("Test message")

            # Read log file and verify JSON format
            content = log_file.read_text()
            data = json.loads(content.strip())

            assert "timestamp" in data
            assert data["message"] == "Test message"

    def test_default_context_is_added(self):
        """Test that default context is added to all logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                json_format=True,
                console_output=False,
                default_context={"environment": "test", "version": "1.0.0"}
            )

            logger = logging.getLogger("test")
            logger.info("Test message")

            # Read log and verify context
            content = log_file.read_text()
            data = json.loads(content.strip())

            assert "context" in data
            assert data["context"]["environment"] == "test"
            assert data["context"]["version"] == "1.0.0"


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger) or isinstance(logger, logging.LoggerAdapter)

    def test_logger_with_context(self):
        """Test that logger includes provided context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                json_format=True,
                console_output=False
            )

            logger = get_logger("test", user_id=123, request_id="abc")
            logger.info("Test message")

            # Read log and verify context
            content = log_file.read_text()
            data = json.loads(content.strip())

            assert "context" in data
            assert data["context"]["user_id"] == 123
            assert data["context"]["request_id"] == "abc"


class TestPerformanceLogger:
    """Test suite for PerformanceLogger context manager."""

    def test_logs_operation_timing(self, caplog):
        """Test that operation timing is logged."""
        setup_logging(log_level="INFO", log_file=None, console_output=True)
        logger = logging.getLogger("test")

        with caplog.at_level(logging.INFO):
            with PerformanceLogger("test_operation", logger):
                import time
                time.sleep(0.01)

        # Check that start and completion messages were logged
        messages = [record.message for record in caplog.records]
        assert any("Starting operation: test_operation" in msg for msg in messages)
        assert any("Completed operation: test_operation" in msg for msg in messages)

    def test_logs_operation_failure(self, caplog):
        """Test that operation failures are logged."""
        setup_logging(log_level="INFO", log_file=None, console_output=True)
        logger = logging.getLogger("test")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                with PerformanceLogger("test_operation", logger):
                    raise ValueError("Test error")

        # Check that failure message was logged
        messages = [record.message for record in caplog.records]
        assert any("Failed operation: test_operation" in msg for msg in messages)


class TestLogWithContext:
    """Test suite for log_with_context function."""

    def test_logs_with_context(self):
        """Test that context is included in log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_level="INFO",
                log_file=str(log_file),
                json_format=True,
                console_output=False
            )

            logger = logging.getLogger("test")
            log_with_context(logger, logging.INFO, "Test message", user_id=123)

            # Read log and verify context
            content = log_file.read_text()
            data = json.loads(content.strip())

            assert data["message"] == "Test message"
            assert "context" in data
            assert data["context"]["user_id"] == 123


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for complete logging workflow."""

    def test_complete_logging_workflow(self):
        """Test complete logging setup and usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Setup logging
            setup_logging(
                log_level="DEBUG",
                log_file=str(log_file),
                json_format=True,
                console_output=False,
                default_context={"app": "test", "version": "1.0"}
            )

            # Get logger with context
            logger = get_logger("integration_test", component="test")

            # Log various levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")

            # Log with additional context
            log_with_context(logger, logging.INFO, "Action", action="test", result="success")

            # Performance logging
            with PerformanceLogger("test_operation", logger, operation_type="test"):
                import time
                time.sleep(0.01)

            # Read all logs
            content = log_file.read_text()
            lines = content.strip().split("\n")

            # Verify all messages were logged
            assert len(lines) >= 5

            # Verify JSON format
            for line in lines:
                data = json.loads(line)
                assert "timestamp" in data
                assert "level" in data
                assert "message" in data

                # Check default context is present
                if "context" in data:
                    assert data["context"].get("app") == "test"
