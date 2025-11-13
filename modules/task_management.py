"""
Task Management System for B3PersonalAssistant.

Provides comprehensive task creation, tracking, scheduling, and workflow automation
for Delta agent.
"""

import logging
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class TaskStatus(Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a single task."""
    task_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.NORMAL

    # Scheduling
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    due_date: Optional[float] = None
    scheduled_start: Optional[float] = None
    completed_at: Optional[float] = None

    # Progress
    progress: float = 0.0  # 0-100%
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Organization
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    project: Optional[str] = None

    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    blocked_by: List[str] = field(default_factory=list)  # Issues blocking this task

    # Assignment
    assigned_to: Optional[str] = None  # Agent name
    created_by: str = "Delta"

    # Metadata
    notes: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)  # Subtask IDs
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'created_at': self.created_at,
            'due_date': self.due_date,
            'scheduled_start': self.scheduled_start,
            'completed_at': self.completed_at,
            'progress': self.progress,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'tags': self.tags,
            'category': self.category,
            'project': self.project,
            'dependencies': self.dependencies,
            'blocked_by': self.blocked_by,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'notes': self.notes,
            'subtasks': self.subtasks,
            'metadata': self.metadata
        }


class TaskManager:
    """
    Manages tasks for B3PersonalAssistant.

    Provides:
    - Task CRUD operations
    - Priority and dependency management
    - Progress tracking
    - Project organization
    - Workflow automation
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize task manager.

        Args:
            db_path: Path to SQLite database
        """
        self.logger = logging.getLogger("task_manager")
        self.db_path = db_path or Path("databases/tasks.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.task_counter = 0

        # Initialize database
        self._init_db()

        self.logger.info("Task manager initialized")

    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at REAL NOT NULL,
                due_date REAL,
                scheduled_start REAL,
                completed_at REAL,
                progress REAL DEFAULT 0.0,
                estimated_hours REAL,
                actual_hours REAL,
                tags TEXT,
                category TEXT,
                project TEXT,
                dependencies TEXT,
                blocked_by TEXT,
                assigned_to TEXT,
                created_by TEXT,
                notes TEXT,
                subtasks TEXT,
                metadata TEXT
            )
        ''')

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at REAL NOT NULL,
                deadline REAL,
                status TEXT,
                metadata TEXT
            )
        ''')

        # Task history table (for analytics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                field TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_at REAL NOT NULL,
                changed_by TEXT
            )
        ''')

        conn.commit()
        conn.close()

        self.logger.info("Task database initialized")

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        project: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        assigned_to: Optional[str] = None,
        estimated_hours: Optional[float] = None
    ) -> str:
        """
        Create a new task.

        Args:
            title: Task title
            description: Detailed description
            priority: Priority level
            due_date: Due date
            tags: List of tags
            category: Task category
            project: Project name
            dependencies: List of task IDs this depends on
            assigned_to: Agent to assign task to
            estimated_hours: Estimated time to complete

        Returns:
            Task ID
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(datetime.now().timestamp())}"

        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date.timestamp() if due_date else None,
            tags=tags or [],
            category=category,
            project=project,
            dependencies=dependencies or [],
            assigned_to=assigned_to,
            estimated_hours=estimated_hours
        )

        self._save_task(task)

        self.logger.info(f"Created task: {task_id} - {title}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task object or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_task(row)

    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        project: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks with filtering.

        Args:
            status: Filter by status
            priority: Filter by priority
            project: Filter by project
            assigned_to: Filter by assignment
            tag: Filter by tag
            limit: Maximum number of tasks

        Returns:
            List of tasks
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status.value)

        if priority is not None:
            query += ' AND priority = ?'
            params.append(priority.value)

        if project:
            query += ' AND project = ?'
            params.append(project)

        if assigned_to:
            query += ' AND assigned_to = ?'
            params.append(assigned_to)

        query += ' ORDER BY priority DESC, created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        tasks = [self._row_to_task(row) for row in rows]

        # Filter by tag if specified (tags are JSON array in DB)
        if tag:
            tasks = [t for t in tasks if tag in t.tags]

        return tasks

    def update_task(
        self,
        task_id: str,
        **updates
    ) -> bool:
        """
        Update task fields.

        Args:
            task_id: Task ID
            **updates: Fields to update (status, priority, progress, etc.)

        Returns:
            True if updated successfully
        """
        task = self.get_task(task_id)
        if not task:
            self.logger.warning(f"Task {task_id} not found")
            return False

        # Track history
        changes = []

        for field, value in updates.items():
            if hasattr(task, field):
                old_value = getattr(task, field)

                # Convert enums if necessary
                if field == 'status' and isinstance(value, str):
                    value = TaskStatus(value)
                elif field == 'priority' and isinstance(value, (int, str)):
                    value = TaskPriority(value) if isinstance(value, str) else TaskPriority(value)

                setattr(task, field, value)
                changes.append((field, old_value, value))

        # Auto-complete if progress reaches 100%
        if 'progress' in updates and updates['progress'] >= 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().timestamp()
            changes.append(('status', TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED))

        self._save_task(task)

        # Record changes in history
        for field, old_val, new_val in changes:
            self._record_history(task_id, field, str(old_val), str(new_val))

        self.logger.info(f"Updated task {task_id}: {len(changes)} changes")
        return True

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        if deleted:
            self.logger.info(f"Deleted task: {task_id}")

        return deleted

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        now = datetime.now().timestamp()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM tasks
            WHERE due_date < ?
            AND status NOT IN (?, ?)
            ORDER BY due_date ASC
        ''', (now, TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks due in the next N days."""
        now = datetime.now().timestamp()
        future = (datetime.now() + timedelta(days=days)).timestamp()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM tasks
            WHERE due_date BETWEEN ? AND ?
            AND status NOT IN (?, ?)
            ORDER BY due_date ASC
        ''', (now, future, TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks that are blocked."""
        tasks = self.get_tasks(status=TaskStatus.BLOCKED)
        return tasks

    def check_dependencies(self, task_id: str) -> Dict[str, Any]:
        """
        Check if task dependencies are satisfied.

        Args:
            task_id: Task ID

        Returns:
            Dictionary with dependency status
        """
        task = self.get_task(task_id)
        if not task:
            return {'satisfied': False, 'reason': 'Task not found'}

        if not task.dependencies:
            return {'satisfied': True, 'dependencies': []}

        # Check each dependency
        unsatisfied = []
        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if not dep_task:
                unsatisfied.append({'task_id': dep_id, 'reason': 'Task not found'})
            elif dep_task.status != TaskStatus.COMPLETED:
                unsatisfied.append({
                    'task_id': dep_id,
                    'title': dep_task.title,
                    'status': dep_task.status.value
                })

        return {
            'satisfied': len(unsatisfied) == 0,
            'unsatisfied_dependencies': unsatisfied,
            'total_dependencies': len(task.dependencies)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total tasks
        cursor.execute('SELECT COUNT(*) FROM tasks')
        total_tasks = cursor.fetchone()[0]

        # By status
        stats_by_status = {}
        for status in TaskStatus:
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', (status.value,))
            stats_by_status[status.value] = cursor.fetchone()[0]

        # By priority
        stats_by_priority = {}
        for priority in TaskPriority:
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE priority = ?', (priority.value,))
            stats_by_priority[priority.name] = cursor.fetchone()[0]

        # Overdue count
        now = datetime.now().timestamp()
        cursor.execute('''
            SELECT COUNT(*) FROM tasks
            WHERE due_date < ?
            AND status NOT IN (?, ?)
        ''', (now, TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value))
        overdue_count = cursor.fetchone()[0]

        # Completion rate
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', (TaskStatus.COMPLETED.value,))
        completed_count = cursor.fetchone()[0]
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

        conn.close()

        return {
            'total_tasks': total_tasks,
            'by_status': stats_by_status,
            'by_priority': stats_by_priority,
            'overdue_count': overdue_count,
            'completion_rate': completion_rate
        }

    def _save_task(self, task: Task):
        """Save task to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO tasks VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            task.task_id,
            task.title,
            task.description,
            task.status.value,
            task.priority.value,
            task.created_at,
            task.due_date,
            task.scheduled_start,
            task.completed_at,
            task.progress,
            task.estimated_hours,
            task.actual_hours,
            json.dumps(task.tags),
            task.category,
            task.project,
            json.dumps(task.dependencies),
            json.dumps(task.blocked_by),
            task.assigned_to,
            task.created_by,
            json.dumps(task.notes),
            json.dumps(task.subtasks),
            json.dumps(task.metadata)
        ))

        conn.commit()
        conn.close()

    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object."""
        return Task(
            task_id=row[0],
            title=row[1],
            description=row[2],
            status=TaskStatus(row[3]),
            priority=TaskPriority(row[4]),
            created_at=row[5],
            due_date=row[6],
            scheduled_start=row[7],
            completed_at=row[8],
            progress=row[9] or 0.0,
            estimated_hours=row[10],
            actual_hours=row[11],
            tags=json.loads(row[12]) if row[12] else [],
            category=row[13],
            project=row[14],
            dependencies=json.loads(row[15]) if row[15] else [],
            blocked_by=json.loads(row[16]) if row[16] else [],
            assigned_to=row[17],
            created_by=row[18],
            notes=json.loads(row[19]) if row[19] else [],
            subtasks=json.loads(row[20]) if row[20] else [],
            metadata=json.loads(row[21]) if row[21] else {}
        )

    def _record_history(self, task_id: str, field: str, old_value: str, new_value: str):
        """Record task change in history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO task_history (task_id, field, old_value, new_value, changed_at, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task_id, field, old_value, new_value, datetime.now().timestamp(), 'Delta'))

        conn.commit()
        conn.close()


def create_task_manager(db_path: Optional[Path] = None) -> TaskManager:
    """
    Convenience function to create a TaskManager.

    Args:
        db_path: Optional database path

    Returns:
        TaskManager instance
    """
    return TaskManager(db_path)
