#!/usr/bin/env python3
"""
Production startup script for B3PersonalAssistant.

This script initializes the system with all production features:
- Database initialization
- Health monitoring
- Background agents
- Logging setup
- Error handling
"""

import sys
import os
import signal
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
import psutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from databases.manager import DatabaseManager
from modules.resources import ResourceMonitor
from monitoring.health_check import HealthChecker
from core.orchestrator import Orchestrator
from core.config import ConfigManager


class ProductionManager:
    """Manages the production deployment of B3PersonalAssistant."""
    
    def __init__(self):
        """Initialize the production manager."""
        self.running = False
        self.threads = []
        self.config = ConfigManager()
        self.setup_logging()
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.resource_monitor = ResourceMonitor(Path("databases"))
        self.health_checker = HealthChecker(self.db_manager, self.resource_monitor)
        
        # Initialize orchestrator with default user profile
        default_profile = {
            "name": "Production User",
            "communication_style": "professional",
            "work_style": "structured",
            "interests": ["productivity", "automation", "ai"],
            "task_management": "detailed"
        }
        self.orchestrator = Orchestrator(default_profile)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"b3_assistant_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set specific log levels
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Production logging initialized: {log_file}")
    
    def initialize_database(self):
        """Initialize database with sample data if empty."""
        try:
            stats = self.db_manager.get_database_stats()
            
            if stats['user_profiles'] == 0:
                self.logger.info("Database is empty, initializing with sample data...")
                
                # Create production user profile
                user = self.db_manager.create_user_profile(
                    name="Production User",
                    email="production@b3personalassistant.com",
                    communication_style="professional",
                    work_style="structured",
                    interests=["productivity", "automation", "ai", "monitoring"],
                    task_management="detailed"
                )
                
                # Create initial tasks
                initial_tasks = [
                    {
                        "title": "Monitor system health",
                        "description": "Regular health checks and monitoring",
                        "priority": "high",
                        "tags": ["monitoring", "health"]
                    },
                    {
                        "title": "Update documentation",
                        "description": "Keep documentation current",
                        "priority": "medium",
                        "tags": ["documentation"]
                    }
                ]
                
                for task_data in initial_tasks:
                    self.db_manager.create_task(
                        user_id=user.id,
                        title=task_data["title"],
                        description=task_data["description"],
                        priority=task_data["priority"],
                        tags=task_data["tags"]
                    )
                
                self.logger.info("Database initialized with production data")
            else:
                self.logger.info("Database already contains data, skipping initialization")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def start_health_monitoring(self):
        """Start background health monitoring."""
        def health_monitor():
            while self.running:
                try:
                    health_status = self.health_checker.check_system_health()
                    
                    if health_status['overall_status'] == 'unhealthy':
                        self.logger.warning(f"System health check failed: {health_status['alerts']}")
                    
                    # Log health summary every hour
                    if datetime.now().minute == 0:
                        summary = self.health_checker.get_health_summary()
                        self.logger.info(f"Health summary: {summary}")
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Error in health monitoring: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=health_monitor, daemon=True)
        thread.start()
        self.threads.append(thread)
        self.logger.info("Health monitoring started")
    
    def start_background_agents(self):
        """Start background agent processes."""
        def background_eta():
            """Eta agent for continuous system improvement."""
            while self.running:
                try:
                    # Run system improvement tasks
                    improvement_result = self.orchestrator.process_request(
                        "Analyze system performance and suggest improvements"
                    )
                    self.logger.info(f"Eta improvement: {improvement_result[:100]}...")
                    time.sleep(3600)  # Run every hour
                except Exception as e:
                    self.logger.error(f"Error in Eta background process: {e}")
                    time.sleep(3600)
        
        def background_zeta():
            """Zeta agent for code quality monitoring."""
            while self.running:
                try:
                    # Run code quality checks
                    quality_result = self.orchestrator.process_request(
                        "Scan codebase for potential improvements and issues"
                    )
                    self.logger.info(f"Zeta quality check: {quality_result[:100]}...")
                    time.sleep(7200)  # Run every 2 hours
                except Exception as e:
                    self.logger.error(f"Error in Zeta background process: {e}")
                    time.sleep(7200)
        
        def background_delta():
            """Delta agent for task optimization."""
            while self.running:
                try:
                    # Run task optimization
                    optimization_result = self.orchestrator.process_request(
                        "Optimize current tasks and workflows"
                    )
                    self.logger.info(f"Delta optimization: {optimization_result[:100]}...")
                    time.sleep(1800)  # Run every 30 minutes
                except Exception as e:
                    self.logger.error(f"Error in Delta background process: {e}")
                    time.sleep(1800)
        
        # Start background agent threads
        for agent_func, name in [(background_eta, "Eta"), (background_zeta, "Zeta"), (background_delta, "Delta")]:
            thread = threading.Thread(target=agent_func, daemon=True, name=f"background_{name}")
            thread.start()
            self.threads.append(thread)
            self.logger.info(f"Background agent {name} started")
    
    def start_data_cleanup(self):
        """Start periodic data cleanup."""
        def cleanup_worker():
            while self.running:
                try:
                    # Clean up old data every day
                    self.db_manager.cleanup_old_data(days=30)
                    self.logger.info("Data cleanup completed")
                    time.sleep(86400)  # 24 hours
                except Exception as e:
                    self.logger.error(f"Error in data cleanup: {e}")
                    time.sleep(86400)
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
        self.threads.append(thread)
        self.logger.info("Data cleanup worker started")
    
    def start_metrics_collection(self):
        """Start metrics collection."""
        def metrics_collector():
            while self.running:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Store metrics
                    self.db_manager.store_system_metrics(
                        cpu_usage=cpu_percent,
                        memory_usage=memory.percent,
                        disk_usage=disk.percent,
                        active_agents=7,  # All agents active
                        total_requests=0,  # Would track actual requests
                        error_count=0,  # Would track actual errors
                        response_time_avg=0.0  # Would track actual response times
                    )
                    
                    time.sleep(300)  # Collect every 5 minutes
                    
                except Exception as e:
                    self.logger.error(f"Error collecting metrics: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=metrics_collector, daemon=True)
        thread.start()
        self.threads.append(thread)
        self.logger.info("Metrics collection started")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Starting graceful shutdown...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Close database connections
        if hasattr(self.db_manager, 'engine'):
            self.db_manager.engine.dispose()
        
        self.logger.info("Shutdown complete")
        sys.exit(0)
    
    def run(self):
        """Start the production system."""
        try:
            self.logger.info("🚀 Starting B3PersonalAssistant in production mode...")
            
            # Initialize database
            self.initialize_database()
            
            # Set running flag
            self.running = True
            
            # Start background services
            self.start_health_monitoring()
            self.start_background_agents()
            self.start_data_cleanup()
            self.start_metrics_collection()
            
            # Initial health check
            health_status = self.health_checker.check_system_health()
            self.logger.info(f"Initial health check: {health_status['overall_status']}")
            
            if health_status['overall_status'] == 'unhealthy':
                self.logger.warning("System started with health issues")
            
            self.logger.info("✅ B3PersonalAssistant production system is running!")
            self.logger.info("📊 Health monitoring active")
            self.logger.info("🤖 Background agents running")
            self.logger.info("🗄️  Database initialized")
            self.logger.info("📈 Metrics collection active")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Fatal error in production system: {e}")
            self.shutdown()


def main():
    """Main entry point."""
    try:
        manager = ProductionManager()
        manager.run()
    except Exception as e:
        print(f"Failed to start production system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 