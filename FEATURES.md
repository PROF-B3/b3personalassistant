# 🚀 B3PersonalAssistant - New Features

This document describes the enhanced intelligence and automation features that transform B3PersonalAssistant into a comprehensive all-in-one intelligent assistant.

## 📋 Table of Contents

1. [Context Management](#context-management)
2. [Semantic Search](#semantic-search)
3. [Proactive Agent](#proactive-agent)
4. [Workflow Automation](#workflow-automation)
5. [Multimodal Processing](#multimodal-processing)
6. [Installation](#installation)
7. [Quick Start](#quick-start)

---

## 1. Context Management 🧠

**Location**: `core/context_manager.py`

### Overview

The Context Manager provides persistent memory across conversations, enabling the assistant to remember previous interactions, user preferences, and ongoing work.

### Features

- **Short-term memory**: Current conversation context
- **Long-term memory**: User preferences and important facts
- **Context switching**: Separate contexts for work, personal, projects
- **Time-based expiration**: Automatic cleanup of old context
- **Priority levels**: Mark important context with higher priority
- **Fast in-memory cache**: Quick access to frequently used context

### Usage

```python
from core.context_manager import ContextManager, ContextType, ContextPriority

# Initialize
context = ContextManager()

# Set context
context.set(
    key="current_project",
    value="Website Redesign",
    context_type=ContextType.WORK,
    priority=ContextPriority.HIGH,
    expires_in=timedelta(hours=8)
)

# Get context
project = context.get("current_project", context_type=ContextType.WORK)

# Get relevant context for AI
relevant = context.get_relevant_context(
    context_types=[ContextType.WORK, ContextType.PROJECT],
    min_priority=ContextPriority.MEDIUM,
    limit=10
)

# Format for AI prompt
context_text = context.format_for_ai(limit=10)
```

### Benefits

✅ **Coherent conversations**: Assistant remembers what you discussed
✅ **Personalization**: Learns your preferences over time
✅ **Context-aware responses**: Answers based on current work context
✅ **Resume where left off**: Pick up conversations days later

---

## 2. Semantic Search 🔍

**Location**: `modules/semantic_search.py`

### Overview

Semantic Search enables searching by meaning rather than keywords using embeddings, dramatically improving knowledge base discoverability.

### Features

- **Meaning-based search**: Find content by concept, not exact words
- **Cross-source search**: Search notes, tasks, conversations together
- **Similarity detection**: Find related content automatically
- **Multiple embedding models**: Ollama, Sentence Transformers, OpenAI
- **Fast cosine similarity**: Efficient nearest neighbor search
- **Incremental indexing**: Add content on-the-fly

### Usage

```python
from modules.semantic_search import SemanticSearchEngine

# Initialize
search = SemanticSearchEngine(
    embedding_model="ollama",
    model_name="nomic-embed-text"
)

# Index content
search.index_text(
    content="Python is a high-level programming language",
    source="note",
    source_id="note_123",
    metadata={"tags": ["programming", "python"]}
)

# Search by meaning
results = search.search(
    query="what programming languages are easy to learn?",
    top_k=5,
    min_similarity=0.5
)

for result in results:
    print(f"{result.similarity:.2f}: {result.content}")

# Find similar content
similar = search.find_similar(
    content="I want to learn web development",
    top_k=3
)

# Batch indexing
items = [
    ("Text 1", "note", "note_1", {"tag": "AI"}),
    ("Text 2", "note", "note_2", None),
]
success, failed = search.index_batch(items)
```

### Benefits

✅ **Find what you can't remember**: Search by concept, not keywords
✅ **Discover connections**: Find related notes automatically
✅ **Better knowledge retrieval**: AI gets more relevant context
✅ **Works across languages**: Semantic similarity transcends exact words

---

## 3. Proactive Agent 🎯

**Location**: `modules/agents/proactive_agent.py`

### Overview

The Proactive Agent learns from your behavior patterns and makes intelligent suggestions before you ask.

### Features

- **Pattern learning**: Time-based, context-based, sequence patterns
- **Smart suggestions**: Predict what you need next
- **Productivity analysis**: Track and optimize your workflows
- **Missing pattern detection**: Remind about tasks you usually do
- **Feedback learning**: Improves from your responses
- **Anomaly detection**: Notice unusual behavior

### Usage

```python
from modules.agents.proactive_agent import ProactiveAgent, Suggestion

# Initialize
agent = ProactiveAgent()

# Record actions (happens automatically)
agent.record_action(
    action="checked email",
    context="morning",
    metadata={"duration": 120}
)

# Get suggestions
suggestions = agent.get_suggestions(current_context="morning")

for suggestion in suggestions:
    print(f"{suggestion.title}")
    print(f"  {suggestion.description}")
    print(f"  Confidence: {suggestion.confidence:.0%}")

# Provide feedback
agent.record_feedback(
    suggestion_title="Time for checked email?",
    accepted=True
)

# Analyze productivity
analysis = agent.analyze_productivity(days=7)
print(f"Most productive day: {analysis['most_productive_day']}")
print(f"Peak hour: {analysis['peak_productivity_hour']}")

# View learned patterns
patterns = agent.get_learned_patterns(min_confidence=0.5)
for pattern in patterns:
    print(f"{pattern.description} (confidence: {pattern.confidence:.0%})")
```

### Benefits

✅ **Anticipates needs**: Suggests actions before you think of them
✅ **Learns routines**: Understands your daily/weekly patterns
✅ **Improves over time**: Gets better with more usage
✅ **Productivity insights**: Understand how you work

---

## 4. Workflow Automation ⚙️

**Location**: `modules/workflow_engine.py`

### Overview

Workflow Automation enables creating automated workflows with triggers and actions - like IFTTT for your personal assistant.

### Features

- **Time-based triggers**: Run workflows on schedule (cron-like)
- **Event-based triggers**: React to events (new email, task created)
- **Condition-based triggers**: If-this-then-that logic
- **Multi-step actions**: Chain multiple actions together
- **Workflow templates**: Pre-built workflows for common tasks
- **Execution history**: Track what workflows did
- **Error handling**: Retry failed actions

### Usage

```python
from modules.workflow_engine import (
    WorkflowEngine, Workflow, Trigger, Action,
    TriggerType, ActionType
)

# Initialize
engine = WorkflowEngine()

# Create workflow
workflow = Workflow(
    name="Morning Routine",
    description="Automated morning tasks",
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
            action_type=ActionType.CREATE_TASK.value,
            config={"title": "Review daily tasks", "priority": "high"},
            description="Create daily review task"
        ),
        Action(
            action_type=ActionType.SEND_NOTIFICATION.value,
            config={"title": "Good Morning!", "message": "Here's your daily summary"},
            description="Send greeting"
        )
    ]
)

# Save workflow
workflow_id = engine.create_workflow(workflow)

# Execute manually
engine.execute_workflow(workflow_id, trigger_reason="manual_test")

# List all workflows
workflows = engine.list_workflows(enabled_only=True)

# Get workflow templates
templates = engine.get_templates(category="productivity")
```

### Built-in Templates

1. **Morning Email Summary**: Daily email digest
2. **Weekly Review Reminder**: Friday afternoon reminder
3. **High Priority Email Alert**: Instant alerts for important emails

### Benefits

✅ **Automate repetitive tasks**: Set it and forget it
✅ **Never miss important events**: Automatic reminders and alerts
✅ **Save time**: Eliminate manual routine tasks
✅ **Customize your flow**: Create workflows that fit your needs

---

## 5. Multimodal Processing 📷🎵📄

**Location**: `modules/agents/multimodal_agent.py`

### Overview

The Multimodal Agent processes images, audio, PDFs, and documents, enabling the assistant to understand multiple media types.

### Features

- **Image understanding**: Describe images using vision models
- **OCR**: Extract text from images
- **Audio transcription**: Convert speech to text
- **PDF processing**: Extract text and structure
- **Document parsing**: Read various document formats
- **Auto-detection**: Automatically detect and process file types

### Usage

```python
from modules.agents.multimodal_agent import MultimodalAgent

# Initialize
agent = MultimodalAgent(ollama_vision_model="llava")

# Process image
result = agent.process_image("screenshot.png", extract_text=True, describe=True)
print(f"OCR Text: {result.extracted_text}")
print(f"Description: {result.summary}")

# Process audio
result = agent.process_audio("meeting.mp3")
print(f"Transcription: {result.extracted_text}")

# Process PDF
result = agent.process_pdf("report.pdf")
print(f"Pages: {result.metadata['page_count']}")
print(f"Text: {result.extracted_text}")

# Auto-detect and process any file
result = agent.process_file("unknown_file.pdf")
print(f"Type: {result.content_type}")

# Custom image analysis
response = agent.describe_image_with_prompt(
    "diagram.png",
    "What is this diagram showing? Explain the relationships."
)
print(response)
```

### Supported Formats

| Type | Formats | Features |
|------|---------|----------|
| **Images** | PNG, JPG, GIF, BMP | OCR, description, custom prompts |
| **Audio** | MP3, WAV, M4A | Transcription, speaker detection |
| **PDFs** | PDF | Text extraction, structure analysis |
| **Documents** | TXT, MD, HTML | Text parsing, metadata |

### Benefits

✅ **Understand screenshots**: Extract text and describe images
✅ **Transcribe meetings**: Convert audio recordings to text
✅ **Parse documents**: Extract information from PDFs
✅ **Unified interface**: Process any media type the same way

---

## Installation

### Basic Installation

```bash
# Clone repository
git clone https://github.com/PROF-B3/b3personalassistant.git
cd b3personalassistant

# Install core dependencies
pip install -e .
```

### Install Feature Modules

```bash
# For multimodal support (images, audio, PDFs)
pip install -e ".[multimodal]"

# For web integrations (Gmail, Calendar, Web API)
pip install -e ".[integrations]"

# Install everything
pip install -e ".[full,multimodal,integrations]"
```

### External Dependencies

**For OCR (Tesseract)**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**For Ollama (required)**:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama2
ollama pull nomic-embed-text
ollama pull llava  # For vision
```

---

## Quick Start

### 1. Set Up Context Management

```python
from core.context_manager import ContextManager, ContextPriority

context = ContextManager()

# Store user preferences
context.set("user_name", "Alice", priority=ContextPriority.HIGH)
context.set("preferred_tone", "professional", priority=ContextPriority.HIGH)
context.set("current_project", "Website Redesign")

# Get context for AI
ai_context = context.format_for_ai()
print(ai_context)
```

### 2. Enable Semantic Search

```python
from modules.semantic_search import SemanticSearchEngine

search = SemanticSearchEngine()

# Index your existing knowledge base
from pathlib import Path

for note_file in Path("knowledge_base").rglob("*.md"):
    content = note_file.read_text()
    search.index_text(
        content=content,
        source="note",
        source_id=note_file.stem
    )

# Search semantically
results = search.search("How can I improve productivity?", top_k=5)
for result in results:
    print(f"{result.similarity:.0%}: {result.content[:100]}...")
```

### 3. Start Learning Patterns

```python
from modules.agents.proactive_agent import ProactiveAgent

agent = ProactiveAgent()

# Record your actions (do this automatically)
agent.record_action("checked email", context="morning")
agent.record_action("reviewed tasks", context="morning")
agent.record_action("wrote code", context="work")

# Get suggestions
suggestions = agent.get_suggestions(current_context="morning")
for s in suggestions:
    print(f"💡 {s.title}: {s.description}")
```

### 4. Create Your First Workflow

```python
from modules.workflow_engine import *

engine = WorkflowEngine()

# Use a template
templates = engine.get_templates()
template = templates[0]  # Morning Email Summary

# Create from template
workflow = Workflow(
    name=template["name"],
    description=template["description"],
    trigger=Trigger(**template["template_data"]["trigger"]),
    actions=[Action(**a) for a in template["template_data"]["actions"]]
)

workflow_id = engine.create_workflow(workflow)
print(f"Created workflow: {workflow_id}")
```

### 5. Process Multimodal Content

```python
from modules.agents.multimodal_agent import MultimodalAgent

agent = MultimodalAgent()

# Process a screenshot
result = agent.process_image("screenshot.png", extract_text=True)
if result.extracted_text:
    # Add to knowledge base
    search.index_text(
        content=result.extracted_text,
        source="screenshot",
        source_id="screenshot_001"
    )
```

---

## Integration with Existing System

All new features integrate seamlessly with the existing B3PersonalAssistant architecture:

### With Orchestrator

```python
# Orchestrator can use context for better responses
context = ContextManager()
current_context = context.format_for_ai()

response = orchestrator.process_request(
    user_query,
    additional_context=current_context
)
```

### With Knowledge Base

```python
# Enhance Zettelkasten with semantic search
search = SemanticSearchEngine()

# Index all notes
for note in knowledge_manager.get_all_notes():
    search.index_text(note.content, "note", note.id)

# Search semantically instead of by tags
results = search.search(user_query)
```

### With Task Manager

```python
# Proactive agent creates task suggestions
suggestions = proactive_agent.get_suggestions()

for suggestion in suggestions:
    if suggestion.suggestion_type == "task":
        # Create actual task
        task_manager.create_task(
            title=suggestion.title,
            description=suggestion.description,
            priority=suggestion.priority
        )
```

---

## Performance Considerations

- **Context Manager**: Uses in-memory cache for hot data, database for persistence
- **Semantic Search**: Uses NumPy for fast similarity computation; consider using FAISS for large datasets (>100K items)
- **Proactive Agent**: Patterns updated asynchronously; minimal overhead
- **Workflow Engine**: Lightweight scheduler; actions run in separate threads
- **Multimodal Agent**: Processing happens on-demand; results can be cached

---

## Next Steps

1. **Explore the code**: Each module has comprehensive docstrings and examples
2. **Check tests**: See `tests/test_*` for usage examples
3. **Read the docs**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guide
4. **Try examples**: Run the `if __name__ == "__main__"` sections in each module
5. **Customize**: Extend action handlers, add new workflow templates, train custom models

---

## Coming Soon 🚧

- ✅ Context Management
- ✅ Semantic Search
- ✅ Proactive Agent
- ✅ Workflow Automation
- ✅ Multimodal Processing
- 🚧 FastAPI Web Interface
- 🚧 Email Integration (Gmail API)
- 🚧 Calendar Integration (Google Calendar)
- 🚧 Voice Input/Output
- 🚧 Knowledge Graph Visualization
- 🚧 Mobile PWA

---

## Support

- **Documentation**: See module docstrings and inline comments
- **Issues**: Report bugs on [GitHub Issues](https://github.com/PROF-B3/b3personalassistant/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Built with ❤️ by the B3PersonalAssistant Team**
