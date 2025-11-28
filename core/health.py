"""
Health Check Module for B3PersonalAssistant

Provides comprehensive health checks for all system components:
- Database connectivity
- Ollama service availability
- System resources (CPU, memory, disk)
- Agent status
- Module dependencies
"""

import logging
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading

from core.constants import (
    DATABASE_DIR,
    CONVERSATIONS_DB_PATH,
    TASKS_DB_PATH,
    OLLAMA_HEALTH_TIMEOUT,
)

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a single component."""
    name: str
    status: HealthStatus
    message: str
    latency_ms: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    components: List[ComponentHealth]
    checked_at: datetime = field(default_factory=datetime.now)
    uptime_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "checked_at": self.checked_at.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                    "details": c.details,
                }
                for c in self.components
            ]
        }


class HealthChecker:
    """
    Comprehensive health checker for the B3PersonalAssistant system.

    Example:
        >>> checker = HealthChecker()
        >>> health = checker.check_all()
        >>> print(health.status)
        HealthStatus.HEALTHY
    """

    def __init__(self):
        self._start_time = time.time()
        self._last_check: Optional[SystemHealth] = None
        self._check_lock = threading.Lock()

    @property
    def uptime_seconds(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time

    def check_all(self, use_cache: bool = False, cache_ttl: float = 5.0) -> SystemHealth:
        """
        Run all health checks.

        Args:
            use_cache: Return cached result if available
            cache_ttl: Cache time-to-live in seconds

        Returns:
            SystemHealth with all component statuses
        """
        with self._check_lock:
            # Return cached result if valid
            if use_cache and self._last_check:
                age = (datetime.now() - self._last_check.checked_at).total_seconds()
                if age < cache_ttl:
                    return self._last_check

            components = []

            # Run all checks
            components.append(self.check_database())
            components.append(self.check_ollama())
            components.append(self.check_system_resources())
            components.append(self.check_dependencies())

            # Determine overall status
            statuses = [c.status for c in components]
            if HealthStatus.UNHEALTHY in statuses:
                overall_status = HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                overall_status = HealthStatus.DEGRADED
            elif HealthStatus.UNKNOWN in statuses:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY

            self._last_check = SystemHealth(
                status=overall_status,
                components=components,
                uptime_seconds=self.uptime_seconds
            )

            return self._last_check

    def check_database(self) -> ComponentHealth:
        """Check database connectivity."""
        start = time.time()
        try:
            db_path = Path(CONVERSATIONS_DB_PATH)

            if not db_path.parent.exists():
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Database directory does not exist",
                    latency_ms=(time.time() - start) * 1000
                )

            # Test connection
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            conn.close()

            latency = (time.time() - start) * 1000

            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message=f"SQLite {version} connected",
                latency_ms=latency,
                details={"sqlite_version": version, "path": str(db_path)}
            )

        except sqlite3.Error as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {e}",
                latency_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error: {e}",
                latency_ms=(time.time() - start) * 1000
            )

    def check_ollama(self) -> ComponentHealth:
        """Check Ollama service availability."""
        start = time.time()
        try:
            import ollama
            client = ollama.Client()

            # Try to list models
            models = client.list()
            model_count = len(models.get('models', []))
            model_names = [m.get('name', 'unknown') for m in models.get('models', [])]

            latency = (time.time() - start) * 1000

            if model_count == 0:
                return ComponentHealth(
                    name="ollama",
                    status=HealthStatus.DEGRADED,
                    message="Connected but no models available",
                    latency_ms=latency,
                    details={"model_count": 0}
                )

            return ComponentHealth(
                name="ollama",
                status=HealthStatus.HEALTHY,
                message=f"Connected with {model_count} models",
                latency_ms=latency,
                details={"model_count": model_count, "models": model_names[:5]}
            )

        except ImportError:
            return ComponentHealth(
                name="ollama",
                status=HealthStatus.UNHEALTHY,
                message="Ollama package not installed",
                latency_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ComponentHealth(
                name="ollama",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect: {e}",
                latency_ms=(time.time() - start) * 1000
            )

    def check_system_resources(self) -> ComponentHealth:
        """Check system resource availability."""
        start = time.time()
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }

            latency = (time.time() - start) * 1000

            # Determine status based on resource usage
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                return ComponentHealth(
                    name="system_resources",
                    status=HealthStatus.UNHEALTHY,
                    message="Critical resource usage",
                    latency_ms=latency,
                    details=details
                )
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                return ComponentHealth(
                    name="system_resources",
                    status=HealthStatus.DEGRADED,
                    message="High resource usage",
                    latency_ms=latency,
                    details=details
                )
            else:
                return ComponentHealth(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="Resources OK",
                    latency_ms=latency,
                    details=details
                )

        except ImportError:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message="psutil not installed",
                latency_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking resources: {e}",
                latency_ms=(time.time() - start) * 1000
            )

    def check_dependencies(self) -> ComponentHealth:
        """Check required Python dependencies."""
        start = time.time()

        required = {
            "ollama": "ollama",
            "pydantic": "pydantic",
            "PyQt6": "PyQt6.QtCore",
        }

        optional = {
            "moviepy": "moviepy.editor",
            "PIL": "PIL.Image",
            "psutil": "psutil",
        }

        missing_required = []
        missing_optional = []
        installed = []

        for name, import_path in required.items():
            try:
                __import__(import_path)
                installed.append(name)
            except ImportError:
                missing_required.append(name)

        for name, import_path in optional.items():
            try:
                __import__(import_path)
                installed.append(name)
            except ImportError:
                missing_optional.append(name)

        latency = (time.time() - start) * 1000
        details = {
            "installed": installed,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
        }

        if missing_required:
            return ComponentHealth(
                name="dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"Missing required: {', '.join(missing_required)}",
                latency_ms=latency,
                details=details
            )
        elif missing_optional:
            return ComponentHealth(
                name="dependencies",
                status=HealthStatus.DEGRADED,
                message=f"Missing optional: {', '.join(missing_optional)}",
                latency_ms=latency,
                details=details
            )
        else:
            return ComponentHealth(
                name="dependencies",
                status=HealthStatus.HEALTHY,
                message="All dependencies installed",
                latency_ms=latency,
                details=details
            )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def check_health(use_cache: bool = True) -> SystemHealth:
    """
    Convenience function to check system health.

    Args:
        use_cache: Use cached result if available

    Returns:
        SystemHealth status
    """
    return get_health_checker().check_all(use_cache=use_cache)


def is_healthy() -> bool:
    """
    Quick check if system is healthy.

    Returns:
        True if system is healthy
    """
    health = check_health(use_cache=True)
    return health.status == HealthStatus.HEALTHY


if __name__ == "__main__":
    import json

    print("Running health checks...")
    health = check_health(use_cache=False)

    print(f"\nOverall Status: {health.status.value.upper()}")
    print(f"Uptime: {health.uptime_seconds:.1f}s")
    print("\nComponent Status:")

    for component in health.components:
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.UNKNOWN: "❓",
        }[component.status]

        print(f"  {status_emoji} {component.name}: {component.message}")
        if component.latency_ms:
            print(f"     Latency: {component.latency_ms:.1f}ms")

    print("\nFull JSON:")
    print(json.dumps(health.to_dict(), indent=2))
