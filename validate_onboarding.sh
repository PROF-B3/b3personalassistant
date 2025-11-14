#!/bin/bash

# Onboarding System Validation Script
# Quick validation of all onboarding components

echo "=========================================="
echo "  B3 Onboarding System Validation"
echo "=========================================="
echo

PASS=0
FAIL=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Test: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo "✓ PASS"
        ((PASS++))
    else
        echo "✗ FAIL"
        ((FAIL++))
    fi
}

# Test 1: Core module imports
run_test "Core module imports" \
    "python3 -c 'from modules.onboarding import OnboardingManager; from modules.sample_data import SampleDataGenerator'"

# Test 2: Tutorial loading
run_test "Tutorial loading (7 tutorials)" \
    "python3 -c 'from modules.onboarding import get_all_tutorials; assert len(get_all_tutorials()) == 7'"

# Test 3: OnboardingManager creation
run_test "OnboardingManager instantiation" \
    "python3 -c 'from modules.onboarding import OnboardingManager; mgr = OnboardingManager(); assert hasattr(mgr, \"is_first_run\")'"

# Test 4: UserPreferences
run_test "UserPreferences dataclass" \
    "python3 -c 'from modules.onboarding import UserPreferences; prefs = UserPreferences(); assert prefs.default_citation_style == \"APA\"'"

# Test 5: Sample data generator
run_test "SampleDataGenerator creation" \
    "python3 -c 'from modules.sample_data import SampleDataGenerator; gen = SampleDataGenerator()'"

# Test 6: Lazy imports (interfaces)
run_test "Lazy imports (interfaces)" \
    "python3 -c 'import interfaces; import interfaces.desktop_app'"

# Test 7: Tutorial structure validation
run_test "Tutorial structure validation" \
    "python3 -c 'from modules.onboarding import get_tutorial; t = get_tutorial(\"basic_navigation\"); assert t is not None and \"steps\" in t'"

# Test 8: Workspace creation
run_test "Workspace creation logic" \
    "python3 -c 'from modules.onboarding import OnboardingManager; from pathlib import Path; import tempfile; mgr = OnboardingManager(); w_str = mgr.create_default_workspace(); w = Path(w_str); assert w.exists()'"

# Test 9: Preferences to dict
run_test "Preferences serialization" \
    "python3 -c 'from modules.onboarding import UserPreferences; prefs = UserPreferences(name=\"Test\"); d = prefs.to_dict(); assert d[\"name\"] == \"Test\"'"

# Test 10: Helper functions
run_test "Helper functions exist" \
    "python3 -c 'from modules.sample_data import generate_sample_data_for_onboarding; from modules.onboarding import get_all_tutorials, get_tutorial'"

echo
echo "=========================================="
echo "  Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Total:  $((PASS + FAIL))"
echo

if [ $FAIL -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
