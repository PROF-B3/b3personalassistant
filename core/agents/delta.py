"""
Delta Agent - Task Coordinator and Workflow Manager

Delta specializes in task management, project planning, and workflow optimization.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import (
    SIMPLE_MODEL,
    COMPLEX_MODEL,
    MAX_CONVERSATION_CONTEXT,
    DEFAULT_TASK_LIST_LIMIT,
    SECONDS_PER_DAY,
    PRIORITY_ICONS,
    STATUS_ICONS,
)
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class DeltaAgent(AgentBase):
    """
    Delta (Δ) - Task Coordinator and Workflow Manager

    Delta specializes in task management, project planning, and workflow optimization.
    Responsibilities include:
    - Task creation and management
    - Project planning and scheduling
    - Workflow optimization and automation
    - Progress tracking and reporting

    Personality: Efficient, organized, action-oriented

    Example:
        >>> delta = DeltaAgent(user_profile={"communication_style": "casual"})
        >>> response = delta.act("Create task list")
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None, task_manager=None):
        """
        Initialize Delta agent with task management capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
            task_manager: TaskManager instance for task operations
        """
        super().__init__('Delta', orchestrator, user_profile, resource_monitor)

        self.task_manager = task_manager
        if self.task_manager is None:
            from modules.task_management import create_task_manager
            self.task_manager = create_task_manager()

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Delta-specific system prompt."""
        return """You are Delta (Δ), the Task Coordinator of B3PersonalAssistant. You are:
- Efficient, organized, and action-oriented
- Expert at task management, project planning, and workflow optimization
- Skilled at breaking down complex projects into manageable tasks
- Focused on productivity, efficiency, and getting things done
- Strategic about prioritization and resource allocation

Your role is to help users create, organize, and optimize their tasks and workflows. You excel at project planning, task prioritization, and finding the most efficient path to goals.

Key phrases: "Let's break this down", "The most efficient approach", "I'll optimize this workflow", "First priority is"
Always help users stay organized and productive with clear, actionable task management."""

    def _handle_task_command(self, input_text: str) -> Optional[str]:
        """
        Handle direct task management commands.

        Args:
            input_text: User input text

        Returns:
            Response string if command was handled, None otherwise
        """
        from modules.task_management import TaskPriority, TaskStatus

        input_lower = input_text.lower()

        # Command: Create task
        if any(keyword in input_lower for keyword in ['create task', 'add task', 'new task']):
            title_match = re.search(r'(?:create|add|new) task[:\s]+(.+)', input_text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()

                priority = TaskPriority.NORMAL
                if 'urgent' in input_lower or 'critical' in input_lower:
                    priority = TaskPriority.URGENT
                elif 'high priority' in input_lower or 'important' in input_lower:
                    priority = TaskPriority.HIGH
                elif 'low priority' in input_lower:
                    priority = TaskPriority.LOW

                task_id = self.task_manager.create_task(title=title, priority=priority)
                return f"✓ Created task {task_id}: {title} [{priority.name}]"

            return "Please specify the task. Example: 'create task Review quarterly report'"

        # Command: List tasks
        elif any(keyword in input_lower for keyword in ['list tasks', 'show tasks', 'my tasks']):
            status_filter = None
            if 'todo' in input_lower:
                status_filter = TaskStatus.TODO
            elif 'in progress' in input_lower or 'active' in input_lower:
                status_filter = TaskStatus.IN_PROGRESS
            elif 'completed' in input_lower or 'done' in input_lower:
                status_filter = TaskStatus.COMPLETED

            tasks = self.task_manager.get_tasks(status=status_filter, limit=DEFAULT_TASK_LIST_LIMIT)

            if not tasks:
                return "📋 No tasks found." if not status_filter else f"📋 No {status_filter.value} tasks found."

            response = f"📋 Tasks ({len(tasks)}):\n\n"
            for task in tasks:
                priority_icon = PRIORITY_ICONS.get(task.priority.name, "")
                status_icon = STATUS_ICONS.get(task.status.name, "")

                response += f"{priority_icon} {status_icon} {task.task_id}: {task.title}\n"
                if task.due_date:
                    due_str = datetime.fromtimestamp(task.due_date).strftime('%Y-%m-%d')
                    response += f"  Due: {due_str}\n"

            return response

        # Command: Update task
        elif any(keyword in input_lower for keyword in ['update task', 'complete task', 'finish task']):
            task_id_match = re.search(r'task[_\s]?(\w+)', input_lower)
            if task_id_match:
                task_id = task_id_match.group(1)

                if 'complete' in input_lower or 'finish' in input_lower or 'done' in input_lower:
                    success = self.task_manager.update_task(
                        task_id,
                        status=TaskStatus.COMPLETED,
                        progress=100.0
                    )
                    if success:
                        return f"✅ Completed task {task_id}"
                    return f"❌ Task {task_id} not found"

                progress_match = re.search(r'(\d+)%', input_text)
                if progress_match:
                    progress = float(progress_match.group(1))
                    success = self.task_manager.update_task(task_id, progress=progress)
                    if success:
                        return f"✓ Updated task {task_id} progress to {progress}%"

            return "Please specify task ID. Example: 'complete task task_1'"

        # Command: Task statistics
        elif any(keyword in input_lower for keyword in ['task stats', 'task statistics', 'task summary']):
            stats = self.task_manager.get_statistics()

            return f"""📊 Task Statistics:

**Total Tasks:** {stats['total_tasks']}

**By Status:**
  • To-Do: {stats['by_status'].get('todo', 0)}
  • In Progress: {stats['by_status'].get('in_progress', 0)}
  • Completed: {stats['by_status'].get('completed', 0)}
  • Blocked: {stats['by_status'].get('blocked', 0)}

**By Priority:**
  • Urgent: {stats['by_priority'].get('URGENT', 0)}
  • High: {stats['by_priority'].get('HIGH', 0)}
  • Normal: {stats['by_priority'].get('NORMAL', 0)}
  • Low: {stats['by_priority'].get('LOW', 0)}

**Completion Rate:** {stats['completion_rate']:.1f}%
**Overdue Tasks:** {stats['overdue_count']}"""

        # Command: Overdue tasks
        elif 'overdue' in input_lower:
            overdue = self.task_manager.get_overdue_tasks()
            if not overdue:
                return "✅ No overdue tasks!"

            response = f"⚠️ Overdue Tasks ({len(overdue)}):\n\n"
            for task in overdue:
                due_date = datetime.fromtimestamp(task.due_date).strftime('%Y-%m-%d')
                days_overdue = (datetime.now().timestamp() - task.due_date) / SECONDS_PER_DAY
                response += f"• {task.task_id}: {task.title}\n"
                response += f"  Due: {due_date} ({int(days_overdue)} days ago)\n"

            return response

        return None

    @track_agent_performance('Delta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle task management and workflow operations.

        Args:
            input_data: User input text (task request)
            context: Optional context dictionary

        Returns:
            Task management response
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            command_response = self._handle_task_command(validated_input)
            if command_response:
                self.save_conversation('assistant', command_response)
                return self.adapt_to_user(command_response)

            complexity = self.estimate_complexity(input_data)
            model = COMPLEX_MODEL if complexity == "complex" else SIMPLE_MODEL

            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            messages = [{"role": "system", "content": self.system_prompt(context)}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Delta managing tasks with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Delta input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Delta circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Delta Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Delta act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)
