"""
Health Monitoring System for B3PersonalAssistant

Provides health checks for various system components including databases,
external services, file system, and resource usage.
"""

import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable
import requests

from core.constants import (
    CONVERSATIONS_DB,
    TASKS_DB,
    KNOWLEDGE_DB,
    OLLAMA_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    details: Optional[Dict] = None
    timestamp: Optional[datetime] = None
    response_time_ms: Optional[float] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details or {},
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
        }


class HealthMonitor:
    """
    Monitors the health of various system components.

    Example:
        >>> monitor = HealthMonitor()
        >>> results = monitor.check_all()
        >>> if monitor.is_healthy():
        ...     print("System healthy")
        >>> else:
        ...     print(f"Issues: {monitor.get_unhealthy_components()}")
    """

    def __init__(self):
        """Initialize health monitor."""
        self.checks: Dict[str, Callable] = {
            "database_conversations": self.check_database_conversations,
            "database_tasks": self.check_database_tasks,
            "database_knowledge": self.check_database_knowledge,
            "ollama_service": self.check_ollama_service,
            "file_system": self.check_file_system,
            "memory": self.check_memory_usage,
        }
        self.last_results: Dict[str, HealthCheckResult] = {}

    def check_database_conversations(self) -> HealthCheckResult:
        """
        Check conversations database health.

        Returns:
            HealthCheckResult with database status
        """
        start_time = time.perf_counter()

        try:
            db_path = Path(CONVERSATIONS_DB)

            # Check if database file exists
            if not db_path.exists():
                return HealthCheckResult(
                    component="database_conversations",
                    status=HealthStatus.UNHEALTHY,
                    message="Database file does not exist",
                    details={"path": str(db_path)},
                )

            # Try to connect and query
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]

                response_time_ms = (time.perf_counter() - start_time) * 1000

                return HealthCheckResult(
                    component="database_conversations",
                    status=HealthStatus.HEALTHY,
                    message="Database operational",
                    details={
                        "path": str(db_path),
                        "table_count": table_count,
                        "size_mb": db_path.stat().st_size / (1024 * 1024),
                    },
                    response_time_ms=response_time_ms,
                )

        except sqlite3.Error as e:
            return HealthCheckResult(
                component="database_conversations",
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {e}",
                details={"error": str(e)},
            )
        except Exception as e:
            return HealthCheckResult(
                component="database_conversations",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error: {e}",
                details={"error": str(e)},
            )

    def check_database_tasks(self) -> HealthCheckResult:
        """Check tasks database health."""
        return self._check_database(TASKS_DB, "database_tasks")

    def check_database_knowledge(self) -> HealthCheckResult:
        """Check knowledge database health."""
        return self._check_database(KNOWLEDGE_DB, "database_knowledge")

    def _check_database(self, db_path_str: str, component_name: str) -> HealthCheckResult:
        """
        Generic database health check.

        Args:
            db_path_str: Path to database file
            component_name: Name of the component

        Returns:
            HealthCheckResult
        """
        start_time = time.perf_counter()

        try:
            db_path = Path(db_path_str)

            if not db_path.exists():
                return HealthCheckResult(
                    component=component_name,
                    status=HealthStatus.DEGRADED,
                    message="Database file does not exist (may not be initialized)",
                    details={"path": str(db_path)},
                )

            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]

                response_time_ms = (time.perf_counter() - start_time) * 1000

                return HealthCheckResult(
                    component=component_name,
                    status=HealthStatus.HEALTHY,
                    message="Database operational",
                    details={
                        "path": str(db_path),
                        "table_count": table_count,
                        "size_mb": round(db_path.stat().st_size / (1024 * 1024), 2),
                    },
                    response_time_ms=response_time_ms,
                )

        except Exception as e:
            return HealthCheckResult(
                component=component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {e}",
                details={"error": str(e)},
            )

    def check_ollama_service(self) -> HealthCheckResult:
        """
        Check Ollama service availability.

        Returns:
            HealthCheckResult with Ollama status
        """
        start_time = time.perf_counter()

        try:
            # Try to connect to Ollama API
            response = requests.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=DEFAULT_TIMEOUT_SECONDS
            )

            response_time_ms = (time.perf_counter() - start_time) * 1000

            if response.status_code == 200:
                models = response.json().get("models", [])
                return HealthCheckResult(
                    component="ollama_service",
                    status=HealthStatus.HEALTHY,
                    message="Ollama service available",
                    details={
                        "url": OLLAMA_BASE_URL,
                        "model_count": len(models),
                        "models": [m.get("name") for m in models[:5]],  # First 5 models
                    },
                    response_time_ms=response_time_ms,
                )
            else:
                return HealthCheckResult(
                    component="ollama_service",
                    status=HealthStatus.DEGRADED,
                    message=f"Ollama returned status {response.status_code}",
                    details={"status_code": response.status_code},
                    response_time_ms=response_time_ms,
                )

        except requests.ConnectionError:
            return HealthCheckResult(
                component="ollama_service",
                status=HealthStatus.UNHEALTHY,
                message="Cannot connect to Ollama service",
                details={"url": OLLAMA_BASE_URL},
            )
        except requests.Timeout:
            return HealthCheckResult(
                component="ollama_service",
                status=HealthStatus.DEGRADED,
                message="Ollama service timeout",
                details={"url": OLLAMA_BASE_URL, "timeout": DEFAULT_TIMEOUT_SECONDS},
            )
        except Exception as e:
            return HealthCheckResult(
                component="ollama_service",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error: {e}",
                details={"error": str(e)},
            )

    def check_file_system(self) -> HealthCheckResult:
        """
        Check file system health and accessibility.

        Returns:
            HealthCheckResult with file system status
        """
        start_time = time.perf_counter()

        try:
            # Check database directory
            db_dir = Path("databases")
            db_dir_exists = db_dir.exists()
            db_dir_writable = db_dir.is_dir() and db_dir.stat().st_mode & 0o200

            # Check logs directory
            logs_dir = Path("logs")
            logs_dir_exists = logs_dir.exists() or logs_dir.parent.exists()

            # Check knowledge base directory
            kb_dir = Path("knowledge_base")
            kb_dir_exists = kb_dir.exists()

            response_time_ms = (time.perf_counter() - start_time) * 1000

            issues = []
            if not db_dir_exists:
                issues.append("Database directory does not exist")
            if not db_dir_writable:
                issues.append("Database directory not writable")
            if not logs_dir_exists:
                issues.append("Logs directory not accessible")

            if issues:
                status = HealthStatus.DEGRADED if db_dir_exists else HealthStatus.UNHEALTHY
                return HealthCheckResult(
                    component="file_system",
                    status=status,
                    message="; ".join(issues),
                    details={
                        "database_dir_exists": db_dir_exists,
                        "database_dir_writable": db_dir_writable,
                        "logs_dir_exists": logs_dir_exists,
                        "knowledge_base_dir_exists": kb_dir_exists,
                    },
                    response_time_ms=response_time_ms,
                )

            return HealthCheckResult(
                component="file_system",
                status=HealthStatus.HEALTHY,
                message="File system accessible",
                details={
                    "database_dir": str(db_dir.resolve()),
                    "logs_dir": str(logs_dir.parent.resolve()),
                    "knowledge_base_dir": str(kb_dir.resolve()) if kb_dir_exists else "not created",
                },
                response_time_ms=response_time_ms,
            )

        except Exception as e:
            return HealthCheckResult(
                component="file_system",
                status=HealthStatus.UNKNOWN,
                message=f"File system check failed: {e}",
                details={"error": str(e)},
            )

    def check_memory_usage(self) -> HealthCheckResult:
        """
        Check system memory usage.

        Returns:
            HealthCheckResult with memory status
        """
        start_time = time.perf_counter()

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            # Get system memory
            system_memory = psutil.virtual_memory()

            # Memory in MB
            process_memory_mb = memory_info.rss / (1024 * 1024)
            system_total_mb = system_memory.total / (1024 * 1024)
            system_available_mb = system_memory.available / (1024 * 1024)
            system_percent = system_memory.percent

            response_time_ms = (time.perf_counter() - start_time) * 1000

            # Determine status based on usage
            if system_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical memory usage"
            elif system_percent > 80:
                status = HealthStatus.DEGRADED
                message = "High memory usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Memory usage normal"

            return HealthCheckResult(
                component="memory",
                status=status,
                message=message,
                details={
                    "process_memory_mb": round(process_memory_mb, 2),
                    "system_total_mb": round(system_total_mb, 2),
                    "system_available_mb": round(system_available_mb, 2),
                    "system_percent": round(system_percent, 1),
                },
                response_time_ms=response_time_ms,
            )

        except ImportError:
            return HealthCheckResult(
                component="memory",
                status=HealthStatus.UNKNOWN,
                message="psutil not installed, cannot check memory",
                details={"note": "Install psutil for memory monitoring"},
            )
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {e}",
                details={"error": str(e)},
            )

    def check_all(self) -> Dict[str, HealthCheckResult]:
        """
        Run all health checks.

        Returns:
            Dictionary of component names to HealthCheckResult
        """
        logger.info("Running all health checks")

        results = {}
        for component_name, check_func in self.checks.items():
            try:
                result = check_func()
                results[component_name] = result
                self.last_results[component_name] = result

                logger.debug(
                    f"Health check: {component_name} = {result.status.value}",
                    extra={
                        "component": component_name,
                        "status": result.status.value,
                        "response_time_ms": result.response_time_ms,
                    }
                )

            except Exception as e:
                logger.error(f"Health check failed for {component_name}: {e}", exc_info=True)
                result = HealthCheckResult(
                    component=component_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {e}",
                    details={"error": str(e)},
                )
                results[component_name] = result
                self.last_results[component_name] = result

        return results

    def is_healthy(self) -> bool:
        """
        Check if all components are healthy.

        Returns:
            True if all components are healthy, False otherwise
        """
        if not self.last_results:
            self.check_all()

        return all(
            result.status == HealthStatus.HEALTHY
            for result in self.last_results.values()
        )

    def get_unhealthy_components(self) -> List[str]:
        """
        Get list of unhealthy component names.

        Returns:
            List of component names that are unhealthy
        """
        if not self.last_results:
            self.check_all()

        return [
            name
            for name, result in self.last_results.items()
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]
        ]

    def get_status_summary(self) -> Dict:
        """
        Get overall health status summary.

        Returns:
            Dictionary with status summary
        """
        if not self.last_results:
            self.check_all()

        total = len(self.last_results)
        healthy = sum(1 for r in self.last_results.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in self.last_results.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in self.last_results.values() if r.status == HealthStatus.UNHEALTHY)
        unknown = sum(1 for r in self.last_results.values() if r.status == HealthStatus.UNKNOWN)

        # Overall status
        if unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        elif unknown > total // 2:  # More than half unknown
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "overall_status": overall_status.value,
            "total_components": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "unknown": unknown,
            "timestamp": datetime.now().isoformat(),
        }

    def print_report(self):
        """Print a formatted health check report to console."""
        if not self.last_results:
            self.check_all()

        print("\n" + "=" * 80)
        print("B3PersonalAssistant Health Check Report")
        print("=" * 80)

        # Overall summary
        summary = self.get_status_summary()
        status_symbol = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓",
        }

        print(f"\nOverall Status: {status_symbol.get(summary['overall_status'], '❓')} {summary['overall_status'].upper()}")
        print(f"Components: {summary['healthy']} healthy, {summary['degraded']} degraded, {summary['unhealthy']} unhealthy")
        print("\nComponent Details:")
        print("-" * 80)

        # Individual components
        for name, result in sorted(self.last_results.items()):
            symbol = status_symbol.get(result.status.value, "❓")
            print(f"\n{symbol} {name}:")
            print(f"   Status: {result.status.value}")
            print(f"   Message: {result.message}")

            if result.response_time_ms:
                print(f"   Response Time: {result.response_time_ms:.2f}ms")

            if result.details:
                print("   Details:")
                for key, value in result.details.items():
                    print(f"     - {key}: {value}")

        print("\n" + "=" * 80 + "\n")


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    monitor = HealthMonitor()
    monitor.print_report()

    if monitor.is_healthy():
        print("✅ System is healthy!")
    else:
        print(f"⚠️  Issues detected in: {', '.join(monitor.get_unhealthy_components())}")
