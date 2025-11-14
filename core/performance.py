"""
Performance Monitoring and Profiling for B3PersonalAssistant

Provides decorators and utilities for monitoring performance,
tracking execution times, and identifying bottlenecks.
"""

import time
import functools
import logging
from typing import Callable, TypeVar, Any, Dict, Optional
from collections import defaultdict
from datetime import datetime
from threading import Lock

from core.constants import SLOW_QUERY_THRESHOLD_MS, SLOW_OPERATION_THRESHOLD_MS

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Global performance metrics storage
_performance_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    'call_count': 0,
    'total_time_ms': 0.0,
    'min_time_ms': float('inf'),
    'max_time_ms': 0.0,
    'errors': 0,
    'last_called': None,
})
_metrics_lock = Lock()


def track_performance(
    func_name: Optional[str] = None,
    slow_threshold_ms: float = SLOW_OPERATION_THRESHOLD_MS
) -> Callable:
    """
    Decorator to track function performance metrics.

    Tracks call count, execution times (min/max/total), errors, and last call time.
    Logs warnings for slow operations.

    Args:
        func_name: Custom name for the function (defaults to function.__name__)
        slow_threshold_ms: Threshold in ms to log slow operation warnings

    Returns:
        Decorated function

    Example:
        >>> @track_performance(slow_threshold_ms=100)
        ... def expensive_operation():
        ...     time.sleep(0.2)
        ...     return "result"
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = func_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.perf_counter()
            error_occurred = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                raise
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                # Update metrics
                with _metrics_lock:
                    metrics = _performance_metrics[name]
                    metrics['call_count'] += 1
                    metrics['total_time_ms'] += duration_ms
                    metrics['min_time_ms'] = min(metrics['min_time_ms'], duration_ms)
                    metrics['max_time_ms'] = max(metrics['max_time_ms'], duration_ms)
                    metrics['last_called'] = datetime.now().isoformat()

                    if error_occurred:
                        metrics['errors'] += 1

                # Log slow operations
                if duration_ms > slow_threshold_ms:
                    logger.warning(
                        f"Slow operation detected: {name} took {duration_ms:.2f}ms "
                        f"(threshold: {slow_threshold_ms}ms)"
                    )
                else:
                    logger.debug(f"{name} completed in {duration_ms:.2f}ms")

        return wrapper
    return decorator


def track_database_query(query_name: Optional[str] = None) -> Callable:
    """
    Specialized decorator for tracking database query performance.

    Uses a lower threshold for slow query detection.

    Args:
        query_name: Custom name for the query

    Returns:
        Decorated function

    Example:
        >>> @track_database_query("fetch_users")
        ... def get_users():
        ...     return db.query("SELECT * FROM users")
    """
    return track_performance(
        func_name=query_name,
        slow_threshold_ms=SLOW_QUERY_THRESHOLD_MS
    )


def get_performance_metrics(function_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance metrics for a function or all functions.

    Args:
        function_name: Specific function name, or None for all functions

    Returns:
        Dictionary of performance metrics

    Example:
        >>> metrics = get_performance_metrics("expensive_operation")
        >>> print(f"Called {metrics['call_count']} times")
        >>> print(f"Average time: {metrics['avg_time_ms']:.2f}ms")
    """
    with _metrics_lock:
        if function_name:
            if function_name not in _performance_metrics:
                return {}

            metrics = _performance_metrics[function_name].copy()
            # Calculate average
            if metrics['call_count'] > 0:
                metrics['avg_time_ms'] = metrics['total_time_ms'] / metrics['call_count']
            else:
                metrics['avg_time_ms'] = 0.0

            return metrics
        else:
            # Return all metrics
            all_metrics = {}
            for name, metrics in _performance_metrics.items():
                metrics_copy = metrics.copy()
                if metrics_copy['call_count'] > 0:
                    metrics_copy['avg_time_ms'] = (
                        metrics_copy['total_time_ms'] / metrics_copy['call_count']
                    )
                else:
                    metrics_copy['avg_time_ms'] = 0.0
                all_metrics[name] = metrics_copy

            return all_metrics


def reset_performance_metrics(function_name: Optional[str] = None):
    """
    Reset performance metrics for a function or all functions.

    Args:
        function_name: Specific function name, or None to reset all
    """
    with _metrics_lock:
        if function_name:
            if function_name in _performance_metrics:
                del _performance_metrics[function_name]
        else:
            _performance_metrics.clear()


def print_performance_report(top_n: int = 10):
    """
    Print a formatted performance report.

    Args:
        top_n: Number of top functions to show (by total time)

    Example:
        >>> print_performance_report(top_n=5)
        Performance Report:
        ==================
        expensive_operation:
          Calls: 100
          Total: 5000.00ms
          Avg: 50.00ms
          Min: 45.00ms
          Max: 120.00ms
          Errors: 2
    """
    metrics = get_performance_metrics()

    if not metrics:
        print("No performance data available")
        return

    # Sort by total time
    sorted_metrics = sorted(
        metrics.items(),
        key=lambda x: x[1]['total_time_ms'],
        reverse=True
    )[:top_n]

    print("\nPerformance Report")
    print("=" * 80)

    for name, data in sorted_metrics:
        print(f"\n{name}:")
        print(f"  Calls:        {data['call_count']}")
        print(f"  Total Time:   {data['total_time_ms']:.2f}ms")
        print(f"  Avg Time:     {data['avg_time_ms']:.2f}ms")
        print(f"  Min Time:     {data['min_time_ms']:.2f}ms")
        print(f"  Max Time:     {data['max_time_ms']:.2f}ms")
        print(f"  Errors:       {data['errors']}")

        if data['last_called']:
            print(f"  Last Called:  {data['last_called']}")

    print("\n" + "=" * 80)


class PerformanceTimer:
    """
    Context manager for timing code blocks.

    Example:
        >>> with PerformanceTimer("complex_operation") as timer:
        ...     # Do something expensive
        ...     time.sleep(0.1)
        >>> print(f"Operation took {timer.elapsed_ms:.2f}ms")
    """

    def __init__(self, name: str, log_on_exit: bool = True):
        """
        Initialize performance timer.

        Args:
            name: Name for this timer
            log_on_exit: Whether to log elapsed time on exit
        """
        self.name = name
        self.log_on_exit = log_on_exit
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_ms: float = 0.0

    def __enter__(self):
        """Start the timer."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the timer and optionally log."""
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000

        if self.log_on_exit:
            if exc_type is None:
                logger.debug(f"{self.name} completed in {self.elapsed_ms:.2f}ms")
            else:
                logger.warning(
                    f"{self.name} failed after {self.elapsed_ms:.2f}ms: {exc_val}"
                )

        return False  # Don't suppress exceptions


def measure_memory_usage(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure memory usage of a function.

    Requires psutil to be installed.

    Args:
        func: Function to measure

    Returns:
        Decorated function

    Example:
        >>> @measure_memory_usage
        ... def load_large_dataset():
        ...     return [i for i in range(1000000)]
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / 1024 / 1024  # MB

            result = func(*args, **kwargs)

            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_diff = mem_after - mem_before

            logger.info(
                f"{func.__name__} memory usage: "
                f"before={mem_before:.2f}MB, after={mem_after:.2f}MB, "
                f"diff={mem_diff:+.2f}MB"
            )

            return result

        except ImportError:
            logger.warning("psutil not installed, memory measurement skipped")
            return func(*args, **kwargs)

    return wrapper


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    @track_performance(slow_threshold_ms=50)
    def fast_function():
        """Fast function that should not trigger warnings."""
        time.sleep(0.01)
        return "fast"

    @track_performance(slow_threshold_ms=50)
    def slow_function():
        """Slow function that should trigger warnings."""
        time.sleep(0.1)
        return "slow"

    # Test the decorators
    for _ in range(5):
        fast_function()
        slow_function()

    # Print report
    print_performance_report()

    # Test context manager
    with PerformanceTimer("manual_timing") as timer:
        time.sleep(0.05)

    print(f"\nManual timing: {timer.elapsed_ms:.2f}ms")
