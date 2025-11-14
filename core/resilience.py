"""
Resilience patterns for B3PersonalAssistant.
Implements circuit breaker, retry logic, and timeout handling for robust operation.
"""

import time
import logging
from typing import Callable, Any, Optional, TypeVar, Dict
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from core.exceptions import (
    CircuitBreakerOpenError,
    OllamaConnectionError,
    OllamaTimeoutError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Successes needed to close from half-open
    timeout: float = 60.0  # Seconds to wait before trying again
    excluded_exceptions: tuple = ()  # Exceptions that don't count as failures


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by temporarily blocking calls to failing services.
    Automatically recovers when the service becomes healthy again.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests rejected immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed

    Example:
        >>> breaker = CircuitBreaker(name="ollama")
        >>> @breaker.call
        ... def risky_operation():
        ...     return ollama_client.chat(...)
        >>> result = risky_operation()
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name for this circuit breaker (for logging)
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"circuit_breaker.{name}")

    def call(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to protect a function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Wrapped function with circuit breaker protection
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.logger.info(f"Circuit {self.name}: Attempting reset (half-open)")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    self.logger.warning(f"Circuit {self.name}: Open, rejecting call")
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is open. "
                        f"Service unavailable. Try again in {self._time_until_retry():.0f}s"
                    )

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Record success
                self._on_success()
                return result

            except Exception as e:
                # Check if this exception should be excluded
                if isinstance(e, self.config.excluded_exceptions):
                    raise

                # Record failure
                self._on_failure(e)
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout

    def _time_until_retry(self) -> float:
        """Calculate seconds until next retry attempt."""
        if self.last_failure_time is None:
            return 0.0

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0.0, self.config.timeout - elapsed)

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.logger.info(
                f"Circuit {self.name}: Success in half-open "
                f"({self.success_count}/{self.config.success_threshold})"
            )

            if self.success_count >= self.config.success_threshold:
                self.logger.info(f"Circuit {self.name}: Closing (service recovered)")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _on_failure(self, exception: Exception):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        self.logger.warning(
            f"Circuit {self.name}: Failure #{self.failure_count} - {type(exception).__name__}: {exception}"
        )

        if self.state == CircuitState.HALF_OPEN:
            self.logger.warning(f"Circuit {self.name}: Failed in half-open, reopening")
            self.state = CircuitState.OPEN
            self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.logger.error(
                    f"Circuit {self.name}: Opening (threshold {self.config.failure_threshold} reached)"
                )
                self.state = CircuitState.OPEN

    def reset(self):
        """Manually reset the circuit breaker."""
        self.logger.info(f"Circuit {self.name}: Manual reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else 0
        }


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorator function

    Example:
        >>> @retry_with_backoff(max_attempts=3, base_delay=1.0)
        ... def unstable_operation():
        ...     return ollama_client.chat(...)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: "
                            f"{type(e).__name__}: {e}. Retrying in {delay:.1f}s..."
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: "
                            f"{type(e).__name__}: {e}"
                        )

            # All retries exhausted
            raise last_exception

        return wrapper
    return decorator


def timeout(seconds: float) -> Callable:
    """
    Decorator to add timeout to a function using threading.

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorator function

    Raises:
        OllamaTimeoutError: If function execution exceeds timeout

    Example:
        >>> @timeout(30.0)
        ... def slow_operation():
        ...     return ollama_client.chat(...)
    """
    import threading

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                # Thread is still running - timeout occurred
                logger.warning(f"Function {func.__name__} timed out after {seconds}s")
                from core.exceptions import OllamaTimeoutError
                raise OllamaTimeoutError(f"Operation timed out after {seconds} seconds")

            if exception[0] is not None:
                raise exception[0]

            return result[0]
        return wrapper
    return decorator


# Global circuit breakers for different services
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """
    Get or create a circuit breaker by name.

    Args:
        name: Circuit breaker name
        config: Optional configuration

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def reset_all_circuit_breakers():
    """Reset all circuit breakers (useful for testing)."""
    for breaker in _circuit_breakers.values():
        breaker.reset()


def get_all_circuit_breaker_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers."""
    return {name: breaker.get_status() for name, breaker in _circuit_breakers.items()}
