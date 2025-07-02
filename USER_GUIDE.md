# 👤 User Guide

> **Complete guide to using B3PersonalAssistant effectively**

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Agent System](#agent-system)
3. [Core Features](#core-features)
4. [Video Processing](#video-processing)
5. [Knowledge Management](#knowledge-management)
6. [Task Management](#task-management)
7. [Configuration](#configuration)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### First Launch

```bash
# Start the assistant
python run_assistant.py

# Or use CLI interface
python -m interfaces.cli_launcher
```

### Initial Setup

The system will guide you through:
1. **Profile Creation**: Name, work style, interests
2. **Interface Selection**: GUI or CLI
3. **Database Initialization**: Knowledge base setup
4. **Agent Introduction**: Meet your 7 AI assistants

### Basic Commands

```
/help          - Show help menu
/status        - System status
/agents        - List all agents
/clear         - Clear chat
/exit          - Exit system
```

## 🤖 Agent System

### Meet Your Agents

| Agent | Role | Best For |
|-------|------|----------|
| **Alpha (Α)** | Chief Coordinator | General assistance, coordination |
| **Beta (Β)** | Research Analyst | Research, data analysis, investigations |
| **Gamma (Γ)** | Knowledge Manager | Information organization, Zettelkasten |
| **Delta (Δ)** | Task Coordinator | Task management, scheduling, optimization |
| **Epsilon (Ε)** | Creative Assistant | Creative tasks, brainstorming, ideation |
| **Zeta (Ζ)** | Code Architect | Code review, optimization, architecture |
| **Eta (Η)** | Evolution Engineer | System improvement, capability enhancement |

### Agent Communication

Agents work together automatically:

```python
# Example: Research workflow
User: "Research quantum computing applications"

Alpha: "I'll coordinate this research project."
Beta: "Gathering information on quantum computing..."
Gamma: "Organizing findings in your knowledge base..."
Delta: "Creating follow-up tasks for deeper exploration..."
Alpha: "Research complete. Here's your comprehensive summary..."
```

### Direct Agent Interaction

```python
# Talk to specific agents
"Beta, research the latest AI trends"
"Gamma, organize my notes on machine learning"
"Delta, create a project plan for my website"
"Zeta, review this Python code"
```

## 🎯 Core Features

### Multi-Agent Collaboration

The system automatically routes requests to the most appropriate agent(s):

```python
# Complex request handled by multiple agents
User: "I need to create a video about AI trends with research and planning"

Alpha: Coordinates the project
Beta: Researches AI trends
Gamma: Organizes information
Delta: Creates project timeline
Epsilon: Handles creative aspects
Zeta: Manages technical requirements
Eta: Monitors and optimizes the process
```

### Intelligent Routing

The system learns your preferences and routes requests accordingly:

- **Research requests** → Beta
- **Knowledge organization** → Gamma  
- **Task management** → Delta
- **Creative projects** → Epsilon
- **Code/technical** → Zeta
- **System improvements** → Eta
- **General coordination** → Alpha

## 🎬 Video Processing

### Basic Video Workflow

```python
from modules.video_processing import VideoProcessor

# Initialize processor
processor = VideoProcessor()

# Process a video
processor.process_video(
    input_path="input.mp4",
    output_dir="output/",
    theme="neon_cyberpunk",
    segment_duration=60
)
```

### Available Themes

- **neon_cyberpunk**: Futuristic neon aesthetics
- **green_solarpunk**: Eco-friendly, organic themes
- **blue_tech**: Clean, professional tech look
- **purple_mystic**: Mystical, ethereal effects
- **custom**: Create your own theme

### Advanced Video Features

```python
# Custom video processing
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

### Collaborative Video Workflow

```python
# Full collaborative workflow
from demo_video_workflow import create_futuristic_remix

# Create AI-enhanced video segments
result = create_futuristic_remix("input_video.mp4")
print(f"Created {len(result)} segments with AI enhancements")
```

## 📚 Knowledge Management

### Zettelkasten System

The system uses a sophisticated knowledge management approach:

```python
# Create a note
"Gamma, take notes on machine learning"

# Search knowledge base
"Gamma, search for information about neural networks"

# Link concepts
"Gamma, link machine learning to artificial intelligence"
```

### Knowledge Commands

```
/knowledge create "Machine Learning Basics"
/knowledge search "neural networks"
/knowledge link "ML" "AI"
/knowledge tags "machine-learning, ai, algorithms"
/knowledge export "ml_notes.txt"
```

### Knowledge Organization

The system automatically:
- **Creates connections** between related concepts
- **Suggests tags** for better organization
- **Links to existing knowledge** when relevant
- **Maintains a knowledge graph** of your information

## ✅ Task Management

### Creating Tasks

```python
# Simple task creation
"Delta, I need to finish my project by Friday"

# Complex project planning
"Delta, create a project plan for my website redesign"
```

### Task Commands

```
/tasks list                    # List all tasks
/tasks add "New task"          # Add task
/tasks complete 1              # Mark complete
/tasks priority 1 high         # Set priority
/tasks due 1 2024-02-15        # Set due date
/tasks project "Website"       # Group by project
```

### Project Management

```python
# Create a project
"Delta, create a project called 'Website Redesign'"

# Add tasks to project
"Delta, add 'Design homepage' to Website Redesign project"

# View project status
"Delta, show me the status of Website Redesign project"
```

### Task Optimization

Delta automatically:
- **Estimates time** for tasks
- **Suggests priorities** based on deadlines
- **Creates dependencies** between related tasks
- **Optimizes schedules** for maximum efficiency

## 🔧 Configuration

### Environment Configuration

```bash
# Copy example configuration
cp config.env.example .env

# Edit configuration
nano .env
```

### Key Settings

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

### User Profiles

```python
# Create different profiles
/profile create developer
/profile create researcher
/profile create student

# Switch profiles
/profile switch developer

# Edit profile
/profile edit
```

## 🚀 Advanced Usage

### Custom Workflows

```python
# Define custom workflow
from core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Custom research workflow
def research_workflow(topic):
    """Custom research workflow"""
    # Beta researches
    research = orchestrator.get_agent("beta").research(topic)
    
    # Gamma organizes
    knowledge = orchestrator.get_agent("gamma").organize(research)
    
    # Delta creates tasks
    tasks = orchestrator.get_agent("delta").create_tasks(knowledge)
    
    return {"research": research, "knowledge": knowledge, "tasks": tasks}
```

### API Integration

```python
# Use the system programmatically
from core.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Process request
response = orchestrator.process_request("Research quantum computing")
print(response)

# Get specific agent
beta = orchestrator.get_agent("beta")
research = beta.research("AI trends")
```

### Background Processing

```python
# Run agents in background
from scripts.start_production import start_background_agents

# Start background processing
start_background_agents()

# Agents will process tasks automatically
```

### Performance Monitoring

```python
# Check system health
from monitoring.health_check import HealthChecker

checker = HealthChecker()
status = checker.check_all()
print(status)

# Monitor specific metrics
cpu_usage = checker.get_cpu_usage()
memory_usage = checker.get_memory_usage()
agent_status = checker.get_agent_status()
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | `pip install -r requirements-minimal.txt` |
| **Ollama connection** | `ollama serve` and check `OLLAMA_BASE_URL` |
| **Video processing** | Install FFmpeg: `sudo apt install ffmpeg` |
| **Database errors** | Run `python scripts/init_database.py` |
| **High memory usage** | Use smaller model or enable throttling |
| **Slow responses** | Check system resources and model size |

### Debug Mode

```bash
# Enable debug mode
export DEBUG_MODE=true

# Run with verbose output
python run_assistant.py --verbose

# Check logs
tail -f logs/b3_assistant_*.log
```

### System Health

```bash
# Run health check
python scripts/start_production.py --health-check

# Check database status
python -c "from databases.manager import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"
```

### Performance Optimization

```python
# Monitor system resources
from monitoring.health_check import HealthChecker

checker = HealthChecker()

# Check current usage
print(f"CPU: {checker.get_cpu_usage()}%")
print(f"Memory: {checker.get_memory_usage()}%")
print(f"Disk: {checker.get_disk_usage()}%")

# Optimize settings
if checker.get_cpu_usage() > 80:
    print("Consider using a smaller AI model")
```

## 📞 Support

### Getting Help

- **Built-in Help**: Use `/help` commands
- **Documentation**: [API Documentation](API_DOCS.md)
- **Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING.md)
- **GitHub Issues**: [Report bugs](https://github.com/PROF-B3/b3personalassistant/issues)
- **Discussions**: [Ask questions](https://github.com/PROF-B3/b3personalassistant/discussions)

### Best Practices

1. **Start Simple**: Begin with basic commands and gradually explore advanced features
2. **Use Agent Strengths**: Let each agent handle their specialized tasks
3. **Organize Knowledge**: Use Gamma to maintain a well-organized knowledge base
4. **Plan Projects**: Use Delta for comprehensive project planning
5. **Monitor Performance**: Regularly check system health and optimize settings
6. **Backup Regularly**: Use the built-in backup system for your data

---

**Ready to explore the full potential of multi-agent AI collaboration? Start with the [Quick Start Guide](QUICK_START.md) or dive into [API Documentation](API_DOCS.md) for developers.** 