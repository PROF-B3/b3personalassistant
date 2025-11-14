"""
Task Management System
A comprehensive task and project management system with AI-powered optimization.
"""

import sqlite3
import json
import datetime
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(Enum):
    """Task status levels."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


@dataclass
class Category:
    """Represents a task category."""
    id: int
    name: str
    color: str
    description: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Task:
    """Represents a single task."""
    id: int
    title: str
    description: str
    priority: Priority
    due_date: Optional[str]
    status: Status
    category_id: Optional[int]
    project_id: Optional[str]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    tags: List[str]
    metadata: Dict[str, Any]


class TaskManager:
    """Main task management system."""
    
    def __init__(self, db_path: str = "databases/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with all required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#007bff',
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    due_date TEXT,
                    status TEXT NOT NULL DEFAULT 'todo',
                    category_id INTEGER,
                    project_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    estimated_hours REAL,
                    actual_hours REAL,
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)
            
            # Create task dependencies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id INTEGER,
                    depends_on_id INTEGER,
                    dependency_type TEXT DEFAULT 'blocks',  -- blocks, requires, suggests
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (task_id, depends_on_id),
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (depends_on_id) REFERENCES tasks (id)
                )
            """)
            
            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    due_date TEXT,
                    metadata TEXT  -- JSON object
                )
            """)
            
            # Create task history table for tracking changes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_at TEXT NOT NULL,
                    changed_by TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_task ON task_dependencies(task_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_depends ON task_dependencies(depends_on_id)")
            
            # Insert default categories
            default_categories = [
                ("Work", "#007bff", "Work-related tasks"),
                ("Personal", "#28a745", "Personal tasks"),
                ("Health", "#dc3545", "Health and fitness"),
                ("Learning", "#ffc107", "Learning and education"),
                ("Finance", "#17a2b8", "Financial tasks"),
                ("Home", "#6f42c1", "Home and maintenance"),
                ("Urgent", "#fd7e14", "Urgent tasks requiring immediate attention")
            ]
            
            for name, color, description in default_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, color, description, created_at)
                    VALUES (?, ?, ?, ?)
                """, (name, color, description, datetime.now().isoformat()))
            
            conn.commit()
    
    def create_task(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM,
                   due_date: Optional[str] = None, category_id: Optional[int] = None,
                   project_id: Optional[str] = None, estimated_hours: Optional[float] = None,
                   tags: List[str] = None, metadata: Dict[str, Any] = None) -> int:
        """Create a new task."""
        now = datetime.now().isoformat()
        tags = tags or []
        metadata = metadata or {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tasks 
                (title, description, priority, due_date, status, category_id, project_id,
                 created_at, updated_at, estimated_hours, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, description, priority.value, due_date, Status.TODO.value,
                category_id, project_id, now, now, estimated_hours,
                json.dumps(tags), json.dumps(metadata)
            ))
            
            task_id = cursor.lastrowid
            
            # Log the creation
            cursor.execute("""
                INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, "created", None, title, now))
            
            conn.commit()
        
        logger.info(f"Created task {task_id}: {title}")
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, priority, due_date, status, category_id,
                       project_id, created_at, updated_at, completed_at, estimated_hours,
                       actual_hours, tags, metadata
                FROM tasks WHERE id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Task(
                id=row[0],
                title=row[1],
                description=row[2],
                priority=Priority(row[3]),
                due_date=row[4],
                status=Status(row[5]),
                category_id=row[6],
                project_id=row[7],
                created_at=row[8],
                updated_at=row[9],
                completed_at=row[10],
                estimated_hours=row[11],
                actual_hours=row[12],
                tags=json.loads(row[13]) if row[13] else [],
                metadata=json.loads(row[14]) if row[14] else {}
            )
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update a task with new values."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Track changes
        changes = []
        now = datetime.now().isoformat()
        
        # Update fields
        update_fields = []
        update_values = []
        
        for field, value in kwargs.items():
            if hasattr(task, field) and getattr(task, field) != value:
                old_value = getattr(task, field)
                setattr(task, field, value)
                changes.append((field, old_value, value))
                update_fields.append(f"{field} = ?")
                update_values.append(value)
        
        if not changes:
            return True  # No changes needed
        
        update_fields.append("updated_at = ?")
        update_values.append(now)
        update_values.append(task_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update task
            cursor.execute(f"""
                UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?
            """, update_values)
            
            # Log changes
            for field, old_value, new_value in changes:
                cursor.execute("""
                    INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (task_id, field, str(old_value), str(new_value), now))
            
            conn.commit()
        
        logger.info(f"Updated task {task_id}: {changes}")
        return True
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task and its dependencies."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete dependencies
            cursor.execute("DELETE FROM task_dependencies WHERE task_id = ? OR depends_on_id = ?", 
                         (task_id, task_id))
            
            # Delete task history
            cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
            
            # Delete task
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            conn.commit()
        
        logger.info(f"Deleted task {task_id}")
        return True
    
    def get_tasks(self, status: Optional[Status] = None, priority: Optional[Priority] = None,
                  category_id: Optional[int] = None, project_id: Optional[str] = None,
                  due_before: Optional[str] = None, limit: int = 100) -> List[Task]:
        """Get tasks with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, title, description, priority, due_date, status, category_id, project_id, created_at, updated_at, completed_at, estimated_hours, actual_hours, tags, metadata FROM tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority.value)
            
            if category_id:
                query += " AND category_id = ?"
                params.append(category_id)
            
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            
            if due_before:
                query += " AND due_date <= ?"
                params.append(due_before)
            
            query += " ORDER BY priority DESC, due_date ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row[0], title=row[1], description=row[2], priority=Priority(row[3]),
                    due_date=row[4], status=Status(row[5]), category_id=row[6], project_id=row[7],
                    created_at=row[8], updated_at=row[9], completed_at=row[10],
                    estimated_hours=row[11], actual_hours=row[12],
                    tags=json.loads(row[13]) if row[13] else [],
                    metadata=json.loads(row[14]) if row[14] else {}
                ))
            
            return tasks
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get tasks that are overdue."""
        now = datetime.now().isoformat()
        return self.get_tasks(due_before=now, status=Status.TODO)
    
    def get_due_soon_tasks(self, days: int = 3) -> List[Task]:
        """Get tasks due within the next N days."""
        future_date = (datetime.now() + timedelta(days=days)).isoformat()
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, priority, due_date, status, category_id, project_id,
                       created_at, updated_at, completed_at, estimated_hours, actual_hours, tags, metadata
                FROM tasks 
                WHERE due_date BETWEEN ? AND ? AND status IN ('todo', 'in_progress')
                ORDER BY due_date ASC
            """, (now, future_date))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row[0], title=row[1], description=row[2], priority=Priority(row[3]),
                    due_date=row[4], status=Status(row[5]), category_id=row[6], project_id=row[7],
                    created_at=row[8], updated_at=row[9], completed_at=row[10],
                    estimated_hours=row[11], actual_hours=row[12],
                    tags=json.loads(row[13]) if row[13] else [],
                    metadata=json.loads(row[14]) if row[14] else {}
                ))
            
            return tasks
    
    def add_dependency(self, task_id: int, depends_on_id: int, 
                      dependency_type: str = "blocks") -> bool:
        """Add a dependency between tasks."""
        if task_id == depends_on_id:
            return False  # Can't depend on itself
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if dependency already exists
            cursor.execute("""
                SELECT 1 FROM task_dependencies 
                WHERE task_id = ? AND depends_on_id = ?
            """, (task_id, depends_on_id))
            
            if cursor.fetchone():
                return False  # Dependency already exists
            
            # Check for circular dependencies
            if self._would_create_circular_dependency(task_id, depends_on_id):
                return False
            
            cursor.execute("""
                INSERT INTO task_dependencies (task_id, depends_on_id, dependency_type, created_at)
                VALUES (?, ?, ?, ?)
            """, (task_id, depends_on_id, dependency_type, datetime.now().isoformat()))
            
            conn.commit()
        
        logger.info(f"Added dependency: task {task_id} depends on {depends_on_id}")
        return True
    
    def _would_create_circular_dependency(self, task_id: int, depends_on_id: int) -> bool:
        """
        Check if adding a dependency would create a circular dependency.

        Optimized version that fetches all dependencies once and performs
        graph traversal in memory using BFS.

        Args:
            task_id: The task that would depend on depends_on_id
            depends_on_id: The task that task_id would depend on

        Returns:
            True if adding this dependency would create a cycle
        """
        # Fetch all dependencies in one query
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, depends_on_id FROM task_dependencies
            """)
            all_deps = cursor.fetchall()

        # Build adjacency list (dependency graph)
        graph = {}
        for t_id, dep_id in all_deps:
            if t_id not in graph:
                graph[t_id] = []
            graph[t_id].append(dep_id)

        # Check if adding (task_id -> depends_on_id) would create a cycle
        # by checking if there's already a path from depends_on_id to task_id
        visited = set()
        queue = [depends_on_id]

        while queue:
            current = queue.pop(0)

            if current == task_id:
                return True  # Found a path - would create cycle

            if current in visited:
                continue

            visited.add(current)

            # Add all dependencies of current task to queue
            if current in graph:
                queue.extend(graph[current])

        return False  # No path found - safe to add dependency
    
    def get_dependencies(self, task_id: int) -> List[Task]:
        """Get all tasks that the given task depends on."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT depends_on_id FROM task_dependencies WHERE task_id = ?
            """, (task_id,))
            
            dependency_ids = [row[0] for row in cursor.fetchall()]
            
            dependencies = []
            for dep_id in dependency_ids:
                task = self.get_task(dep_id)
                if task:
                    dependencies.append(task)
            
            return dependencies
    
    def get_dependents(self, task_id: int) -> List[Task]:
        """Get all tasks that depend on the given task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id FROM task_dependencies WHERE depends_on_id = ?
            """, (task_id,))
            
            dependent_ids = [row[0] for row in cursor.fetchall()]
            
            dependents = []
            for dep_id in dependent_ids:
                task = self.get_task(dep_id)
                if task:
                    dependents.append(task)
            
            return dependents
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks that are blocked by incomplete dependencies."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT t.id FROM tasks t
                JOIN task_dependencies td ON t.id = td.task_id
                JOIN tasks dep ON td.depends_on_id = dep.id
                WHERE t.status = 'todo' AND dep.status != 'done'
            """)
            
            blocked_ids = [row[0] for row in cursor.fetchall()]
            
            blocked_tasks = []
            for task_id in blocked_ids:
                task = self.get_task(task_id)
                if task:
                    blocked_tasks.append(task)
            
            return blocked_tasks
    
    def create_category(self, name: str, color: str = "#007bff", 
                       description: str = None) -> int:
        """Create a new category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, color, description, created_at)
                VALUES (?, ?, ?, ?)
            """, (name, color, description, datetime.now().isoformat()))
            
            category_id = cursor.lastrowid
            conn.commit()
        
        logger.info(f"Created category {category_id}: {name}")
        return category_id
    
    def get_categories(self) -> List[Category]:
        """Get all categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, color, description, created_at FROM categories
                ORDER BY name
            """)
            
            categories = []
            for row in cursor.fetchall():
                categories.append(Category(
                    id=row[0], name=row[1], color=row[2], 
                    description=row[3], created_at=row[4]
                ))
            
            return categories
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get comprehensive task statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total tasks by status
            cursor.execute("""
                SELECT status, COUNT(*) FROM tasks GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Total tasks by priority
            cursor.execute("""
                SELECT priority, COUNT(*) FROM tasks GROUP BY priority
            """)
            priority_counts = dict(cursor.fetchall())
            
            # Overdue tasks
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE due_date < ? AND status IN ('todo', 'in_progress')
            """, (datetime.now().isoformat(),))
            overdue_count = cursor.fetchone()[0]
            
            # Due soon tasks
            future_date = (datetime.now() + timedelta(days=3)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE due_date BETWEEN ? AND ? AND status IN ('todo', 'in_progress')
            """, (datetime.now().isoformat(), future_date))
            due_soon_count = cursor.fetchone()[0]
            
            # Completion rate (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE completed_at >= ?
            """, (thirty_days_ago,))
            completed_recent = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE created_at >= ?
            """, (thirty_days_ago,))
            created_recent = cursor.fetchone()[0]
            
            completion_rate = (completed_recent / created_recent * 100) if created_recent > 0 else 0
            
            return {
                "status_counts": status_counts,
                "priority_counts": priority_counts,
                "overdue_count": overdue_count,
                "due_soon_count": due_soon_count,
                "completion_rate_30d": completion_rate,
                "total_tasks": sum(status_counts.values()),
                "blocked_tasks": len(self.get_blocked_tasks())
            }


class DeltaTaskOptimizer:
    """AI-powered task optimization for Delta agent."""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def analyze_workflow_efficiency(self) -> Dict[str, Any]:
        """Analyze current workflow efficiency and identify bottlenecks."""
        stats = self.task_manager.get_task_statistics()
        blocked_tasks = self.task_manager.get_blocked_tasks()
        overdue_tasks = self.task_manager.get_overdue_tasks()
        
        analysis = {
            "efficiency_score": 0,
            "bottlenecks": [],
            "recommendations": [],
            "critical_issues": []
        }
        
        # Calculate efficiency score
        total_tasks = stats["total_tasks"]
        if total_tasks > 0:
            done_tasks = stats["status_counts"].get("done", 0)
            analysis["efficiency_score"] = (done_tasks / total_tasks) * 100
        
        # Identify bottlenecks
        if blocked_tasks:
            analysis["bottlenecks"].append({
                "type": "blocked_tasks",
                "count": len(blocked_tasks),
                "description": f"{len(blocked_tasks)} tasks are blocked by incomplete dependencies"
            })
        
        if overdue_tasks:
            analysis["bottlenecks"].append({
                "type": "overdue_tasks",
                "count": len(overdue_tasks),
                "description": f"{len(overdue_tasks)} tasks are overdue"
            })
        
        # Generate recommendations
        if analysis["efficiency_score"] < 70:
            analysis["recommendations"].append(
                "Consider breaking down large tasks into smaller, more manageable pieces"
            )
        
        if len(blocked_tasks) > 0:
            analysis["recommendations"].append(
                "Focus on completing tasks that are blocking others to improve workflow"
            )
        
        if len(overdue_tasks) > 0:
            analysis["recommendations"].append(
                "Review and reprioritize overdue tasks or adjust due dates"
            )
        
        # Identify critical issues
        if len(overdue_tasks) > 5:
            analysis["critical_issues"].append("High number of overdue tasks indicates planning issues")
        
        if stats["completion_rate_30d"] < 50:
            analysis["critical_issues"].append("Low completion rate suggests workflow inefficiency")
        
        return analysis
    
    def optimize_task_priorities(self) -> List[Dict[str, Any]]:
        """Optimize task priorities based on dependencies, due dates, and impact."""
        tasks = self.task_manager.get_tasks(status=Status.TODO)
        
        # Score each task based on multiple factors
        scored_tasks = []
        for task in tasks:
            score = 0
            
            # Due date factor
            if task.due_date:
                due_date = datetime.fromisoformat(task.due_date)
                days_until_due = (due_date - datetime.now()).days
                if days_until_due < 0:
                    score += 100  # Overdue tasks get high priority
                elif days_until_due <= 3:
                    score += 50
                elif days_until_due <= 7:
                    score += 25
            
            # Priority factor
            priority_scores = {
                Priority.URGENT: 40,
                Priority.HIGH: 30,
                Priority.MEDIUM: 20,
                Priority.LOW: 10
            }
            score += priority_scores.get(task.priority, 20)
            
            # Dependency factor
            dependents = self.task_manager.get_dependents(task.id)
            score += len(dependents) * 15  # More dependents = higher priority
            
            # Blocking factor
            dependencies = self.task_manager.get_dependencies(task.id)
            blocked_dependencies = [dep for dep in dependencies if dep.status != Status.DONE]
            if blocked_dependencies:
                score -= 20  # Reduce priority if dependencies are incomplete
            
            scored_tasks.append({
                "task": task,
                "score": score,
                "factors": {
                    "due_date_urgency": days_until_due if task.due_date else None,
                    "dependents_count": len(dependents),
                    "blocked_dependencies": len(blocked_dependencies)
                }
            })
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_tasks
    
    def suggest_workflow_improvements(self) -> List[str]:
        """Suggest improvements to the current workflow."""
        suggestions = []
        stats = self.task_manager.get_task_statistics()
        
        # Analyze task distribution
        if stats["priority_counts"].get("urgent", 0) > 5:
            suggestions.append(
                "Too many urgent tasks - consider better planning to avoid last-minute urgency"
            )
        
        if stats["status_counts"].get("in_progress", 0) > 10:
            suggestions.append(
                "Too many tasks in progress - consider focusing on fewer tasks at once"
            )
        
        # Analyze completion patterns
        if stats["completion_rate_30d"] < 60:
            suggestions.append(
                "Low completion rate - consider setting more realistic deadlines"
            )
        
        # Analyze dependencies
        blocked_tasks = self.task_manager.get_blocked_tasks()
        if len(blocked_tasks) > 3:
            suggestions.append(
                "Many blocked tasks - review dependency structure and consider parallel work"
            )
        
        return suggestions
    
    def create_optimal_schedule(self, hours_per_day: float = 8.0, 
                               days_ahead: int = 7) -> Dict[str, List[Task]]:
        """Create an optimal daily schedule for the next N days."""
        prioritized_tasks = self.optimize_task_priorities()
        
        schedule = {}
        current_date = datetime.now().date()
        
        for day in range(days_ahead):
            date_key = (current_date + timedelta(days=day)).isoformat()
            schedule[date_key] = []
            
            remaining_hours = hours_per_day
            
            for scored_task in prioritized_tasks:
                task = scored_task["task"]
                
                # Skip if task is already scheduled or completed
                if task.status == Status.DONE:
                    continue
                
                # Estimate hours needed
                estimated_hours = task.estimated_hours or 2.0  # Default 2 hours
                
                if estimated_hours <= remaining_hours:
                    schedule[date_key].append(task)
                    remaining_hours -= estimated_hours
                    
                    # Mark as scheduled
                    scored_task["task"].status = Status.IN_PROGRESS
        
        return schedule


class NaturalLanguageTaskParser:
    """Parse natural language task descriptions into structured task data."""
    
    def __init__(self):
        # Priority keywords
        self.priority_keywords = {
            Priority.URGENT: ["urgent", "asap", "emergency", "critical", "immediately"],
            Priority.HIGH: ["high", "important", "priority", "urgent", "critical"],
            Priority.MEDIUM: ["medium", "normal", "standard"],
            Priority.LOW: ["low", "minor", "optional", "when possible"]
        }
        
        # Time patterns
        self.time_patterns = [
            (r"today", lambda: datetime.now().date()),
            (r"tomorrow", lambda: (datetime.now() + timedelta(days=1)).date()),
            (r"next week", lambda: (datetime.now() + timedelta(days=7)).date()),
            (r"in (\d+) days?", lambda m: (datetime.now() + timedelta(days=int(m.group(1)))).date()),
            (r"by (\w+ \d+)", lambda m: datetime.strptime(m.group(1), "%B %d").replace(year=datetime.now().year).date()),
        ]
    
    def parse_task_description(self, description: str) -> Dict[str, Any]:
        """Parse natural language task description into structured data."""
        description_lower = description.lower()
        
        # Extract priority
        priority = Priority.MEDIUM  # Default
        for pri, keywords in self.priority_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                priority = pri
                break
        
        # Extract due date
        due_date = None
        for pattern, date_func in self.time_patterns:
            match = re.search(pattern, description_lower)
            if match:
                try:
                    due_date = date_func(match).isoformat()
                    break
                except:
                    continue
        
        # Extract tags (words starting with #)
        tags = re.findall(r'#(\w+)', description)
        
        # Extract estimated time
        time_match = re.search(r'(\d+)\s*(?:hour|hr)s?', description_lower)
        estimated_hours = float(time_match.group(1)) if time_match else None
        
        return {
            "priority": priority,
            "due_date": due_date,
            "tags": tags,
            "estimated_hours": estimated_hours
        }


# Convenience functions
def create_task_manager(db_path: str = "databases/tasks.db") -> TaskManager:
    """Create and return a task manager instance."""
    return TaskManager(db_path)


def create_delta_optimizer(task_manager: TaskManager) -> DeltaTaskOptimizer:
    """Create and return a Delta task optimizer instance."""
    return DeltaTaskOptimizer(task_manager)


if __name__ == "__main__":
    # Test the task management system
    tm = create_task_manager()
    
    # Create some test tasks
    task1_id = tm.create_task(
        "Complete project proposal",
        "Write a comprehensive project proposal for the new AI system",
        priority=Priority.HIGH,
        due_date=(datetime.now() + timedelta(days=3)).isoformat(),
        estimated_hours=4.0,
        tags=["work", "proposal"]
    )
    
    task2_id = tm.create_task(
        "Review code changes",
        "Review the latest code changes and provide feedback",
        priority=Priority.MEDIUM,
        due_date=(datetime.now() + timedelta(days=1)).isoformat(),
        estimated_hours=2.0,
        tags=["work", "code-review"]
    )
    
    # Add dependency
    tm.add_dependency(task1_id, task2_id)
    
    # Test Delta optimizer
    delta_opt = create_delta_optimizer(tm)
    analysis = delta_opt.analyze_workflow_efficiency()
    print(f"Workflow analysis: {analysis}")
    
    # Get optimized priorities
    optimized = delta_opt.optimize_task_priorities()
    print(f"Optimized task priorities: {len(optimized)} tasks")
    
    # Get statistics
    stats = tm.get_task_statistics()
    print(f"Task statistics: {stats}") 