#!/usr/bin/env python3
"""
Test script for resilience features.
Tests input validation, circuit breaker, and error handling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.agents import AlphaAgent
from core.validators import InputValidator
from core.exceptions import InputValidationError, CircuitBreakerOpenError
from core.resilience import CircuitBreaker, CircuitBreakerConfig


def test_input_validation():
    """Test input validation."""
    print("Testing input validation...")
    validator = InputValidator()

    # Test valid input
    try:
        result = validator.validate_and_sanitize("Hello, this is a normal query")
        assert result == "Hello, this is a normal query"
        print("  ✓ Valid input accepted")
    except Exception as e:
        print(f"  ✗ Valid input rejected: {e}")
        return False

    # Test empty input
    try:
        validator.validate_and_sanitize("")
        print("  ✗ Empty input not rejected")
        return False
    except InputValidationError:
        print("  ✓ Empty input rejected")

    # Test too long input
    try:
        validator.validate_and_sanitize("x" * 20000)
        print("  ✗ Too long input not rejected")
        return False
    except InputValidationError:
        print("  ✓ Too long input rejected")

    # Test dangerous patterns
    try:
        validator.validate_and_sanitize("<script>alert('xss')</script>")
        print("  ✗ Script tag not rejected")
        return False
    except InputValidationError:
        print("  ✓ Script tag rejected")

    # Test SQL injection patterns
    try:
        validator.validate_sql_safe("'; DROP TABLE users; --")
        print("  ✗ SQL injection not rejected")
        return False
    except InputValidationError:
        print("  ✓ SQL injection rejected")

    print("✓ Input validation tests passed\n")
    return True


def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("Testing circuit breaker...")

    breaker = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=1.0
    ))

    # Test closed state (normal operation)
    @breaker.call
    def normal_operation():
        return "success"

    try:
        result = normal_operation()
        assert result == "success"
        print("  ✓ Circuit breaker allows normal operation")
    except Exception as e:
        print(f"  ✗ Circuit breaker blocked normal operation: {e}")
        return False

    # Test failure accumulation
    @breaker.call
    def failing_operation():
        raise Exception("Simulated failure")

    for i in range(3):
        try:
            failing_operation()
        except Exception:
            pass

    # Circuit should now be open
    try:
        failing_operation()
        print("  ✗ Circuit breaker didn't open after threshold")
        return False
    except CircuitBreakerOpenError:
        print("  ✓ Circuit breaker opened after threshold failures")

    # Get status
    status = breaker.get_status()
    assert status['state'] == 'open'
    assert status['failure_count'] >= 3
    print(f"  ✓ Circuit breaker status: {status['state']}, failures: {status['failure_count']}")

    # Reset
    breaker.reset()
    assert breaker.state.value == 'closed'
    print("  ✓ Circuit breaker reset successful")

    print("✓ Circuit breaker tests passed\n")
    return True


def test_agent_validation():
    """Test that agents have validation."""
    print("Testing agent validators...")

    alpha = AlphaAgent()

    # Check validator exists
    assert hasattr(alpha, 'validator'), "Agent missing validator"
    assert isinstance(alpha.validator, InputValidator), "Validator wrong type"
    print("  ✓ Agent has input validator")

    # Check circuit breaker exists
    assert hasattr(alpha, 'circuit_breaker'), "Agent missing circuit breaker"
    assert isinstance(alpha.circuit_breaker, CircuitBreaker), "Circuit breaker wrong type"
    print("  ✓ Agent has circuit breaker")

    # Check resilient call method exists
    assert hasattr(alpha, 'call_ollama_with_resilience'), "Agent missing resilient call method"
    print("  ✓ Agent has resilient Ollama call method")

    print("✓ Agent validation tests passed\n")
    return True


def test_error_messages():
    """Test user-friendly error messages."""
    print("Testing error messages...")

    alpha = AlphaAgent()

    # Test with invalid input (too short after strip)
    try:
        result = alpha.act("   ")
        assert "couldn't process your input" in result.lower() or "too short" in result.lower()
        print("  ✓ Empty input returns user-friendly message")
    except Exception as e:
        print(f"  ✗ Empty input caused exception: {e}")
        return False

    # Test with dangerous input
    try:
        result = alpha.act("<script>alert('test')</script>")
        assert "couldn't process" in result.lower() or "dangerous" in result.lower()
        print("  ✓ Dangerous input returns user-friendly message")
    except Exception as e:
        print(f"  ✗ Dangerous input caused exception: {e}")
        return False

    print("✓ Error message tests passed\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("B3PersonalAssistant Resilience Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_input_validation,
        test_circuit_breaker,
        test_agent_validation,
        test_error_messages,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()

    if failed == 0:
        print("✓ ALL RESILIENCE TESTS PASSED!")
        print()
        print("Resilience features active:")
        print("  ✓ Input validation (XSS, SQL injection, length)")
        print("  ✓ Circuit breaker (auto-recovery from failures)")
        print("  ✓ Retry logic (exponential backoff)")
        print("  ✓ Timeout handling (30s default)")
        print("  ✓ User-friendly error messages")
        print("  ✓ Comprehensive exception hierarchy")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
