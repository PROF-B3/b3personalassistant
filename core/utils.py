"""
Utility Functions for B3PersonalAssistant

Common utility functions used across the application.
"""

import re
import hashlib
import unicodedata
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, TypeVar, Callable
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# TEXT UTILITIES
# =============================================================================

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text with suffix if needed

    Example:
        >>> truncate_text("Hello World", 8)
        "Hello..."
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str, separator: str = "-") -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to convert
        separator: Word separator

    Returns:
        Slugified text

    Example:
        >>> slugify("Hello World!")
        "hello-world"
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Convert to lowercase and replace spaces
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', separator, text)

    return text


def extract_tags(text: str) -> List[str]:
    """
    Extract hashtags from text.

    Args:
        text: Text containing hashtags

    Returns:
        List of tags (without #)

    Example:
        >>> extract_tags("Check this #python #coding")
        ["python", "coding"]
    """
    return re.findall(r'#(\w+)', text)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string for use as a filename.

    Args:
        filename: Original filename

    Returns:
        Safe filename

    Example:
        >>> sanitize_filename("My File: Test?.txt")
        "My File_ Test_.txt"
    """
    # Replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    return filename or 'unnamed'


def word_count(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Text to count

    Returns:
        Number of words
    """
    return len(text.split())


def reading_time_minutes(text: str, wpm: int = 200) -> int:
    """
    Estimate reading time in minutes.

    Args:
        text: Text to estimate
        wpm: Words per minute (default 200)

    Returns:
        Estimated minutes to read
    """
    words = word_count(text)
    return max(1, round(words / wpm))


# =============================================================================
# DATE/TIME UTILITIES
# =============================================================================

def parse_relative_date(text: str) -> Optional[datetime]:
    """
    Parse relative date expressions.

    Args:
        text: Text like "tomorrow", "next week", "in 3 days"

    Returns:
        datetime object or None if not recognized

    Example:
        >>> parse_relative_date("tomorrow")
        datetime(2024, 1, 2, ...)  # Next day
    """
    text = text.lower().strip()
    now = datetime.now()

    patterns = {
        'today': now,
        'tomorrow': now + timedelta(days=1),
        'yesterday': now - timedelta(days=1),
        'next week': now + timedelta(weeks=1),
        'next month': now + timedelta(days=30),
    }

    if text in patterns:
        return patterns[text]

    # Match "in X days/weeks/months"
    match = re.match(r'in\s+(\d+)\s+(day|week|month)s?', text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == 'day':
            return now + timedelta(days=amount)
        elif unit == 'week':
            return now + timedelta(weeks=amount)
        elif unit == 'month':
            return now + timedelta(days=amount * 30)

    return None


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2h 30m" or "45s"

    Example:
        >>> format_duration(3665)
        "1h 1m 5s"
    """
    if seconds < 60:
        return f"{int(seconds)}s"

    minutes, secs = divmod(int(seconds), 60)
    hours, mins = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    if secs and not hours:  # Only show seconds if under 1 hour
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time.

    Args:
        dt: datetime to format

    Returns:
        String like "2 hours ago" or "in 3 days"

    Example:
        >>> format_relative_time(datetime.now() - timedelta(hours=2))
        "2 hours ago"
    """
    now = datetime.now()
    diff = now - dt

    if diff.total_seconds() < 0:
        # Future
        diff = -diff
        suffix = "from now"
    else:
        suffix = "ago"

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now" if suffix == "ago" else "soon"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} {suffix}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} {suffix}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} {suffix}"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} {suffix}"


# =============================================================================
# HASHING UTILITIES
# =============================================================================

def generate_id(content: str, prefix: str = "") -> str:
    """
    Generate a unique ID based on content.

    Args:
        content: Content to hash
        prefix: Optional prefix

    Returns:
        Short unique ID

    Example:
        >>> generate_id("Hello World", "note_")
        "note_a591a6d4"
    """
    hash_obj = hashlib.sha256(content.encode())
    short_hash = hash_obj.hexdigest()[:8]
    return f"{prefix}{short_hash}"


def content_hash(content: str) -> str:
    """
    Generate a content hash for deduplication.

    Args:
        content: Content to hash

    Returns:
        SHA-256 hash string
    """
    return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# COLLECTION UTILITIES
# =============================================================================

def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Example:
        >>> chunk_list([1,2,3,4,5], 2)
        [[1,2], [3,4], [5]]
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Key separator

    Returns:
        Flattened dictionary

    Example:
        >>> flatten_dict({'a': {'b': 1, 'c': 2}})
        {'a.b': 1, 'a.c': 2}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary with overriding values

    Returns:
        Merged dictionary

    Example:
        >>> deep_merge({'a': {'b': 1}}, {'a': {'c': 2}})
        {'a': {'b': 1, 'c': 2}}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


# =============================================================================
# DECORATORS
# =============================================================================

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch

    Example:
        >>> @retry(max_attempts=3, delay=1.0)
        ... def unstable_function():
        ...     ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff

            logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            raise last_exception

        return wrapper
    return decorator


def timed(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log function execution time.

    Example:
        >>> @timed
        ... def slow_function():
        ...     time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} completed in {elapsed:.3f}s")
        return result
    return wrapper


def deprecated(message: str = ""):
    """
    Decorator to mark a function as deprecated.

    Args:
        message: Deprecation message

    Example:
        >>> @deprecated("Use new_function instead")
        ... def old_function():
        ...     ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            warning = f"{func.__name__} is deprecated"
            if message:
                warning += f": {message}"
            logger.warning(warning)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def is_valid_email(email: str) -> bool:
    """
    Check if string is a valid email address.

    Args:
        email: String to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL.

    Args:
        url: String to validate

    Returns:
        True if valid URL format
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")

    # Text utilities
    assert truncate_text("Hello World", 8) == "Hello..."
    assert slugify("Hello World!") == "hello-world"
    assert extract_tags("Check #python #coding") == ["python", "coding"]
    assert sanitize_filename("My:File?.txt") == "My_File_.txt"

    # Date utilities
    assert parse_relative_date("tomorrow") is not None
    assert format_duration(3665) == "1h 1m 5s"

    # Hash utilities
    assert len(generate_id("test")) == 8
    assert len(content_hash("test")) == 64

    # Collection utilities
    assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert flatten_dict({'a': {'b': 1}}) == {'a.b': 1}

    # Validation
    assert is_valid_email("test@example.com")
    assert not is_valid_email("invalid")
    assert is_valid_url("https://example.com")
    assert not is_valid_url("not a url")

    print("All utility tests passed!")
