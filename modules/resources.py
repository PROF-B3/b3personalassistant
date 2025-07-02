"""
System Resource Monitoring Module

This module monitors system resources including CPU, memory, disk usage,
and provides system health information for the B3PersonalAssistant.
"""

import psutil
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import threading
import requests


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int  # bytes
    memory_total: int  # bytes
    disk_percent: float
    disk_free: int  # bytes
    disk_total: int  # bytes
    network_sent: int  # bytes
    network_recv: int  # bytes
    load_average: Optional[float] = None


@dataclass
class ProcessInfo:
    """Information about a specific process"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int  # bytes
    status: str
    create_time: float


OLLAMA_DEFAULT_URL = "http://localhost:11434"
OLLAMA_STATUS_ENDPOINT = "/api/tags"
OLLAMA_TIMEOUT = 2

DATABASE_PATHS = [
    "databases/conversations.db",
    "databases/tasks.db",
    "X/_metadata/zettelkasten.db"
]

class PerformanceTracker:
    """Tracks agent performance and response times."""
    def __init__(self):
        self.agent_stats = {}
        self.lock = threading.Lock()

    def record(self, agent_name, response_time, success=True):
        with self.lock:
            stats = self.agent_stats.setdefault(agent_name, {
                'calls': 0, 'errors': 0, 'total_time': 0.0, 'max_time': 0.0, 'min_time': float('inf')
            })
            stats['calls'] += 1
            if not success:
                stats['errors'] += 1
            stats['total_time'] += response_time
            stats['max_time'] = max(stats['max_time'], response_time)
            stats['min_time'] = min(stats['min_time'], response_time)

    def get_stats(self, agent_name):
        with self.lock:
            stats = self.agent_stats.get(agent_name, None)
            if not stats or stats['calls'] == 0:
                return None
            return {
                'calls': stats['calls'],
                'errors': stats['errors'],
                'avg_time': stats['total_time'] / stats['calls'],
                'max_time': stats['max_time'],
                'min_time': stats['min_time'] if stats['min_time'] != float('inf') else 0.0
            }

    def get_all_stats(self):
        with self.lock:
            return {k: self.get_stats(k) for k in self.agent_stats}

class ResourceMonitor:
    """Monitors system resources and provides health information"""
    
    def __init__(self, storage_path: Path, history_size: int = 1000, ollama_url: str = OLLAMA_DEFAULT_URL):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("resource_monitor")
        self.history_size = history_size
        
        # Metrics history
        self.metrics_history: List[SystemMetrics] = []
        self.process_history: Dict[int, List[ProcessInfo]] = {}
        
        # Performance thresholds
        self.thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0
        }
        
        # Initialize baseline metrics
        self._initialize_baseline()
        self.ollama_url = ollama_url
        self.performance = PerformanceTracker()
        self.alerts = []
        self.last_alert_time = None
        self.throttle_active = False
        self.throttle_reason = None
        self.alert_thresholds = {
            'cpu': 90.0,
            'memory': 95.0,
            'disk': 95.0
        }
        self.throttle_thresholds = {
            'cpu': 98.0,
            'memory': 98.0
        }
        self.status_callbacks = []  # For GUI/CLI real-time updates
    
    def _initialize_baseline(self):
        """Initialize baseline system metrics"""
        try:
            # Get initial system info
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.logger.info(f"System initialized - CPU cores: {cpu_count}, "
                           f"Memory: {memory.total / (1024**3):.1f}GB, "
                           f"Disk: {disk.total / (1024**3):.1f}GB")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize baseline metrics: {e}")
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk (monitor root directory)
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Load average (Unix-like systems)
            load_avg = None
            try:
                load_avg = psutil.getloadavg()[0]  # 1-minute load average
            except AttributeError:
                # Windows doesn't have load average
                pass
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available,
                memory_total=memory.total,
                disk_percent=disk.percent,
                disk_free=disk.free,
                disk_total=disk.total,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                load_average=load_avg
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            
            # Maintain history size
            if len(self.metrics_history) > self.history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get current metrics: {e}")
            # Return empty metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available=0,
                memory_total=0,
                disk_percent=0.0,
                disk_free=0,
                disk_total=0,
                network_sent=0,
                network_recv=0
            )
    
    def get_process_info(self, pid: Optional[int] = None) -> List[ProcessInfo]:
        """Get information about running processes"""
        try:
            processes = []
            
            if pid:
                # Get specific process
                try:
                    proc = psutil.Process(pid)
                    processes.append(self._get_process_info(proc))
                except psutil.NoSuchProcess:
                    self.logger.warning(f"Process {pid} not found")
            else:
                # Get all processes
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time']):
                    try:
                        processes.append(self._get_process_info(proc))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to get process info: {e}")
            return []
    
    def _get_process_info(self, proc) -> ProcessInfo:
        """Extract process information from psutil process object"""
        try:
            with proc.oneshot():
                return ProcessInfo(
                    pid=proc.pid,
                    name=proc.name(),
                    cpu_percent=proc.cpu_percent(),
                    memory_percent=proc.memory_percent(),
                    memory_rss=proc.memory_info().rss,
                    status=proc.status(),
                    create_time=proc.create_time()
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            raise
    
    def get_top_processes(self, n: int = 10, sort_by: str = "cpu") -> List[ProcessInfo]:
        """Get top processes by CPU or memory usage"""
        processes = self.get_process_info()
        
        if sort_by == "cpu":
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        elif sort_by == "memory_rss":
            processes.sort(key=lambda p: p.memory_rss, reverse=True)
        
        return processes[:n]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        metrics = self.get_current_metrics()
        
        health_status = {
            "timestamp": metrics.timestamp.isoformat(),
            "overall_status": "healthy",
            "warnings": [],
            "critical_alerts": [],
            "metrics": {
                "cpu": {
                    "percent": metrics.cpu_percent,
                    "status": self._get_metric_status(metrics.cpu_percent, "cpu")
                },
                "memory": {
                    "percent": metrics.memory_percent,
                    "available_gb": metrics.memory_available / (1024**3),
                    "total_gb": metrics.memory_total / (1024**3),
                    "status": self._get_metric_status(metrics.memory_percent, "memory")
                },
                "disk": {
                    "percent": metrics.disk_percent,
                    "free_gb": metrics.disk_free / (1024**3),
                    "total_gb": metrics.disk_total / (1024**3),
                    "status": self._get_metric_status(metrics.disk_percent, "disk")
                },
                "network": {
                    "sent_mb": metrics.network_sent / (1024**2),
                    "recv_mb": metrics.network_recv / (1024**2)
                }
            }
        }
        
        # Check for warnings and critical alerts
        if metrics.cpu_percent >= self.thresholds["cpu_critical"]:
            health_status["critical_alerts"].append(f"CPU usage critical: {metrics.cpu_percent:.1f}%")
            health_status["overall_status"] = "critical"
        elif metrics.cpu_percent >= self.thresholds["cpu_warning"]:
            health_status["warnings"].append(f"CPU usage high: {metrics.cpu_percent:.1f}%")
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "warning"
        
        if metrics.memory_percent >= self.thresholds["memory_critical"]:
            health_status["critical_alerts"].append(f"Memory usage critical: {metrics.memory_percent:.1f}%")
            health_status["overall_status"] = "critical"
        elif metrics.memory_percent >= self.thresholds["memory_warning"]:
            health_status["warnings"].append(f"Memory usage high: {metrics.memory_percent:.1f}%")
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "warning"
        
        if metrics.disk_percent >= self.thresholds["disk_critical"]:
            health_status["critical_alerts"].append(f"Disk usage critical: {metrics.disk_percent:.1f}%")
            health_status["overall_status"] = "critical"
        elif metrics.disk_percent >= self.thresholds["disk_warning"]:
            health_status["warnings"].append(f"Disk usage high: {metrics.disk_percent:.1f}%")
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "warning"
        
        return health_status
    
    def _get_metric_status(self, value: float, metric_type: str) -> str:
        """Get status for a specific metric"""
        if metric_type == "cpu":
            if value >= self.thresholds["cpu_critical"]:
                return "critical"
            elif value >= self.thresholds["cpu_warning"]:
                return "warning"
        elif metric_type == "memory":
            if value >= self.thresholds["memory_critical"]:
                return "critical"
            elif value >= self.thresholds["memory_warning"]:
                return "warning"
        elif metric_type == "disk":
            if value >= self.thresholds["disk_critical"]:
                return "critical"
            elif value >= self.thresholds["disk_warning"]:
                return "warning"
        
        return "healthy"
    
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """Get average metrics over the specified time period"""
        history = self.get_metrics_history(hours)
        
        if not history:
            return {}
        
        return {
            "cpu_percent": sum(m.cpu_percent for m in history) / len(history),
            "memory_percent": sum(m.memory_percent for m in history) / len(history),
            "disk_percent": sum(m.disk_percent for m in history) / len(history),
            "network_sent_mb": sum(m.network_sent for m in history) / (1024**2 * len(history)),
            "network_recv_mb": sum(m.network_recv for m in history) / (1024**2 * len(history))
        }
    
    def save_metrics_snapshot(self) -> bool:
        """Save current metrics to disk"""
        try:
            metrics = self.get_current_metrics()
            health = self.get_system_health()
            
            snapshot = {
                "timestamp": metrics.timestamp.isoformat(),
                "metrics": {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "memory_available_gb": metrics.memory_available / (1024**3),
                    "memory_total_gb": metrics.memory_total / (1024**3),
                    "disk_percent": metrics.disk_percent,
                    "disk_free_gb": metrics.disk_free / (1024**3),
                    "disk_total_gb": metrics.disk_total / (1024**3),
                    "network_sent_mb": metrics.network_sent / (1024**2),
                    "network_recv_mb": metrics.network_recv / (1024**2),
                    "load_average": metrics.load_average
                },
                "health": health,
                "top_processes": [
                    {
                        "pid": p.pid,
                        "name": p.name,
                        "cpu_percent": p.cpu_percent,
                        "memory_percent": p.memory_percent,
                        "memory_rss_mb": p.memory_rss / (1024**2)
                    }
                    for p in self.get_top_processes(5, "cpu")
                ]
            }
            
            timestamp_str = metrics.timestamp.strftime("%Y%m%d_%H%M%S")
            file_path = self.storage_path / f"snapshot_{timestamp_str}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved metrics snapshot to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save metrics snapshot: {e}")
            return False
    
    def set_thresholds(self, **kwargs) -> None:
        """Update monitoring thresholds"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                self.logger.info(f"Updated threshold {key}: {value}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            return {
                "platform": psutil.sys.platform,
                "python_version": psutil.sys.version,
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "disk_partitions": [
                    {
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "total_gb": psutil.disk_usage(p.mountpoint).total / (1024**3) if p.mountpoint else 0
                    }
                    for p in psutil.disk_partitions()
                ],
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}

    def monitor_ollama_status(self):
        """Check Ollama model status via API."""
        try:
            resp = requests.get(self.ollama_url + OLLAMA_STATUS_ENDPOINT, timeout=OLLAMA_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                return {'status': 'online', 'models': data.get('models', [])}
            return {'status': 'unreachable', 'models': []}
        except Exception:
            return {'status': 'offline', 'models': []}

    def get_database_sizes(self):
        """Return dict of database file sizes in MB."""
        sizes = {}
        for db in DATABASE_PATHS:
            p = Path(db)
            if p.exists():
                sizes[db] = round(p.stat().st_size / (1024*1024), 2)
            else:
                sizes[db] = 0.0
        return sizes

    def record_agent_response(self, agent_name, response_time, success=True):
        self.performance.record(agent_name, response_time, success)

    def get_agent_performance(self):
        return self.performance.get_all_stats()

    def check_alerts_and_throttle(self, metrics: SystemMetrics):
        alerts = []
        throttle = False
        reason = None
        if metrics.cpu_percent >= self.alert_thresholds['cpu']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        if metrics.memory_percent >= self.alert_thresholds['memory']:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        if metrics.disk_percent >= self.alert_thresholds['disk']:
            alerts.append(f"High disk usage: {metrics.disk_percent:.1f}%")
        if metrics.cpu_percent >= self.throttle_thresholds['cpu']:
            throttle = True
            reason = 'CPU'
        if metrics.memory_percent >= self.throttle_thresholds['memory']:
            throttle = True
            reason = 'Memory'
        self.alerts = alerts
        self.throttle_active = throttle
        self.throttle_reason = reason
        self.last_alert_time = datetime.now() if alerts else self.last_alert_time
        return alerts, throttle, reason

    def get_status_dashboard(self) -> Dict[str, Any]:
        metrics = self.get_current_metrics()
        ollama = self.monitor_ollama_status()
        db_sizes = self.get_database_sizes()
        agent_perf = self.get_agent_performance()
        alerts, throttle, reason = self.check_alerts_and_throttle(metrics)
        return {
            'timestamp': metrics.timestamp.isoformat(),
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'disk_percent': metrics.disk_percent,
            'ollama_status': ollama,
            'db_sizes': db_sizes,
            'agent_performance': agent_perf,
            'alerts': alerts,
            'throttle': throttle,
            'throttle_reason': reason
        }

    def register_status_callback(self, callback):
        """Register a callback for real-time status updates (GUI/CLI)."""
        self.status_callbacks.append(callback)

    def notify_status(self):
        status = self.get_status_dashboard()
        for cb in self.status_callbacks:
            try:
                cb(status)
            except Exception as e:
                self.logger.error(f"Status callback error: {e}")

    def log_performance(self, log_path: str = "performance.log"):
        """Log agent performance and alerts to a file."""
        with open(log_path, 'a') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'agent_performance': self.get_agent_performance(),
                'alerts': self.alerts,
                'throttle': self.throttle_active,
                'throttle_reason': self.throttle_reason
            }
            f.write(json.dumps(log_entry) + "\n")

    def get_cli_status(self) -> str:
        """Return a CLI-friendly status string."""
        dash = self.get_status_dashboard()
        lines = [
            f"Time: {dash['timestamp']}",
            f"CPU: {dash['cpu_percent']:.1f}%",
            f"Memory: {dash['memory_percent']:.1f}%",
            f"Disk: {dash['disk_percent']:.1f}%",
            f"Ollama: {dash['ollama_status']['status']}",
            f"DB Sizes: {dash['db_sizes']}",
            f"Agent Perf: {dash['agent_performance']}",
        ]
        if dash['alerts']:
            lines.append(f"ALERTS: {'; '.join(dash['alerts'])}")
        if dash['throttle']:
            lines.append(f"THROTTLING ACTIVE ({dash['throttle_reason']})")
        return "\n".join(lines)

# Decorator for agent methods to track performance
import functools

def track_agent_performance(agent_name, monitor: ResourceMonitor):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception:
                success = False
                result = None
                raise
            finally:
                elapsed = time.time() - start
                monitor.record_agent_response(agent_name, elapsed, success)
            return result
        return wrapper
    return decorator 