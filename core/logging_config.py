"""
Structured Logging Configuration for B3PersonalAssistant

Provides JSON-formatted logging with context, filtering, and multiple output formats.
Supports both structured (JSON) and human-readable console output.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
import traceback

from core.constants import (
    LOG_LEVEL,
    LOG_FILE_PATH,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOG_FORMAT_JSON,
)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.

    Each log entry includes:
    - timestamp: ISO format timestamp
    - level: Log level name
    - logger: Logger name
    - message: Log message
    - context: Additional context data
    - exception: Exception info if present
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add location info
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add context from extra fields
        context = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info"
            ]:
                context[key] = value

        if context:
            log_data["context"] = context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter with color support for console output.

    Format: [TIMESTAMP] LEVEL - logger_name - message (context)
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize formatter.

        Args:
            use_colors: Whether to use ANSI colors in output
        """
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format."""
        # Base format
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, self.COLORS["RESET"])
            level = f"{color}{level}{self.COLORS['RESET']}"

        base_msg = f"[{timestamp}] {level:8s} - {record.name} - {record.getMessage()}"

        # Add context if present
        context = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info"
            ]:
                context[key] = value

        if context:
            base_msg += f" | Context: {json.dumps(context)}"

        # Add exception info if present
        if record.exc_info:
            base_msg += "\n" + self.formatException(record.exc_info)

        return base_msg


class ContextFilter(logging.Filter):
    """
    Filter that adds default context to all log records.

    Useful for adding global context like environment, version, etc.
    """

    def __init__(self, default_context: Optional[Dict[str, Any]] = None):
        """
        Initialize filter with default context.

        Args:
            default_context: Default context to add to all records
        """
        super().__init__()
        self.default_context = default_context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add default context to record."""
        for key, value in self.default_context.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True


def setup_logging(
    log_level: str = LOG_LEVEL,
    log_file: Optional[str] = LOG_FILE_PATH,
    json_format: bool = LOG_FORMAT_JSON,
    console_output: bool = True,
    default_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None to disable file logging)
        json_format: Whether to use JSON format for file logs
        console_output: Whether to output to console
        default_context: Default context to add to all logs

    Example:
        >>> setup_logging(
        ...     log_level="INFO",
        ...     log_file="logs/app.log",
        ...     json_format=True,
        ...     default_context={"environment": "production", "version": "1.0.0"}
        ... )
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add context filter if default context provided
    if default_context:
        context_filter = ContextFilter(default_context)
        root_logger.addFilter(context_filter)

    # Console handler (human-readable)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(HumanReadableFormatter(use_colors=True))
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        if json_format:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(HumanReadableFormatter(use_colors=False))

        root_logger.addHandler(file_handler)


def get_logger(name: str, **context) -> logging.Logger:
    """
    Get a logger with optional context.

    Args:
        name: Logger name (typically __name__)
        **context: Additional context to include in all logs

    Returns:
        Logger instance with context

    Example:
        >>> logger = get_logger(__name__, user_id=123, request_id="abc")
        >>> logger.info("Processing request")
        # Logs will include user_id and request_id in context
    """
    logger = logging.getLogger(name)

    if context:
        # Create adapter that adds context to all log calls
        logger = logging.LoggerAdapter(logger, context)

    return logger


class PerformanceLogger:
    """
    Context manager for logging operation performance.

    Example:
        >>> with PerformanceLogger("database_query", logger, query_type="SELECT"):
        ...     result = db.query(sql)
        # Logs: Operation 'database_query' completed in 45.23ms
    """

    def __init__(
        self,
        operation_name: str,
        logger: logging.Logger,
        log_level: int = logging.INFO,
        **context
    ):
        """
        Initialize performance logger.

        Args:
            operation_name: Name of the operation being timed
            logger: Logger to use for output
            log_level: Log level for performance messages
            **context: Additional context to include
        """
        self.operation_name = operation_name
        self.logger = logger
        self.log_level = log_level
        self.context = context
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.now()
        self.logger.log(
            self.log_level,
            f"Starting operation: {self.operation_name}",
            extra=self.context
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log result."""
        self.end_time = datetime.now()
        duration_ms = (self.end_time - self.start_time).total_seconds() * 1000

        context = {**self.context, "duration_ms": duration_ms}

        if exc_type is None:
            self.logger.log(
                self.log_level,
                f"Completed operation: {self.operation_name} in {duration_ms:.2f}ms",
                extra=context
            )
        else:
            self.logger.error(
                f"Failed operation: {self.operation_name} after {duration_ms:.2f}ms",
                extra=context,
                exc_info=(exc_type, exc_val, exc_tb)
            )

        return False  # Don't suppress exceptions


# Convenience functions for common logging patterns

def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """
    Log a message with additional context.

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context fields

    Example:
        >>> log_with_context(logger, logging.INFO, "User login", user_id=123, ip="1.2.3.4")
    """
    logger.log(level, message, extra=context)


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with arguments.

    Example:
        >>> @log_function_call(logger)
        ... def process_data(data_id: int, options: dict):
        ...     pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(
                f"Calling {func_name}",
                extra={
                    "function": func_name,
                    "args": str(args)[:100],  # Limit length
                    "kwargs": str(kwargs)[:100]
                }
            )

            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}", extra={"function": func_name})
                return result
            except Exception as e:
                logger.error(
                    f"Error in {func_name}: {e}",
                    extra={"function": func_name},
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    setup_logging(
        log_level="DEBUG",
        log_file="logs/test.log",
        json_format=True,
        default_context={"environment": "test", "version": "1.0.0"}
    )

    # Get logger
    logger = get_logger(__name__, component="test")

    # Test different log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test with context
    log_with_context(
        logger,
        logging.INFO,
        "User action",
        user_id=123,
        action="login",
        ip="192.168.1.1"
    )

    # Test performance logging
    with PerformanceLogger("test_operation", logger, query_type="SELECT"):
        import time
        time.sleep(0.1)

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Exception occurred")

    print("\n✅ Structured logging test completed!")
    print("Check logs/test.log for JSON output")
