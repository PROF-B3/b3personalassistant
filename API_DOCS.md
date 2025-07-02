# 🔌 API Documentation

> **Developer reference for B3PersonalAssistant**

## 📋 Table of Contents

1. [Core Classes](#core-classes)
2. [Agent System](#agent-system)
3. [Modules](#modules)
4. [Database](#database)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)

## 🏗️ Core Classes

### Orchestrator

The central coordination hub for the multi-agent system.

```python
from core.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator()

# Process requests
response = orchestrator.process_request("Research quantum computing")
print(response)

# Get specific agent
beta = orchestrator.get_agent("beta")
research = beta.research("AI trends")
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `process_request()` | Route request to appropriate agent | `request: str` | `str` |
| `get_agent()` | Get specific agent instance | `agent_name: str` | `BaseAgent` |
| `get_all_agents()` | Get all agent instances | None | `dict` |
| `get_system_status()` | Get overall system status | None | `dict` |

### ConfigManager

Manages system configuration and environment variables.

```python
from core.config import ConfigManager

# Initialize config
config = ConfigManager()

# Get configuration values
ollama_url = config.get("OLLAMA_BASE_URL")
model = config.get("OLLAMA_MODEL")
debug_mode = config.get_bool("DEBUG_MODE")

# Set configuration
config.set("CUSTOM_SETTING", "value")
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get()` | Get string configuration | `key: str, default=None` | `str` |
| `get_int()` | Get integer configuration | `key: str, default=0` | `int` |
| `get_bool()` | Get boolean configuration | `key: str, default=False` | `bool` |
| `set()` | Set configuration value | `key: str, value: str` | None |

## 🤖 Agent System

### BaseAgent

Base class for all agents with common functionality.

```python
from core.agents import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name, role, model):
        super().__init__(name, role, model)
    
    def process(self, request):
        """Process a request"""
        return f"Processed: {request}"
    
    def get_status(self):
        """Get agent status"""
        return {"status": "active", "requests_processed": 100}
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `process()` | Process a request | `request: str` | `str` |
| `get_status()` | Get agent status | None | `dict` |
| `get_capabilities()` | Get agent capabilities | None | `list` |
| `update_model()` | Update AI model | `model: str` | None |

### Agent Instances

Each agent has specialized methods:

```python
# Beta (Research Agent)
beta = orchestrator.get_agent("beta")
research = beta.research("quantum computing")
analysis = beta.analyze_data(data)

# Gamma (Knowledge Agent)
gamma = orchestrator.get_agent("gamma")
note = gamma.create_note("Machine Learning Basics")
links = gamma.find_connections("neural networks")

# Delta (Task Agent)
delta = orchestrator.get_agent("delta")
task = delta.create_task("Complete project", due_date="2024-02-15")
project = delta.create_project("Website Redesign")

# Epsilon (Creative Agent)
epsilon = orchestrator.get_agent("epsilon")
idea = epsilon.brainstorm("video themes")
creative = epsilon.generate_content("futuristic text")

# Zeta (Code Agent)
zeta = orchestrator.get_agent("zeta")
review = zeta.review_code(python_code)
optimized = zeta.optimize_code(python_code)

# Eta (Evolution Agent)
eta = orchestrator.get_agent("eta")
improvements = eta.suggest_improvements()
metrics = eta.get_performance_metrics()
```

## 📦 Modules

### VideoProcessor

Handles AI-powered video processing and editing.

```python
from modules.video_processing import VideoProcessor

# Initialize processor
processor = VideoProcessor()

# Basic video processing
processor.process_video(
    input_path="input.mp4",
    output_dir="output/",
    theme="neon_cyberpunk",
    segment_duration=60
)

# Advanced processing with custom config
processor.process_video(
    input_path="video.mp4",
    output_dir="output/",
    theme="custom",
    custom_config={
        "colors": ["cyan", "magenta"],
        "effects": ["glitch", "neon"],
        "text_style": "futuristic",
        "segment_duration": 30,
        "fps": 30
    }
)
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `process_video()` | Process video with AI enhancements | `input_path, output_dir, theme, **kwargs` | `list` |
| `detect_scenes()` | Detect video scenes | `video_path: str` | `list` |
| `generate_overlay()` | Generate text overlay | `text: str, theme: str` | `str` |
| `apply_effects()` | Apply visual effects | `video_path: str, effects: list` | `str` |

### ConversationManager

Manages conversation history and context.

```python
from modules.conversation import ConversationManager

# Initialize conversation manager
conversation = ConversationManager()

# Add messages
conversation.add_message("user", "Hello, how are you?")
conversation.add_message("alpha", "I'm doing well, thank you!")

# Get conversation history
history = conversation.get_history()
context = conversation.get_context()

# Clear conversation
conversation.clear()
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `add_message()` | Add message to history | `sender: str, content: str` | None |
| `get_history()` | Get conversation history | `limit: int = 50` | `list` |
| `get_context()` | Get conversation context | None | `str` |
| `clear()` | Clear conversation history | None | None |

### TaskManager

Manages tasks and project organization.

```python
from modules.tasks import TaskManager

# Initialize task manager
tasks = TaskManager()

# Create tasks
task_id = tasks.create_task(
    title="Complete project",
    description="Finish the website redesign",
    due_date="2024-02-15",
    priority="high"
)

# Update task
tasks.update_task(task_id, status="in_progress")

# Get tasks
all_tasks = tasks.get_all_tasks()
project_tasks = tasks.get_tasks_by_project("Website Redesign")
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `create_task()` | Create new task | `title, description, due_date, priority` | `int` |
| `update_task()` | Update task | `task_id, **kwargs` | `bool` |
| `get_all_tasks()` | Get all tasks | None | `list` |
| `get_tasks_by_project()` | Get tasks by project | `project: str` | `list` |

### KnowledgeManager

Manages Zettelkasten knowledge system.

```python
from modules.knowledge import KnowledgeManager

# Initialize knowledge manager
knowledge = KnowledgeManager()

# Create notes
note_id = knowledge.create_note(
    title="Machine Learning Basics",
    content="Machine learning is a subset of AI...",
    tags=["ai", "ml", "algorithms"]
)

# Search notes
results = knowledge.search("neural networks")
tagged_notes = knowledge.get_notes_by_tag("ai")

# Link concepts
knowledge.create_link("machine learning", "artificial intelligence")
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `create_note()` | Create new note | `title, content, tags` | `int` |
| `search()` | Search notes | `query: str` | `list` |
| `create_link()` | Link concepts | `source: str, target: str` | `bool` |
| `get_notes_by_tag()` | Get notes by tag | `tag: str` | `list` |

## 🗄️ Database

### DatabaseManager

Manages SQLAlchemy database operations.

```python
from databases.manager import DatabaseManager

# Initialize database manager
db = DatabaseManager()

# Get database stats
stats = db.get_database_stats()
print(f"Tables: {stats['tables']}")
print(f"Records: {stats['total_records']}")

# Backup database
db.backup_database("backup_20240101.db")

# Restore database
db.restore_database("backup_20240101.db")
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_database_stats()` | Get database statistics | None | `dict` |
| `backup_database()` | Create database backup | `filename: str` | `bool` |
| `restore_database()` | Restore from backup | `filename: str` | `bool` |
| `get_session()` | Get database session | None | `Session` |

### Database Models

```python
from databases.models import Conversation, Task, Note, Agent

# Create records
conversation = Conversation(
    user_id="user123",
    agent_name="alpha",
    message="Hello",
    timestamp=datetime.now()
)

task = Task(
    title="Complete project",
    description="Finish the website redesign",
    status="pending",
    priority="high",
    due_date=datetime(2024, 2, 15)
)

note = Note(
    title="Machine Learning",
    content="Machine learning is...",
    tags=["ai", "ml"]
)
```

## 🔧 Configuration

### Environment Variables

```bash
# AI Model Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OPENAI_API_KEY=your_key_here

# System Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=5

# Video Processing
VIDEO_SEGMENT_DURATION=60
VIDEO_FPS=30
VIDEO_QUALITY=high

# Database
DATABASE_PATH=databases/b3_assistant.db
BACKUP_ENABLED=true
```

### Agent Configuration

```json
{
  "agents": {
    "alpha": {
      "role": "Chief Assistant & Coordinator",
      "model": "mixtral:latest",
      "capabilities": ["coordination", "planning", "communication"]
    },
    "beta": {
      "role": "Research Analyst & Data Specialist",
      "model": "llama2:latest",
      "capabilities": ["research", "analysis", "investigation"]
    }
  }
}
```

## 📊 Monitoring

### HealthChecker

Monitors system health and performance.

```python
from monitoring.health_check import HealthChecker

# Initialize health checker
checker = HealthChecker()

# Check all systems
status = checker.check_all()
print(f"Overall status: {status['overall_status']}")

# Check specific metrics
cpu_usage = checker.get_cpu_usage()
memory_usage = checker.get_memory_usage()
disk_usage = checker.get_disk_usage()

# Check agent status
agent_status = checker.get_agent_status()
```

**Key Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `check_all()` | Check all systems | None | `dict` |
| `get_cpu_usage()` | Get CPU usage | None | `float` |
| `get_memory_usage()` | Get memory usage | None | `float` |
| `get_disk_usage()` | Get disk usage | None | `float` |
| `get_agent_status()` | Get agent status | None | `dict` |

### Logging

```python
import logging
from core.config import ConfigManager

# Configure logging
config = ConfigManager()
logging.basicConfig(
    level=getattr(logging, config.get("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/b3_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("B3PersonalAssistant started")
```

## 🚀 Usage Examples

### Basic Integration

```python
from core.orchestrator import Orchestrator
from core.config import ConfigManager

# Initialize system
config = ConfigManager()
orchestrator = Orchestrator()

# Process user request
def handle_user_request(request):
    """Handle user request through orchestrator"""
    try:
        response = orchestrator.process_request(request)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Example usage
result = handle_user_request("Research quantum computing")
print(result["response"])
```

### Custom Agent

```python
from core.agents import BaseAgent

class CustomResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_research", "Custom Research", "llama2")
    
    def research(self, topic):
        """Custom research method"""
        # Implement custom research logic
        return f"Custom research on {topic}"
    
    def analyze(self, data):
        """Custom analysis method"""
        # Implement custom analysis logic
        return f"Analysis of {data}"

# Register custom agent
orchestrator.register_agent(CustomResearchAgent())
```

### Video Processing Pipeline

```python
from modules.video_processing import VideoProcessor
from modules.knowledge import KnowledgeManager

def create_video_with_knowledge(video_path, topic):
    """Create video with knowledge integration"""
    
    # Get knowledge about topic
    knowledge = KnowledgeManager()
    notes = knowledge.search(topic)
    
    # Process video with knowledge context
    processor = VideoProcessor()
    result = processor.process_video(
        input_path=video_path,
        output_dir="output/",
        theme="neon_cyberpunk",
        knowledge_context=notes
    )
    
    return result
```

---

**For more examples and advanced usage, see the [User Guide](USER_GUIDE.md) and [Quick Start Guide](QUICK_START.md).** 