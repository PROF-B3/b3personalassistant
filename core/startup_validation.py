"""
Startup Validation Module for B3PersonalAssistant

Performs pre-flight checks to ensure all required dependencies, databases,
and resources are available before the application starts.
"""

import logging
import sqlite3
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from core.constants import (
    DATABASE_DIR,
    CONVERSATIONS_DB_PATH,
    TASKS_DB_PATH,
    ZETTELKASTEN_BASE_PATH,
    OLLAMA_HEALTH_TIMEOUT,
)


logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of a validation check."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    status: ValidationStatus
    message: str
    details: Optional[str] = None


class StartupValidator:
    """
    Performs startup validation checks for B3PersonalAssistant.

    Validates:
    - Required Python packages
    - Database availability
    - Directory structure
    - Ollama connectivity
    - System resources
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the startup validator.

        Args:
            base_path: Base path for the application (defaults to current directory)
        """
        self.base_path = base_path or Path.cwd()
        self.results: List[ValidationResult] = []
        self.logger = logging.getLogger("startup_validator")

    def run_all_checks(self) -> Tuple[bool, List[ValidationResult]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (all_passed, results)
        """
        self.results = []

        # Run all checks
        self._check_python_version()
        self._check_required_packages()
        self._check_directories()
        self._check_databases()
        self._check_ollama_connectivity()
        self._check_disk_space()

        # Determine overall status
        all_passed = all(
            r.status != ValidationStatus.FAILED
            for r in self.results
        )

        return all_passed, self.results

    def _check_python_version(self):
        """Check Python version is compatible."""
        major, minor = sys.version_info[:2]

        if major < 3 or (major == 3 and minor < 9):
            self.results.append(ValidationResult(
                name="Python Version",
                status=ValidationStatus.FAILED,
                message=f"Python 3.9+ required, found {major}.{minor}",
                details="Please upgrade Python to version 3.9 or higher."
            ))
        else:
            self.results.append(ValidationResult(
                name="Python Version",
                status=ValidationStatus.PASSED,
                message=f"Python {major}.{minor} detected"
            ))

    def _check_required_packages(self):
        """Check that required packages are installed."""
        required_packages = [
            ("ollama", "ollama"),
            ("pydantic", "pydantic"),
            ("sqlite3", None),  # Built-in
            ("PyQt6", "PyQt6.QtCore"),
        ]

        optional_packages = [
            ("moviepy", "moviepy.editor"),
            ("scenedetect", "scenedetect"),
            ("PIL", "PIL.Image"),
        ]

        # Check required packages
        missing_required = []
        for name, import_path in required_packages:
            if import_path is None:
                continue  # Built-in
            try:
                __import__(import_path)
            except ImportError:
                missing_required.append(name)

        if missing_required:
            self.results.append(ValidationResult(
                name="Required Packages",
                status=ValidationStatus.FAILED,
                message=f"Missing required packages: {', '.join(missing_required)}",
                details="Install missing packages with: pip install " + " ".join(missing_required)
            ))
        else:
            self.results.append(ValidationResult(
                name="Required Packages",
                status=ValidationStatus.PASSED,
                message="All required packages installed"
            ))

        # Check optional packages
        missing_optional = []
        for name, import_path in optional_packages:
            try:
                __import__(import_path)
            except ImportError:
                missing_optional.append(name)

        if missing_optional:
            self.results.append(ValidationResult(
                name="Optional Packages",
                status=ValidationStatus.WARNING,
                message=f"Missing optional packages: {', '.join(missing_optional)}",
                details="Some features may be limited. Install with: pip install " + " ".join(missing_optional)
            ))
        else:
            self.results.append(ValidationResult(
                name="Optional Packages",
                status=ValidationStatus.PASSED,
                message="All optional packages installed"
            ))

    def _check_directories(self):
        """Check that required directories exist or can be created."""
        required_dirs = [
            DATABASE_DIR,
            Path(ZETTELKASTEN_BASE_PATH),
            Path(ZETTELKASTEN_BASE_PATH) / "_metadata",
        ]

        missing_dirs = []
        created_dirs = []

        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(dir_path))
                except OSError as e:
                    missing_dirs.append(f"{dir_path}: {e}")

        if missing_dirs:
            self.results.append(ValidationResult(
                name="Directory Structure",
                status=ValidationStatus.FAILED,
                message=f"Cannot create directories: {', '.join(missing_dirs)}"
            ))
        elif created_dirs:
            self.results.append(ValidationResult(
                name="Directory Structure",
                status=ValidationStatus.PASSED,
                message=f"Created directories: {', '.join(created_dirs)}"
            ))
        else:
            self.results.append(ValidationResult(
                name="Directory Structure",
                status=ValidationStatus.PASSED,
                message="All required directories exist"
            ))

    def _check_databases(self):
        """Check database connectivity and schema."""
        db_paths = [
            ("Conversations DB", self.base_path / CONVERSATIONS_DB_PATH),
            ("Tasks DB", self.base_path / TASKS_DB_PATH),
        ]

        db_issues = []

        for name, db_path in db_paths:
            try:
                # Ensure parent directory exists
                db_path.parent.mkdir(parents=True, exist_ok=True)

                # Try to connect
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version()")
                conn.close()

            except sqlite3.Error as e:
                db_issues.append(f"{name}: {e}")

        if db_issues:
            self.results.append(ValidationResult(
                name="Database Connectivity",
                status=ValidationStatus.FAILED,
                message=f"Database issues: {'; '.join(db_issues)}"
            ))
        else:
            self.results.append(ValidationResult(
                name="Database Connectivity",
                status=ValidationStatus.PASSED,
                message="All databases accessible"
            ))

    def _check_ollama_connectivity(self):
        """Check if Ollama is running and accessible."""
        try:
            import ollama
            client = ollama.Client()

            # Try to list models with timeout
            models = client.list()
            model_names = [m.get('name', 'unknown') for m in models.get('models', [])]

            if model_names:
                self.results.append(ValidationResult(
                    name="Ollama Connectivity",
                    status=ValidationStatus.PASSED,
                    message=f"Connected. Available models: {', '.join(model_names[:3])}..."
                ))
            else:
                self.results.append(ValidationResult(
                    name="Ollama Connectivity",
                    status=ValidationStatus.WARNING,
                    message="Connected but no models found",
                    details="Install a model with: ollama pull llama3.2:3b"
                ))

        except ImportError:
            self.results.append(ValidationResult(
                name="Ollama Connectivity",
                status=ValidationStatus.WARNING,
                message="Ollama package not installed",
                details="Install with: pip install ollama"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                name="Ollama Connectivity",
                status=ValidationStatus.WARNING,
                message=f"Cannot connect to Ollama: {e}",
                details="Ensure Ollama is running with: ollama serve"
            ))

    def _check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil

            total, used, free = shutil.disk_usage(self.base_path)

            free_gb = free / (1024 ** 3)

            if free_gb < 1:
                self.results.append(ValidationResult(
                    name="Disk Space",
                    status=ValidationStatus.FAILED,
                    message=f"Only {free_gb:.1f}GB free disk space",
                    details="At least 1GB free space is recommended."
                ))
            elif free_gb < 5:
                self.results.append(ValidationResult(
                    name="Disk Space",
                    status=ValidationStatus.WARNING,
                    message=f"Low disk space: {free_gb:.1f}GB free",
                    details="Consider freeing up space for optimal performance."
                ))
            else:
                self.results.append(ValidationResult(
                    name="Disk Space",
                    status=ValidationStatus.PASSED,
                    message=f"{free_gb:.1f}GB free disk space"
                ))
        except OSError as e:
            self.results.append(ValidationResult(
                name="Disk Space",
                status=ValidationStatus.WARNING,
                message=f"Cannot check disk space: {e}"
            ))

    def print_report(self):
        """Print a formatted validation report."""
        print("\n" + "=" * 60)
        print("B3PersonalAssistant Startup Validation Report")
        print("=" * 60 + "\n")

        # Group by status
        passed = [r for r in self.results if r.status == ValidationStatus.PASSED]
        warnings = [r for r in self.results if r.status == ValidationStatus.WARNING]
        failed = [r for r in self.results if r.status == ValidationStatus.FAILED]

        # Print passed checks
        if passed:
            print("✅ PASSED:")
            for r in passed:
                print(f"   • {r.name}: {r.message}")
            print()

        # Print warnings
        if warnings:
            print("⚠️  WARNINGS:")
            for r in warnings:
                print(f"   • {r.name}: {r.message}")
                if r.details:
                    print(f"     → {r.details}")
            print()

        # Print failures
        if failed:
            print("❌ FAILED:")
            for r in failed:
                print(f"   • {r.name}: {r.message}")
                if r.details:
                    print(f"     → {r.details}")
            print()

        # Summary
        total = len(self.results)
        print("-" * 60)
        print(f"Summary: {len(passed)} passed, {len(warnings)} warnings, {len(failed)} failed")
        print("=" * 60 + "\n")

        return len(failed) == 0


def validate_startup(base_path: Optional[Path] = None, verbose: bool = True) -> bool:
    """
    Convenience function to run startup validation.

    Args:
        base_path: Base path for the application
        verbose: Whether to print the report

    Returns:
        True if all critical checks passed
    """
    validator = StartupValidator(base_path)
    all_passed, results = validator.run_all_checks()

    if verbose:
        validator.print_report()

    return all_passed


if __name__ == "__main__":
    # Run validation when executed directly
    success = validate_startup()
    sys.exit(0 if success else 1)
