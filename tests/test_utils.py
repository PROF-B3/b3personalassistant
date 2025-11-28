"""
Tests for the utility functions module.

Tests cover:
- Text utilities
- Date/time utilities
- Hashing utilities
- Collection utilities
- Decorators
- Validation utilities
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

from core.utils import (
    # Text utilities
    truncate_text,
    slugify,
    extract_tags,
    sanitize_filename,
    word_count,
    reading_time_minutes,
    # Date utilities
    parse_relative_date,
    format_duration,
    format_relative_time,
    # Hash utilities
    generate_id,
    content_hash,
    # Collection utilities
    chunk_list,
    flatten_dict,
    deep_merge,
    # Decorators
    retry,
    timed,
    deprecated,
    # Validation
    is_valid_email,
    is_valid_url,
)


class TestTextUtilities:
    """Tests for text utility functions."""

    def test_truncate_text_short(self):
        """Test truncating text shorter than limit."""
        assert truncate_text("Hello", 10) == "Hello"

    def test_truncate_text_exact(self):
        """Test truncating text exactly at limit."""
        assert truncate_text("Hello", 5) == "Hello"

    def test_truncate_text_long(self):
        """Test truncating text longer than limit."""
        assert truncate_text("Hello World", 8) == "Hello..."

    def test_truncate_text_custom_suffix(self):
        """Test truncating with custom suffix."""
        assert truncate_text("Hello World", 9, "…") == "Hello Wo…"

    def test_slugify_basic(self):
        """Test basic slugification."""
        assert slugify("Hello World") == "hello-world"

    def test_slugify_special_chars(self):
        """Test slugification with special characters."""
        assert slugify("Hello, World!") == "hello-world"

    def test_slugify_multiple_spaces(self):
        """Test slugification with multiple spaces."""
        assert slugify("Hello    World") == "hello-world"

    def test_slugify_custom_separator(self):
        """Test slugification with custom separator."""
        assert slugify("Hello World", "_") == "hello_world"

    def test_slugify_unicode(self):
        """Test slugification with unicode characters."""
        assert slugify("Café résumé") == "cafe-resume"

    def test_extract_tags(self):
        """Test extracting hashtags."""
        assert extract_tags("Check #python #coding") == ["python", "coding"]

    def test_extract_tags_no_tags(self):
        """Test extracting from text without tags."""
        assert extract_tags("No tags here") == []

    def test_extract_tags_mixed(self):
        """Test extracting tags from mixed content."""
        text = "Working on #project with #team today"
        assert extract_tags(text) == ["project", "team"]

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("My File.txt") == "My File.txt"

    def test_sanitize_filename_special_chars(self):
        """Test filename sanitization with special characters."""
        assert sanitize_filename("My:File?.txt") == "My_File_.txt"

    def test_sanitize_filename_all_invalid(self):
        """Test filename with all invalid characters."""
        assert sanitize_filename(":<>?") == "____"

    def test_sanitize_filename_empty(self):
        """Test empty filename."""
        assert sanitize_filename("") == "unnamed"

    def test_word_count(self):
        """Test word counting."""
        assert word_count("Hello World") == 2
        assert word_count("One") == 1
        assert word_count("") == 1  # Empty string splits to ['']

    def test_reading_time_minutes(self):
        """Test reading time estimation."""
        # 200 words should take 1 minute at 200 wpm
        text = " ".join(["word"] * 200)
        assert reading_time_minutes(text) == 1

        # 400 words should take 2 minutes
        text = " ".join(["word"] * 400)
        assert reading_time_minutes(text) == 2


class TestDateUtilities:
    """Tests for date/time utility functions."""

    def test_parse_relative_date_today(self):
        """Test parsing 'today'."""
        result = parse_relative_date("today")
        assert result.date() == datetime.now().date()

    def test_parse_relative_date_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_relative_date("tomorrow")
        expected = datetime.now() + timedelta(days=1)
        assert result.date() == expected.date()

    def test_parse_relative_date_in_days(self):
        """Test parsing 'in X days'."""
        result = parse_relative_date("in 3 days")
        expected = datetime.now() + timedelta(days=3)
        assert result.date() == expected.date()

    def test_parse_relative_date_in_weeks(self):
        """Test parsing 'in X weeks'."""
        result = parse_relative_date("in 2 weeks")
        expected = datetime.now() + timedelta(weeks=2)
        assert result.date() == expected.date()

    def test_parse_relative_date_invalid(self):
        """Test parsing invalid date string."""
        assert parse_relative_date("not a date") is None

    def test_format_duration_seconds(self):
        """Test formatting seconds."""
        assert format_duration(45) == "45s"

    def test_format_duration_minutes(self):
        """Test formatting minutes."""
        assert format_duration(90) == "1m 30s"

    def test_format_duration_hours(self):
        """Test formatting hours."""
        assert format_duration(3665) == "1h 1m 5s"

    def test_format_duration_hours_no_seconds(self):
        """Test formatting hours without seconds shown."""
        assert format_duration(3660) == "1h 1m"

    def test_format_relative_time_just_now(self):
        """Test 'just now' formatting."""
        assert format_relative_time(datetime.now()) == "just now"

    def test_format_relative_time_minutes_ago(self):
        """Test minutes ago formatting."""
        past = datetime.now() - timedelta(minutes=5)
        assert "5 minutes ago" in format_relative_time(past)

    def test_format_relative_time_hours_ago(self):
        """Test hours ago formatting."""
        past = datetime.now() - timedelta(hours=2)
        assert "2 hours ago" in format_relative_time(past)

    def test_format_relative_time_future(self):
        """Test future time formatting."""
        future = datetime.now() + timedelta(hours=2)
        result = format_relative_time(future)
        assert "from now" in result


class TestHashUtilities:
    """Tests for hashing utility functions."""

    def test_generate_id(self):
        """Test ID generation."""
        id1 = generate_id("test content")
        assert len(id1) == 8

    def test_generate_id_with_prefix(self):
        """Test ID generation with prefix."""
        id1 = generate_id("test content", "note_")
        assert id1.startswith("note_")
        assert len(id1) == 13  # 5 + 8

    def test_generate_id_deterministic(self):
        """Test that same content generates same ID."""
        id1 = generate_id("test content")
        id2 = generate_id("test content")
        assert id1 == id2

    def test_generate_id_different(self):
        """Test that different content generates different IDs."""
        id1 = generate_id("content 1")
        id2 = generate_id("content 2")
        assert id1 != id2

    def test_content_hash(self):
        """Test content hash generation."""
        hash1 = content_hash("test content")
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars

    def test_content_hash_deterministic(self):
        """Test that same content generates same hash."""
        hash1 = content_hash("test")
        hash2 = content_hash("test")
        assert hash1 == hash2


class TestCollectionUtilities:
    """Tests for collection utility functions."""

    def test_chunk_list_even(self):
        """Test chunking a list that divides evenly."""
        result = chunk_list([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_chunk_list_uneven(self):
        """Test chunking a list that doesn't divide evenly."""
        result = chunk_list([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_list_empty(self):
        """Test chunking an empty list."""
        assert chunk_list([], 2) == []

    def test_chunk_list_single(self):
        """Test chunking with single item."""
        assert chunk_list([1], 2) == [[1]]

    def test_flatten_dict_simple(self):
        """Test flattening a simple nested dict."""
        assert flatten_dict({'a': {'b': 1}}) == {'a.b': 1}

    def test_flatten_dict_deep(self):
        """Test flattening a deeply nested dict."""
        nested = {'a': {'b': {'c': 1}}}
        assert flatten_dict(nested) == {'a.b.c': 1}

    def test_flatten_dict_mixed(self):
        """Test flattening a dict with mixed nesting."""
        nested = {'a': 1, 'b': {'c': 2, 'd': 3}}
        result = flatten_dict(nested)
        assert result == {'a': 1, 'b.c': 2, 'b.d': 3}

    def test_flatten_dict_custom_sep(self):
        """Test flattening with custom separator."""
        nested = {'a': {'b': 1}}
        assert flatten_dict(nested, sep='_') == {'a_b': 1}

    def test_deep_merge_simple(self):
        """Test simple deep merge."""
        base = {'a': 1}
        override = {'b': 2}
        result = deep_merge(base, override)
        assert result == {'a': 1, 'b': 2}

    def test_deep_merge_override(self):
        """Test deep merge with override."""
        base = {'a': 1}
        override = {'a': 2}
        result = deep_merge(base, override)
        assert result == {'a': 2}

    def test_deep_merge_nested(self):
        """Test deep merge with nested dicts."""
        base = {'a': {'b': 1, 'c': 2}}
        override = {'a': {'c': 3, 'd': 4}}
        result = deep_merge(base, override)
        assert result == {'a': {'b': 1, 'c': 3, 'd': 4}}


class TestDecorators:
    """Tests for decorator functions."""

    def test_retry_success(self):
        """Test retry decorator with successful function."""
        call_count = 0

        @retry(max_attempts=3)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_eventual_success(self):
        """Test retry decorator with eventual success."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def eventual_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        result = eventual_success()
        assert result == "success"
        assert call_count == 3

    def test_retry_all_failures(self):
        """Test retry decorator when all attempts fail."""
        @retry(max_attempts=2, delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_timed_decorator(self):
        """Test timed decorator."""
        @timed
        def slow_func():
            time.sleep(0.1)
            return "done"

        result = slow_func()
        assert result == "done"

    def test_deprecated_decorator(self):
        """Test deprecated decorator."""
        @deprecated("Use new_func instead")
        def old_func():
            return "old"

        # Should still work
        result = old_func()
        assert result == "old"


class TestValidationUtilities:
    """Tests for validation utility functions."""

    def test_is_valid_email_valid(self):
        """Test valid email addresses."""
        assert is_valid_email("test@example.com")
        assert is_valid_email("user.name@domain.co.uk")
        assert is_valid_email("user+tag@example.org")

    def test_is_valid_email_invalid(self):
        """Test invalid email addresses."""
        assert not is_valid_email("invalid")
        assert not is_valid_email("@example.com")
        assert not is_valid_email("test@")
        assert not is_valid_email("test@.com")

    def test_is_valid_url_valid(self):
        """Test valid URLs."""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://example.com/path")
        assert is_valid_url("https://sub.example.com/path?query=1")

    def test_is_valid_url_invalid(self):
        """Test invalid URLs."""
        assert not is_valid_url("not a url")
        assert not is_valid_url("example.com")
        assert not is_valid_url("ftp://example.com")  # Only http/https
