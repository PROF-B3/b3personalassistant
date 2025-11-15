#!/usr/bin/env python3
"""
Test script to check if all B3PersonalAssistant modules can be imported.
"""

import sys
from pathlib import Path

def test_import(module_name, description):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: FAILED - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: ERROR - {e}")
        return False

def main():
    print("Testing B3PersonalAssistant imports...")
    print("=" * 50)
    
    # Test core modules
    core_tests = [
        ("core.orchestrator", "Orchestrator"),
        ("core.agents", "Agents"),
        ("core.config", "Configuration"),
    ]
    
    # Test functional modules
    module_tests = [
        ("modules.conversation", "Conversation Manager"),
        ("modules.knowledge", "Knowledge Manager"),
        ("modules.tasks", "Task Manager"),
        ("modules.resources", "Resource Monitor"),
        ("modules.video_processing", "Video Processing"),
    ]
    
    # Test external dependencies
    dependency_tests = [
        ("ollama", "Ollama"),
        ("autogen", "AutoGen"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("rich", "Rich"),
        ("loguru", "Loguru"),
    ]
    
    print("\nCore Modules:")
    core_results = [test_import(module, desc) for module, desc in core_tests]
    
    print("\nFunctional Modules:")
    module_results = [test_import(module, desc) for module, desc in module_tests]
    
    print("\nDependencies:")
    dep_results = [test_import(module, desc) for module, desc in dependency_tests]
    
    # Summary
    print("\n" + "=" * 50)
    total_tests = len(core_results) + len(module_results) + len(dep_results)
    passed_tests = sum(core_results) + sum(module_results) + sum(dep_results)
    
    print(f"Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All imports successful!")
    else:
        print("⚠️  Some imports failed. Check the errors above.")

if __name__ == "__main__":
    main() 