# B3PersonalAssistant API Documentation 🔧

> *"The API is the bridge between human intention and AI execution. Master it, and you master the future."* — Prof. B3

## 📚 Overview

This document provides comprehensive API documentation for B3PersonalAssistant, covering all modules, classes, and methods. Each section includes code examples, usage patterns, and integration guidelines.

## 🏗️ Core Module

### Agents (`core/agents.py`)

#### AgentBase Class

The base class for all AI agents in the system.

```python
from core.agents import AgentBase

class AgentBase:
    def __init__(self, name: str, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize a base agent.
        
        Args:
            name: Agent name (e.g., 'Alpha', 'Beta')
            orchestrator: Reference to the orchestrator for inter-agent communication
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
```

**Methods:**

- `act(input_data, context=None)`: Main agent action method
- `communicate(message, context=None)`: Agent-to-agent communication
- `think(input_data, context=None)`: Internal reasoning
- `send_message(to_agent, message, context=None)`: Send message to another agent
- `handle_error(error, context=None)`: Error handling
- `adapt_to_user(text)`: Adapt output to user preferences

**Example Usage:**
```python
from core.agents import AgentBase

class CustomAgent(AgentBase):
    def act(self, input_data, context=None):
        # Custom logic here
        result = f"Custom agent processed: {input_data}"
        return self.adapt_to_user(result)

# Usage
agent = CustomAgent("Custom", orchestrator=orchestrator, user_profile=profile)
response = agent.act("Hello world")
```

#### Specialized Agents

##### AlphaAgent
```python
from core.agents import AlphaAgent

alpha = AlphaAgent(orchestrator=orchestrator, user_profile=profile)
response = alpha.act("Coordinate a research project")
```

##### BetaAgent
```python
from core.agents import BetaAgent

beta = BetaAgent(orchestrator=orchestrator, user_profile=profile)
response = beta.act("Research quantum computing")
```

##### GammaAgent
```python
from core.agents import GammaAgent

gamma = GammaAgent(orchestrator=orchestrator, user_profile=profile)
response = gamma.act("Create notes on machine learning")
```

##### DeltaAgent
```python
from core.agents import DeltaAgent

delta = DeltaAgent(orchestrator=orchestrator, user_profile=profile)
response = delta.act("Create task list for project")
```

### Orchestrator (`core/orchestrator.py`)

#### Orchestrator Class

Coordinates multi-agent workflows and task routing.

```python
from core.orchestrator import Orchestrator

class Orchestrator:
    def __init__(self, knowledge, tasks, conversation, gui_callback=None, 
                 user_profile=None, resource_monitor=None):
        """
        Initialize the orchestrator.
        
        Args:
            knowledge: KnowledgeManager instance
            tasks: TaskManager instance
            conversation: ConversationManager instance
            gui_callback: Callback for GUI updates
            user_profile: User preferences
            resource_monitor: Resource monitoring instance
        """
```

**Methods:**

- `route_request(user_input, context=None)`: Route user request to appropriate agents
- `agent_communicate(from_agent, to_agent, message, context=None)`: Enable agent communication
- `backup_data(backup_dir="backups")`: Backup all system data
- `restore_data(backup_file)`: Restore data from backup
- `get_example_workflows()`: Get predefined workflow templates

**Example Usage:**
```python
from core.orchestrator import Orchestrator
from modules.knowledge import KnowledgeManager
from modules.tasks import TaskManager
from modules.conversation import ConversationManager

# Initialize managers
knowledge = KnowledgeManager()
tasks = TaskManager()
conversation = ConversationManager()

# Create orchestrator
orchestrator = Orchestrator(
    knowledge=knowledge,
    tasks=tasks,
    conversation=conversation,
    user_profile=user_profile
)

# Route a request
result = orchestrator.route_request("Research AI trends and create tasks")
print(result.success, result.result, result.steps)

# Backup data
backup_result = orchestrator.backup_data("my_backups")
print(f"Backup created: {backup_result}")
```

### Configuration (`core/config.py`)

#### ConfigManager Class

Manages system configuration with support for multiple sources.

```python
from core.config import ConfigManager, get_config

# Get global config instance
config = get_config()

# Or create custom instance
config_manager = ConfigManager("custom_config.json", profile="developer")
```

**Methods:**

- `load_config()`: Load configuration from all sources
- `save_config(config_file=None)`: Save current configuration
- `get_agent_config(agent_name)`: Get agent-specific configuration
- `get_model_config(model_name="default")`: Get AI model configuration
- `update_user_preference(key, value)`: Update user preference
- `create_profile(profile_name)`: Create new user profile
- `load_profile(profile_name)`: Load user profile
- `list_profiles()`: List available profiles

**Example Usage:**
```python
from core.config import ConfigManager

# Create config manager
config = ConfigManager()

# Get model configuration
model_config = config.get_model_config("llama2")
print(f"Model: {model_config.model_name}, Temp: {model_config.temperature}")

# Update user preference
config.update_user_preference("default_agent", "Beta")

# Save configuration
config.save_config("my_config.json")

# Create profile
config.create_profile("researcher")
config.load_profile("researcher")
```

## 📦 Modules

### Knowledge Management (`modules/knowledge.py`)

#### KnowledgeManager Class

Manages the Zettelkasten knowledge system.

```python
from modules.knowledge import KnowledgeManager

knowledge = KnowledgeManager()
```

**Methods:**

- `create_note(title, content, tags=None, links=None)`: Create new note
- `get_note(note_id)`: Retrieve note by ID
- `search_notes(query, search_type="full_text")`: Search notes
- `link_notes(note1_id, note2_id, link_type="related")`: Link notes
- `get_connections(note_id)`: Get note connections
- `export_notes(format="markdown")`: Export knowledge base
- `import_notes(file_path)`: Import notes from file

**Example Usage:**
```python
from modules.knowledge import KnowledgeManager

# Initialize knowledge manager
km = KnowledgeManager()

# Create a note
note_id = km.create_note(
    title="Machine Learning Basics",
    content="Machine learning is a subset of AI...",
    tags=["ai", "ml", "basics"],
    links=["neural-networks", "deep-learning"]
)

# Search notes
results = km.search_notes("machine learning")
for note in results:
    print(f"Found: {note.title}")

# Get connections
connections = km.get_connections(note_id)
print(f"Connected notes: {connections}")

# Export knowledge base
km.export_notes("my_knowledge_base.md")
```

### Task Management (`modules/tasks.py`)

#### TaskManager Class

Manages tasks, projects, and workflows.

```python
from modules.tasks import TaskManager, Task, TaskPriority, TaskStatus

task_manager = TaskManager()
```

**Methods:**

- `create_task(title, description=None, priority=TaskPriority.MEDIUM, 
               due_date=None, category=None)`: Create new task
- `get_task(task_id)`: Retrieve task by ID
- `update_task(task_id, **kwargs)`: Update task properties
- `delete_task(task_id)`: Delete task
- `list_tasks(status=None, category=None, priority=None)`: List tasks with filters
- `create_project(name, description=None)`: Create new project
- `add_task_to_project(task_id, project_id)`: Add task to project
- `get_task_statistics()`: Get task completion statistics
- `optimize_schedule()`: AI-powered schedule optimization

**Example Usage:**
```python
from modules.tasks import TaskManager, TaskPriority, TaskStatus
from datetime import datetime, timedelta

# Initialize task manager
tm = TaskManager()

# Create a task
task_id = tm.create_task(
    title="Complete project documentation",
    description="Write comprehensive documentation for the project",
    priority=TaskPriority.HIGH,
    due_date=datetime.now() + timedelta(days=7),
    category="work"
)

# Update task status
tm.update_task(task_id, status=TaskStatus.IN_PROGRESS)

# List high priority tasks
high_priority_tasks = tm.list_tasks(priority=TaskPriority.HIGH)
for task in high_priority_tasks:
    print(f"Task: {task.title}, Due: {task.due_date}")

# Get statistics
stats = tm.get_task_statistics()
print(f"Completed: {stats['completed']}, Pending: {stats['pending']}")

# Optimize schedule
optimized_schedule = tm.optimize_schedule()
print("Optimized schedule:", optimized_schedule)
```

### Conversation Management (`modules/conversation.py`)

#### ConversationManager Class

Manages conversation history and context.

```python
from modules.conversation import ConversationManager, Message, Session

conversation = ConversationManager()
```

**Methods:**

- `add_message(content, sender="user", session_id=None, 
               sentiment=None, quality=None)`: Add message to conversation
- `get_conversation(session_id=None, limit=None)`: Retrieve conversation history
- `search_conversations(query)`: Search conversation history
- `export_conversation(session_id, format="json")`: Export conversation
- `analyze_sentiment(text)`: Analyze message sentiment
- `get_user_preferences()`: Extract user preferences from conversations
- `create_session(name=None)`: Create new conversation session

**Example Usage:**
```python
from modules.conversation import ConversationManager

# Initialize conversation manager
cm = ConversationManager()

# Create a session
session_id = cm.create_session("Project Planning")

# Add messages
cm.add_message("I need to plan my project", "user", session_id)
cm.add_message("I'll help you create a comprehensive project plan", "alpha", session_id)

# Get conversation history
conversation = cm.get_conversation(session_id)
for msg in conversation:
    print(f"{msg.sender}: {msg.content}")

# Search conversations
results = cm.search_conversations("project planning")
for result in results:
    print(f"Found in session {result.session_id}: {result.content}")

# Export conversation
cm.export_conversation(session_id, "project_planning_chat.json")
```

### Resource Monitoring (`modules/resources.py`)

#### ResourceMonitor Class

Monitors system resources and performance.

```python
from modules.resources import ResourceMonitor, SystemMetrics

monitor = ResourceMonitor(Path("databases"))
```

**Methods:**

- `get_current_metrics()`: Get current system metrics
- `get_process_info(pid=None)`: Get process information
- `get_top_processes(n=10, sort_by="cpu")`: Get top processes by resource usage
- `monitor_ollama_status()`: Check Ollama model status
- `get_database_sizes()`: Get database file sizes
- `record_agent_response(agent_name, response_time, success=True)`: Record agent performance
- `get_agent_performance()`: Get agent performance statistics
- `check_alerts_and_throttle(metrics)`: Check for resource alerts
- `get_status_dashboard()`: Get comprehensive status dashboard
- `get_cli_status()`: Get CLI-friendly status string
- `log_performance(log_path="performance.log")`: Log performance data

**Example Usage:**
```python
from modules.resources import ResourceMonitor
from pathlib import Path

# Initialize resource monitor
rm = ResourceMonitor(Path("databases"))

# Get current metrics
metrics = rm.get_current_metrics()
print(f"CPU: {metrics.cpu_percent}%, Memory: {metrics.memory_percent}%")

# Check Ollama status
ollama_status = rm.monitor_ollama_status()
print(f"Ollama: {ollama_status['status']}")

# Record agent performance
rm.record_agent_response("Alpha", 1.5, success=True)

# Get performance statistics
perf_stats = rm.get_agent_performance()
for agent, stats in perf_stats.items():
    print(f"{agent}: {stats['avg_time']:.2f}s avg, {stats['success_rate']}% success")

# Get status dashboard
dashboard = rm.get_status_dashboard()
print(f"System Status: {dashboard['cpu_percent']}% CPU, {dashboard['memory_percent']}% Memory")

# Log performance
rm.log_performance("my_performance.log")
```

## 🖥️ Interfaces

### GUI Launcher (`interfaces/gui_launcher.py`)

#### RetroGUI Class

Retro terminal-style GUI interface.

```python
from interfaces.gui_launcher import launch_gui, RetroGUI

# Launch GUI
launch_gui(config=config, user_profile=user_profile)

# Or create custom instance
gui = RetroGUI()
gui.mainloop()
```

**Methods:**

- `append(text)`: Append text to panel
- `clear()`: Clear panel content
- `export_content()`: Export panel content to file
- `cycle_focus(current_panel_id)`: Cycle focus between panels
- `show_hints()`: Show help and hints
- `start_system()`: Start system
- `stop_system()`: Stop system

**Example Usage:**
```python
from interfaces.gui_launcher import launch_gui
from core.config import get_config

# Get configuration
config = get_config()

# Load user profile
with open("databases/user_profile.json", "r") as f:
    user_profile = json.load(f)

# Launch GUI
launch_gui(config=config, user_profile=user_profile)
```

### CLI Launcher (`interfaces/cli_launcher.py`)

#### CLI Interface Functions

Rich command-line interface with color-coded output.

```python
from interfaces.cli_launcher import launch_cli, main

# Launch CLI
launch_cli(config=config, user_profile=user_profile)

# Or run main function
main()
```

**Available Commands:**
- `/help`: Show help menu
- `/status`: System status
- `/examples`: Example workflows
- `/backup`: Create backup
- `/restore`: Restore from backup
- `/clear`: Clear chat
- `/profile`: User profile management

**Example Usage:**
```python
from interfaces.cli_launcher import launch_cli
from core.config import get_config

# Get configuration
config = get_config()

# Load user profile
with open("databases/user_profile.json", "r") as f:
    user_profile = json.load(f)

# Launch CLI
launch_cli(config=config, user_profile=user_profile)
```

## 🔧 Integration Examples

### Complete System Setup

```python
from core.config import get_config
from core.orchestrator import Orchestrator
from modules.knowledge import KnowledgeManager
from modules.tasks import TaskManager
from modules.conversation import ConversationManager
from modules.resources import ResourceMonitor
from pathlib import Path
import json

# Load configuration and user profile
config = get_config()
with open("databases/user_profile.json", "r") as f:
    user_profile = json.load(f)

# Initialize managers
knowledge = KnowledgeManager()
tasks = TaskManager()
conversation = ConversationManager()
resource_monitor = ResourceMonitor(Path("databases"))

# Create orchestrator
orchestrator = Orchestrator(
    knowledge=knowledge,
    tasks=tasks,
    conversation=conversation,
    user_profile=user_profile,
    resource_monitor=resource_monitor
)

# Route a complex request
result = orchestrator.route_request(
    "Research quantum computing, create notes, and plan a project"
)

if result.success:
    print("Success:", result.result)
    for step in result.steps:
        print(f"Step: {step['step']}, Agent: {step.get('agent', 'N/A')}")
else:
    print("Error:", result.error)
```

### Custom Agent Development

```python
from core.agents import AgentBase
from modules.resources import track_agent_performance

class CustomAgent(AgentBase):
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        super().__init__("Custom", orchestrator, user_profile, resource_monitor)
    
    @track_agent_performance("Custom", ResourceMonitor(Path("databases")))
    def act(self, input_data, context=None):
        try:
            # Custom logic here
            if "research" in input_data.lower():
                # Delegate to Beta
                response = self.send_message("Beta", input_data, context)
                return f"Research delegated to Beta: {response}"
            elif "task" in input_data.lower():
                # Delegate to Delta
                response = self.send_message("Delta", input_data, context)
                return f"Task delegated to Delta: {response}"
            else:
                return self.adapt_to_user(f"Custom agent processed: {input_data}")
        except Exception as e:
            return self.handle_error(e, context)

# Usage
custom_agent = CustomAgent(orchestrator=orchestrator, user_profile=user_profile)
response = custom_agent.act("Research AI trends")
print(response)
```

### Performance Monitoring Integration

```python
from modules.resources import ResourceMonitor
from core.config import get_config
import time

# Initialize monitor
monitor = ResourceMonitor(Path("databases"))

# Monitor system during operation
def monitored_operation():
    start_time = time.time()
    
    # Your operation here
    result = some_operation()
    
    # Record performance
    elapsed = time.time() - start_time
    monitor.record_agent_response("CustomOperation", elapsed, success=True)
    
    return result

# Get performance dashboard
dashboard = monitor.get_status_dashboard()
print("System Health:", dashboard)

# Check for alerts
metrics = monitor.get_current_metrics()
alerts, throttle, reason = monitor.check_alerts_and_throttle(metrics)
if alerts:
    print("Alerts:", alerts)
if throttle:
    print(f"Throttling active due to {reason}")
```

## 📊 Error Handling

### Common Error Patterns

```python
# Agent error handling
try:
    response = agent.act(input_data)
except Exception as e:
    error_response = agent.handle_error(e)
    print(f"Agent error: {error_response}")

# Orchestrator error handling
result = orchestrator.route_request(user_input)
if not result.success:
    print(f"Orchestration failed: {result.error}")
    # Fallback to Alpha
    fallback_result = orchestrator.agents[AgentRole.ALPHA].act(user_input)

# Resource monitoring error handling
try:
    metrics = monitor.get_current_metrics()
except Exception as e:
    print(f"Monitoring error: {e}")
    # Use default metrics
    metrics = SystemMetrics(timestamp=datetime.now(), cpu_percent=0, ...)
```

## 🔮 Advanced Usage

### Custom Workflow Creation

```python
# Define custom workflow
class CustomWorkflow:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def execute(self, user_input):
        steps = []
        
        # Step 1: Research
        beta_response = self.orchestrator.agents[AgentRole.BETA].act(user_input)
        steps.append({"step": "research", "agent": "Beta", "result": beta_response})
        
        # Step 2: Knowledge organization
        gamma_response = self.orchestrator.agents[AgentRole.GAMMA].act(beta_response)
        steps.append({"step": "knowledge", "agent": "Gamma", "result": gamma_response})
        
        # Step 3: Task creation
        delta_response = self.orchestrator.agents[AgentRole.DELTA].act(gamma_response)
        steps.append({"step": "tasks", "agent": "Delta", "result": delta_response})
        
        # Step 4: Coordination
        alpha_response = self.orchestrator.agents[AgentRole.ALPHA].act(delta_response)
        steps.append({"step": "coordination", "agent": "Alpha", "result": alpha_response})
        
        return alpha_response, steps

# Usage
workflow = CustomWorkflow(orchestrator)
result, steps = workflow.execute("Create a learning plan for AI")
```

### Plugin System Integration

```python
# Plugin interface
class PluginInterface:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def register_plugin(self, plugin_name, plugin_class):
        # Register custom plugin
        pass
    
    def execute_plugin(self, plugin_name, input_data):
        # Execute registered plugin
        pass

# Example plugin
class WeatherPlugin:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def get_weather(self, location):
        # Weather API integration
        return f"Weather for {location}: Sunny, 25°C"
    
    def act(self, input_data):
        if "weather" in input_data.lower():
            location = extract_location(input_data)
            return self.get_weather(location)
        return None
```

---

**"The API is your gateway to the future. Use it wisely, and you'll unlock the full potential of multi-agent AI assistance."**

— Prof. B3, Temporal Research Institute, 2073

*For user documentation, see [User Guide](USER_GUIDE.md). For troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).* 