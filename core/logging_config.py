"""
Centralized Logging Configuration for B3PersonalAssistant

Provides consistent logging setup across all modules with support for:
- Console and file output
- JSON structured logging (optional)
- Log rotation
- Different log levels per module
"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    console_output: bool = True
    file_output: bool = True
    json_format: bool = False
    max_file_size_mb: int = 10
    backup_count: int = 5
    module_levels: Dict[str, LogLevel] = field(default_factory=dict)


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs logs as JSON objects for easy parsing by log aggregation tools.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability.
    """

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def __init__(self, fmt: str = None, use_colors: bool = True):
        super().__init__(fmt)
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            record.name = f"\033[34m{record.name}{self.RESET}"
        return super().format(record)


class LogManager:
    """
    Centralized log manager for the application.

    Example:
        >>> log_manager = LogManager()
        >>> log_manager.configure(LogConfig(level=LogLevel.DEBUG))
        >>> logger = log_manager.get_logger("my_module")
        >>> logger.info("Hello, world!")
    """

    _instance: Optional['LogManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config = LogConfig()
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: list = []

    def configure(self, config: LogConfig) -> None:
        """
        Configure logging with the given settings.

        Args:
            config: LogConfig instance with desired settings
        """
        self.config = config

        # Create log directory
        if config.file_output:
            config.log_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Clear our tracked handlers
        self._handlers.clear()

        # Set root level
        root_logger.setLevel(config.level.value)

        # Add console handler
        if config.console_output:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)
            self._handlers.append(console_handler)

        # Add file handler
        if config.file_output:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
            self._handlers.append(file_handler)

        # Set module-specific levels
        for module_name, level in config.module_levels.items():
            logging.getLogger(module_name).setLevel(level.value)

    def _create_console_handler(self) -> logging.Handler:
        """Create console handler with appropriate formatter."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.config.level.value)

        if self.config.json_format:
            handler.setFormatter(JSONFormatter())
        else:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            handler.setFormatter(ColoredFormatter(fmt))

        return handler

    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler."""
        log_file = self.config.log_dir / "b3assistant.log"

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_file_size_mb * 1024 * 1024,
            backupCount=self.config.backup_count
        )
        handler.setLevel(self.config.level.value)

        if self.config.json_format:
            handler.setFormatter(JSONFormatter())
        else:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
            handler.setFormatter(logging.Formatter(fmt))

        return handler

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for the given name.

        Args:
            name: Logger name (typically __name__)

        Returns:
            Configured logger instance
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)

            # Check for module-specific level
            if name in self.config.module_levels:
                logger.setLevel(self.config.module_levels[name].value)

            self._loggers[name] = logger

        return self._loggers[name]

    def set_level(self, level: LogLevel, module: Optional[str] = None) -> None:
        """
        Set log level for root or specific module.

        Args:
            level: New log level
            module: Module name (None for root)
        """
        if module:
            logging.getLogger(module).setLevel(level.value)
            self.config.module_levels[module] = level
        else:
            logging.getLogger().setLevel(level.value)
            self.config.level = level

    def add_context(self, **kwargs) -> logging.LoggerAdapter:
        """
        Create a logger adapter with additional context.

        Args:
            **kwargs: Context key-value pairs

        Returns:
            LoggerAdapter with context
        """
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                extra = kwargs.get('extra', {})
                extra['extra_data'] = self.extra
                kwargs['extra'] = extra
                return msg, kwargs

        return ContextAdapter(logging.getLogger(), kwargs)


# Global log manager instance
_log_manager: Optional[LogManager] = None


def get_log_manager() -> LogManager:
    """Get the global log manager instance."""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def configure_logging(
    level: str = "INFO",
    log_dir: str = "logs",
    console: bool = True,
    file: bool = True,
    json_format: bool = False
) -> None:
    """
    Convenience function to configure logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        console: Enable console output
        file: Enable file output
        json_format: Use JSON formatting
    """
    config = LogConfig(
        level=LogLevel[level.upper()],
        log_dir=Path(log_dir),
        console_output=console,
        file_output=file,
        json_format=json_format
    )
    get_log_manager().configure(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger
    """
    return get_log_manager().get_logger(name)


if __name__ == "__main__":
    # Demo logging configuration
    configure_logging(level="DEBUG", file=False)

    logger = get_logger("demo")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test with JSON format
    print("\n--- JSON Format ---")
    configure_logging(level="INFO", file=False, json_format=True)
    logger = get_logger("demo.json")
    logger.info("JSON formatted message")
