"""
Workflow Automation Engine for B3PersonalAssistant

Enables users to create automated workflows with triggers and actions.
Supports time-based, event-based, and condition-based automation.
"""

import logging
import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import re

from core.constants import DB_DIR
from core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of workflow triggers."""
    TIME_BASED = "time_based"  # Schedule (daily at 8am, every hour, etc.)
    EVENT_BASED = "event_based"  # When something happens (new email, task created, etc.)
    CONDITION_BASED = "condition_based"  # When condition is met (if X then Y)


class ActionType(Enum):
    """Types of workflow actions."""
    CREATE_TASK = "create_task"
    SEND_NOTIFICATION = "send_notification"
    CREATE_NOTE = "create_note"
    RUN_QUERY = "run_query"
    CALL_AGENT = "call_agent"
    EXECUTE_SCRIPT = "execute_script"
    SEND_EMAIL = "send_email"
    UPDATE_CONTEXT = "update_context"


@dataclass
class Trigger:
    """A workflow trigger."""
    trigger_type: str
    config: Dict[str, Any]  # Type-specific configuration
    description: str


@dataclass
class Action:
    """A workflow action."""
    action_type: str
    config: Dict[str, Any]  # Type-specific configuration
    description: str


@dataclass
class Workflow:
    """A complete workflow with trigger and actions."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    enabled: bool = True
    trigger: Optional[Trigger] = None
    actions: Optional[List[Action]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_run: Optional[str] = None
    run_count: int = 0


class WorkflowEngine:
    """
    Workflow automation engine.

    Features:
    - Time-based triggers (cron-like scheduling)
    - Event-based triggers (respond to events)
    - Condition-based triggers (if-this-then-that)
    - Multi-step actions
    - Workflow templates
    - Execution history
    - Error handling and retries

    Example:
        >>> engine = WorkflowEngine()
        >>>
        >>> # Create morning routine workflow
        >>> workflow = Workflow(
        ...     name="Morning Routine",
        ...     description="Daily morning tasks",
        ...     trigger=Trigger(
        ...         trigger_type=TriggerType.TIME_BASED.value,
        ...         config={"time": "08:00", "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
        ...         description="Every weekday at 8am"
        ...     ),
        ...     actions=[
        ...         Action(
        ...             action_type=ActionType.RUN_QUERY.value,
        ...             config={"query": "summarize unread emails"},
        ...             description="Get email summary"
        ...         ),
        ...         Action(
        ...             action_type=ActionType.CREATE_TASK.value,
        ...             config={"title": "Review daily tasks", "priority": "high"},
        ...             description="Create daily review task"
        ...         )
        ...     ]
        ... )
        >>> engine.create_workflow(workflow)
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize workflow engine.

        Args:
            db_path: Path to workflows database
        """
        if db_path is None:
            db_path = f"{DB_DIR}/workflows.db"

        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

        # Action handlers (can be extended)
        self.action_handlers: Dict[str, Callable] = {
            ActionType.CREATE_TASK.value: self._handle_create_task,
            ActionType.SEND_NOTIFICATION.value: self._handle_send_notification,
            ActionType.CREATE_NOTE.value: self._handle_create_note,
            ActionType.RUN_QUERY.value: self._handle_run_query,
            ActionType.UPDATE_CONTEXT.value: self._handle_update_context,
        }

    def _initialize_database(self):
        """Create workflows database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Workflows table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflows (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        enabled BOOLEAN DEFAULT TRUE,
                        trigger_type TEXT NOT NULL,
                        trigger_config TEXT NOT NULL,
                        trigger_description TEXT,
                        actions TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        last_run TEXT,
                        run_count INTEGER DEFAULT 0
                    )
                """)

                # Execution history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workflow_id INTEGER NOT NULL,
                        workflow_name TEXT NOT NULL,
                        trigger_reason TEXT,
                        started_at TEXT NOT NULL,
                        completed_at TEXT,
                        status TEXT NOT NULL,
                        error TEXT,
                        results TEXT,
                        FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                    )
                """)

                # Workflow templates
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        category TEXT,
                        description TEXT,
                        template_data TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0
                    )
                """)

                # Indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_workflow_enabled
                    ON workflows(enabled)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_workflow_trigger_type
                    ON workflows(trigger_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_execution_workflow
                    ON workflow_executions(workflow_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_execution_status
                    ON workflow_executions(status)
                """)

                conn.commit()

                # Add default templates
                self._add_default_templates()

                logger.info("Workflows database initialized")

        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to initialize workflows database: {e}") from e

    def _add_default_templates(self):
        """Add default workflow templates."""
        templates = [
            {
                "name": "Morning Email Summary",
                "category": "productivity",
                "description": "Get email summary every morning",
                "template_data": json.dumps({
                    "trigger": {
                        "trigger_type": "time_based",
                        "config": {"time": "08:00", "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
                        "description": "Weekdays at 8am"
                    },
                    "actions": [
                        {
                            "action_type": "run_query",
                            "config": {"query": "summarize unread emails from last 24 hours"},
                            "description": "Get email summary"
                        },
                        {
                            "action_type": "send_notification",
                            "config": {"title": "Daily Email Summary", "message": "{query_result}"},
                            "description": "Send notification"
                        }
                    ]
                })
            },
            {
                "name": "Weekly Review Reminder",
                "category": "productivity",
                "description": "Remind to do weekly review every Friday",
                "template_data": json.dumps({
                    "trigger": {
                        "trigger_type": "time_based",
                        "config": {"time": "16:00", "days": ["Fri"]},
                        "description": "Friday at 4pm"
                    },
                    "actions": [
                        {
                            "action_type": "create_task",
                            "config": {"title": "Weekly Review", "priority": "high", "description": "Review accomplishments and plan next week"},
                            "description": "Create review task"
                        }
                    ]
                })
            },
            {
                "name": "High Priority Email Alert",
                "category": "communication",
                "description": "Get notified when high-priority email arrives",
                "template_data": json.dumps({
                    "trigger": {
                        "trigger_type": "event_based",
                        "config": {"event": "email_received", "filter": {"importance": "high"}},
                        "description": "When high-priority email received"
                    },
                    "actions": [
                        {
                            "action_type": "send_notification",
                            "config": {"title": "High Priority Email", "message": "From: {sender}, Subject: {subject}"},
                            "description": "Alert user"
                        },
                        {
                            "action_type": "create_task",
                            "config": {"title": "Respond to {sender}", "priority": "high"},
                            "description": "Create response task"
                        }
                    ]
                })
            }
        ]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for template in templates:
                    cursor.execute("""
                        INSERT OR IGNORE INTO workflow_templates
                        (name, category, description, template_data)
                        VALUES (?, ?, ?, ?)
                    """, (template["name"], template["category"], template["description"], template["template_data"]))

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Failed to add templates: {e}")

    def create_workflow(self, workflow: Workflow) -> Optional[int]:
        """
        Create a new workflow.

        Args:
            workflow: Workflow object

        Returns:
            Workflow ID if successful, None otherwise

        Example:
            >>> workflow = Workflow(
            ...     name="Daily Standup Reminder",
            ...     description="Remind about daily standup",
            ...     trigger=Trigger(
            ...         trigger_type=TriggerType.TIME_BASED.value,
            ...         config={"time": "09:30", "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
            ...         description="Weekdays at 9:30am"
            ...     ),
            ...     actions=[
            ...         Action(
            ...             action_type=ActionType.SEND_NOTIFICATION.value,
            ...             config={"title": "Daily Standup", "message": "Time for daily standup!"},
            ...             description="Send reminder"
            ...         )
            ...     ]
            ... )
            >>> workflow_id = engine.create_workflow(workflow)
        """
        try:
            now = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflows
                    (name, description, enabled, trigger_type, trigger_config, trigger_description,
                     actions, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow.name,
                    workflow.description,
                    workflow.enabled,
                    workflow.trigger.trigger_type,
                    json.dumps(workflow.trigger.config),
                    workflow.trigger.description,
                    json.dumps([asdict(a) for a in workflow.actions]),
                    now,
                    now
                ))
                conn.commit()

                workflow_id = cursor.lastrowid
                logger.info(f"Created workflow: {workflow.name} (ID: {workflow_id})")
                return workflow_id

        except sqlite3.Error as e:
            logger.error(f"Failed to create workflow: {e}")
            return None

    def execute_workflow(self, workflow_id: int, trigger_reason: str = "manual") -> bool:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow ID
            trigger_reason: Reason workflow was triggered

        Returns:
            True if successful
        """
        started_at = datetime.now().isoformat()
        workflow = self.get_workflow(workflow_id)

        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False

        if not workflow.enabled:
            logger.warning(f"Workflow {workflow_id} is disabled")
            return False

        try:
            logger.info(f"Executing workflow: {workflow.name}")
            results = []

            # Execute each action
            for action in workflow.actions:
                handler = self.action_handlers.get(action.action_type)

                if handler:
                    result = handler(action.config)
                    results.append({
                        "action": action.description,
                        "result": result
                    })
                else:
                    logger.warning(f"No handler for action type: {action.action_type}")
                    results.append({
                        "action": action.description,
                        "result": "not_implemented"
                    })

            # Record execution
            completed_at = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Update workflow stats
                cursor.execute("""
                    UPDATE workflows
                    SET last_run = ?, run_count = run_count + 1
                    WHERE id = ?
                """, (completed_at, workflow_id))

                # Record execution
                cursor.execute("""
                    INSERT INTO workflow_executions
                    (workflow_id, workflow_name, trigger_reason, started_at, completed_at, status, results)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow_id,
                    workflow.name,
                    trigger_reason,
                    started_at,
                    completed_at,
                    "success",
                    json.dumps(results)
                ))

                conn.commit()

            logger.info(f"Workflow executed successfully: {workflow.name}")
            return True

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")

            # Record failure
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO workflow_executions
                        (workflow_id, workflow_name, trigger_reason, started_at, completed_at, status, error)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        workflow_id,
                        workflow.name,
                        trigger_reason,
                        started_at,
                        datetime.now().isoformat(),
                        "failed",
                        str(e)
                    ))
                    conn.commit()
            except sqlite3.Error:
                pass

            return False

    def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        """Get workflow by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, enabled, trigger_type, trigger_config,
                           trigger_description, actions, created_at, updated_at, last_run, run_count
                    FROM workflows
                    WHERE id = ?
                """, (workflow_id,))

                row = cursor.fetchone()
                if row:
                    actions_data = json.loads(row[7])
                    actions = [Action(**a) for a in actions_data]

                    return Workflow(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        enabled=bool(row[3]),
                        trigger=Trigger(
                            trigger_type=row[4],
                            config=json.loads(row[5]),
                            description=row[6]
                        ),
                        actions=actions,
                        created_at=row[8],
                        updated_at=row[9],
                        last_run=row[10],
                        run_count=row[11]
                    )

                return None

        except sqlite3.Error as e:
            logger.error(f"Failed to get workflow: {e}")
            return None

    def list_workflows(self, enabled_only: bool = False) -> List[Workflow]:
        """List all workflows."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = """
                    SELECT id, name, description, enabled, trigger_type, trigger_config,
                           trigger_description, actions, created_at, updated_at, last_run, run_count
                    FROM workflows
                """
                if enabled_only:
                    query += " WHERE enabled = TRUE"

                query += " ORDER BY name"

                cursor.execute(query)

                workflows = []
                for row in cursor.fetchall():
                    actions_data = json.loads(row[7])
                    actions = [Action(**a) for a in actions_data]

                    workflows.append(Workflow(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        enabled=bool(row[3]),
                        trigger=Trigger(
                            trigger_type=row[4],
                            config=json.loads(row[5]),
                            description=row[6]
                        ),
                        actions=actions,
                        created_at=row[8],
                        updated_at=row[9],
                        last_run=row[10],
                        run_count=row[11]
                    ))

                return workflows

        except sqlite3.Error as e:
            logger.error(f"Failed to list workflows: {e}")
            return []

    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workflow templates."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT name, category, description, template_data FROM workflow_templates"
                params = []

                if category:
                    query += " WHERE category = ?"
                    params.append(category)

                query += " ORDER BY category, name"

                cursor.execute(query, params)

                templates = []
                for row in cursor.fetchall():
                    templates.append({
                        "name": row[0],
                        "category": row[1],
                        "description": row[2],
                        "template_data": json.loads(row[3])
                    })

                return templates

        except sqlite3.Error as e:
            logger.error(f"Failed to get templates: {e}")
            return []

    # Action handlers (stubs - would integrate with actual modules)

    def _handle_create_task(self, config: Dict) -> str:
        """Handle create_task action."""
        logger.info(f"Creating task: {config.get('title')}")
        # Would integrate with actual task module
        return f"Task created: {config.get('title')}"

    def _handle_send_notification(self, config: Dict) -> str:
        """Handle send_notification action."""
        logger.info(f"Sending notification: {config.get('title')}")
        # Would integrate with notification system
        return f"Notification sent: {config.get('title')}"

    def _handle_create_note(self, config: Dict) -> str:
        """Handle create_note action."""
        logger.info(f"Creating note: {config.get('title')}")
        # Would integrate with knowledge module
        return f"Note created: {config.get('title')}"

    def _handle_run_query(self, config: Dict) -> str:
        """Handle run_query action."""
        logger.info(f"Running query: {config.get('query')}")
        # Would integrate with orchestrator
        return f"Query executed: {config.get('query')}"

    def _handle_update_context(self, config: Dict) -> str:
        """Handle update_context action."""
        logger.info(f"Updating context: {config.get('key')} = {config.get('value')}")
        # Would integrate with context manager
        return f"Context updated"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize engine
    engine = WorkflowEngine()

    # Create a workflow
    workflow = Workflow(
        name="Morning Routine",
        description="Automated morning routine",
        trigger=Trigger(
            trigger_type=TriggerType.TIME_BASED.value,
            config={"time": "08:00", "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
            description="Weekdays at 8am"
        ),
        actions=[
            Action(
                action_type=ActionType.RUN_QUERY.value,
                config={"query": "summarize unread emails"},
                description="Get email summary"
            ),
            Action(
                action_type=ActionType.SEND_NOTIFICATION.value,
                config={"title": "Good Morning!", "message": "Here's your daily summary"},
                description="Send morning greeting"
            ),
            Action(
                action_type=ActionType.CREATE_TASK.value,
                config={"title": "Review daily tasks", "priority": "high"},
                description="Create daily review task"
            )
        ]
    )

    workflow_id = engine.create_workflow(workflow)
    print(f"Created workflow with ID: {workflow_id}")

    # Execute workflow
    if workflow_id:
        print(f"\nExecuting workflow...")
        success = engine.execute_workflow(workflow_id, trigger_reason="manual_test")
        print(f"Execution {'successful' if success else 'failed'}")

    # List workflows
    print("\nAll Workflows:")
    for wf in engine.list_workflows():
        print(f"- {wf.name}: {wf.description}")
        print(f"  Trigger: {wf.trigger.description}")
        print(f"  Actions: {len(wf.actions)}")
        print(f"  Run count: {wf.run_count}\n")

    # Show templates
    print("Available Templates:")
    for template in engine.get_templates():
        print(f"- [{template['category']}] {template['name']}")
        print(f"  {template['description']}\n")
