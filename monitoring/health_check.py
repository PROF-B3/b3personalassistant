"""
Health check and monitoring system for B3PersonalAssistant.
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from databases.manager import DatabaseManager
from modules.resources import ResourceMonitor

logger = logging.getLogger(__name__)


class HealthChecker:
    """System health checker and monitor."""
    
    def __init__(self, db_manager: DatabaseManager, resource_monitor: ResourceMonitor):
        """
        Initialize health checker.
        
        Args:
            db_manager: Database manager instance
            resource_monitor: Resource monitor instance
        """
        self.db_manager = db_manager
        self.resource_monitor = resource_monitor
        self.health_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dictionary with health status and metrics
        """
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'metrics': {},
            'alerts': []
        }
        
        # Check system resources
        resource_check = self._check_system_resources()
        health_status['checks']['resources'] = resource_check
        
        # Check database health
        db_check = self._check_database_health()
        health_status['checks']['database'] = db_check
        
        # Check agent status
        agent_check = self._check_agent_health()
        health_status['checks']['agents'] = agent_check
        
        # Check file system
        fs_check = self._check_file_system()
        health_status['checks']['filesystem'] = fs_check
        
        # Check external dependencies
        deps_check = self._check_dependencies()
        health_status['checks']['dependencies'] = deps_check
        
        # Determine overall status
        failed_checks = [
            check for check in health_status['checks'].values()
            if check.get('status') == 'error'
        ]
        
        if failed_checks:
            health_status['overall_status'] = 'unhealthy'
            health_status['alerts'].extend([
                f"Check failed: {check.get('name', 'Unknown')}"
                for check in failed_checks
            ])
        
        # Store health history
        self.health_history.append(health_status)
        if len(self.health_history) > self.max_history_size:
            self.health_history.pop(0)
        
        # Store metrics in database
        self._store_health_metrics(health_status)
        
        return health_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get resource limits from config
            max_cpu = 80  # Should come from config
            max_memory = 80  # Should come from config
            max_disk = 90  # Should come from config
            
            status = 'healthy'
            alerts = []
            
            if cpu_percent > max_cpu:
                status = 'warning'
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > max_memory:
                status = 'warning'
                alerts.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > max_disk:
                status = 'error'
                alerts.append(f"Critical disk usage: {disk.percent:.1f}%")
            
            return {
                'name': 'System Resources',
                'status': status,
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {
                'name': 'System Resources',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and performance."""
        try:
            # Test database connection
            stats = self.db_manager.get_database_stats()
            
            # Check database size
            db_size_mb = stats.get('database_size_mb', 0)
            max_db_size_mb = 1000  # 1GB limit
            
            status = 'healthy'
            alerts = []
            
            if db_size_mb > max_db_size_mb:
                status = 'warning'
                alerts.append(f"Large database size: {db_size_mb:.1f}MB")
            
            # Check for old data that should be cleaned up
            if stats.get('conversations', 0) > 10000:
                alerts.append("High conversation count - consider cleanup")
            
            return {
                'name': 'Database',
                'status': status,
                'metrics': stats,
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error checking database health: {e}")
            return {
                'name': 'Database',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_agent_health(self) -> Dict[str, Any]:
        """Check agent health and performance."""
        try:
            # This would check actual agent status in a real implementation
            # For now, we'll simulate agent health checks
            
            agent_status = {
                'alpha': {'status': 'active', 'last_seen': datetime.utcnow()},
                'beta': {'status': 'active', 'last_seen': datetime.utcnow()},
                'gamma': {'status': 'active', 'last_seen': datetime.utcnow()},
                'delta': {'status': 'active', 'last_seen': datetime.utcnow()},
                'epsilon': {'status': 'active', 'last_seen': datetime.utcnow()},
                'zeta': {'status': 'active', 'last_seen': datetime.utcnow()},
                'eta': {'status': 'active', 'last_seen': datetime.utcnow()}
            }
            
            active_agents = sum(1 for agent in agent_status.values() if agent['status'] == 'active')
            total_agents = len(agent_status)
            
            status = 'healthy' if active_agents == total_agents else 'warning'
            alerts = []
            
            if active_agents < total_agents:
                alerts.append(f"Some agents inactive: {active_agents}/{total_agents}")
            
            return {
                'name': 'Agents',
                'status': status,
                'metrics': {
                    'active_agents': active_agents,
                    'total_agents': total_agents,
                    'agent_status': agent_status
                },
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error checking agent health: {e}")
            return {
                'name': 'Agents',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_file_system(self) -> Dict[str, Any]:
        """Check file system health and permissions."""
        try:
            required_dirs = [
                'databases',
                'data',
                'output_segments',
                'logs'
            ]
            
            status = 'healthy'
            alerts = []
            dir_status = {}
            
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    alerts.append(f"Created missing directory: {dir_name}")
                
                # Check write permissions
                try:
                    test_file = dir_path / '.test_write'
                    test_file.write_text('test')
                    test_file.unlink()
                    dir_status[dir_name] = 'writable'
                except Exception as e:
                    dir_status[dir_name] = 'not_writable'
                    alerts.append(f"Directory not writable: {dir_name}")
                    status = 'error'
            
            return {
                'name': 'File System',
                'status': status,
                'metrics': {
                    'directory_status': dir_status
                },
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error checking file system: {e}")
            return {
                'name': 'File System',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check external dependencies."""
        try:
            dependencies = {
                'ollama': self._check_ollama(),
                'sqlite': self._check_sqlite(),
                'ffmpeg': self._check_ffmpeg()
            }
            
            failed_deps = [name for name, status in dependencies.items() if not status['available']]
            status = 'healthy' if not failed_deps else 'error'
            
            alerts = []
            if failed_deps:
                alerts.append(f"Missing dependencies: {', '.join(failed_deps)}")
            
            return {
                'name': 'Dependencies',
                'status': status,
                'metrics': dependencies,
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return {
                'name': 'Dependencies',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_ollama(self) -> Dict[str, Any]:
        """Check Ollama availability."""
        try:
            import ollama
            client = ollama.Client()
            # Try to list models
            models = client.list()
            return {
                'available': True,
                'models': [model['name'] for model in models['models']],
                'version': 'unknown'  # Ollama doesn't expose version easily
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _check_sqlite(self) -> Dict[str, Any]:
        """Check SQLite availability."""
        try:
            import sqlite3
            return {
                'available': True,
                'version': sqlite3.sqlite_version
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _check_ffmpeg(self) -> Dict[str, Any]:
        """Check FFmpeg availability."""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from output
                version_line = result.stdout.split('\n')[0]
                version = version_line.split(' ')[2] if ' ' in version_line else 'unknown'
                return {
                    'available': True,
                    'version': version
                }
            else:
                return {
                    'available': False,
                    'error': 'FFmpeg not found or not working'
                }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _store_health_metrics(self, health_status: Dict[str, Any]):
        """Store health metrics in database."""
        try:
            # Extract metrics from health status
            resource_metrics = health_status['checks'].get('resources', {}).get('metrics', {})
            
            self.db_manager.store_system_metrics(
                cpu_usage=resource_metrics.get('cpu_percent', 0),
                memory_usage=resource_metrics.get('memory_percent', 0),
                disk_usage=resource_metrics.get('disk_percent', 0),
                active_agents=health_status['checks'].get('agents', {}).get('metrics', {}).get('active_agents', 0),
                total_requests=0,  # Would come from request tracking
                error_count=len(health_status['alerts']),
                response_time_avg=0.0  # Would come from performance tracking
            )
        except Exception as e:
            logger.error(f"Error storing health metrics: {e}")
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health history for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            health for health in self.health_history
            if datetime.fromisoformat(health['timestamp']) >= cutoff_time
        ]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of recent health status."""
        recent_health = self.get_health_history(hours=1)
        
        if not recent_health:
            return {
                'status': 'unknown',
                'last_check': None,
                'uptime_percentage': 0
            }
        
        healthy_checks = sum(1 for health in recent_health if health['overall_status'] == 'healthy')
        total_checks = len(recent_health)
        uptime_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            'status': recent_health[-1]['overall_status'],
            'last_check': recent_health[-1]['timestamp'],
            'uptime_percentage': uptime_percentage,
            'total_checks': total_checks,
            'healthy_checks': healthy_checks
        } 