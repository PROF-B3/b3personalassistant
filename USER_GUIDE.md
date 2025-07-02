# B3PersonalAssistant User Guide 📖

> *"Welcome to your temporal journey. This guide will help you master the future of personal assistance."* — Prof. B3

## 🌟 Introduction

B3PersonalAssistant is a revolutionary multi-agent AI system that adapts to your work style and helps you manage knowledge, tasks, and productivity. Built with local AI models for privacy and powered by four specialized agents, it represents the future of personal assistance.

### The Prof. B3 Story

*"In 2073, we discovered that true intelligence emerges from collaboration. This system embodies decades of research into multi-agent coordination, temporal knowledge management, and human-AI symbiosis. Your actions today ripple forward in time, contributing to the collective intelligence that shapes our future."*

## 🚀 Getting Started

### First Launch Experience

When you first run `python run_assistant.py`, you'll experience:

1. **Prof. B3's Temporal Message**: A welcome message from the future
2. **Profile Setup**: Configure your preferences and work style
3. **Interface Choice**: Select between GUI (retro terminal) or CLI
4. **First Interaction**: Begin your journey with AI assistance

### Quick Setup

```bash
# Install and run
pip install -r requirements.txt
python run_assistant.py

# Follow the onboarding flow
# Choose your preferences
# Start using the assistant
```

## 🤖 Understanding the Agents

### Alpha (Α) - Chief Assistant
**Role**: Strategic coordinator and main interface
**Personality**: Confident, diplomatic, big-picture thinker
**Specialties**: 
- Coordinating other agents
- Handling complex requests
- Strategic planning
- User interface management

**Example Interaction**:
```
You: "I need to research quantum computing for my project"
Alpha: "I'll coordinate Beta for research, Gamma for knowledge organization, 
       and Delta for task management. Let's create a comprehensive plan."
```

### Beta (Β) - Analyst
**Role**: Research and data analysis specialist
**Personality**: Curious, analytical, detail-oriented
**Specialties**:
- Information gathering
- Data analysis
- Research synthesis
- Insights generation

**Example Interaction**:
```
You: "What are the latest developments in AI?"
Beta: "Based on recent research, I've identified three key trends:
       1. Multimodal AI models
       2. Edge computing for AI
       3. AI ethics and governance
       Let me gather more specific details for you."
```

### Gamma (Γ) - Knowledge Manager
**Role**: Zettelkasten system and knowledge organization
**Personality**: Reflective, creative, connection-focused
**Specialties**:
- Note-taking and organization
- Knowledge linking
- Information synthesis
- Knowledge base management

**Example Interaction**:
```
You: "Take notes on machine learning concepts"
Gamma: "I've created Zettelkasten notes on ML concepts and linked them 
       to your existing knowledge base. I found connections to your 
       previous notes on statistics and programming."
```

### Delta (Δ) - Task Coordinator
**Role**: Task management and workflow optimization
**Personality**: Efficient, organized, action-oriented
**Specialties**:
- Task creation and management
- Workflow optimization
- Scheduling and deadlines
- Progress tracking

**Example Interaction**:
```
You: "I need to plan my week"
Delta: "I've analyzed your current tasks and created an optimized schedule:
       - Monday: Research phase (2 hours)
       - Tuesday: Development (4 hours)
       - Wednesday: Review and testing (3 hours)
       Would you like me to set up reminders?"
```

## 🎮 Using the Interfaces

### CLI Interface

The CLI provides a rich, interactive experience with color-coded agent responses.

#### Basic Commands
```bash
/help          # Show help menu
/status        # System status and health
/examples      # Example workflows
/backup        # Create data backup
/restore       # Restore from backup
/clear         # Clear chat history
/profile       # View/edit user profile
```

#### Agent Interaction
```bash
# Chat with specific agent
1. Select "Chat with Alpha" from main menu
2. Type your message
3. Receive agent response
4. Type 'exit' to return to menu

# Research mode with Beta
1. Select "Research mode (Beta)"
2. Enter research query
3. Get detailed analysis
4. Ask follow-up questions
```

#### Example CLI Session
```
B3PersonalAssistant - Multi-Agent AI CLI
========================================

Main Menu:
1. Chat with Alpha
2. Research mode (Beta)
3. Knowledge management (Gamma)
4. Task management (Delta)
5. System status
6. Settings
7. Exit

Select an option: 1

Chatting with Alpha. Type 'exit' to return to menu.
You: Hello Alpha, I need help with my project
Alpha: Greetings! I'm here to help coordinate your project. 
      What type of project are you working on? I can enlist 
      Beta for research, Gamma for knowledge management, 
      or Delta for task planning.
```

### GUI Interface

The retro terminal GUI provides a nostalgic 80s computer aesthetic with three panels.

#### Panel Layout
- **Left Panel**: Agent Collaboration Terminal
- **Center Panel**: Main User Terminal
- **Right Panel**: System Control/Status Terminal

#### GUI Commands
```
/export   # Export panel content to file
/clear    # Clear panel content
/hint     # Show help and hints
```

#### Keyboard Shortcuts
- **Tab**: Cycle between input boxes
- **Enter**: Send message
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text

#### Example GUI Session
```
[Agent Collaboration Terminal]
Alpha: Coordinating with Beta for research request
Beta: Research completed, sending to Gamma
Gamma: Knowledge organized and linked
Delta: Tasks created and scheduled

[Main User Terminal]
You: Research quantum computing
System: Processing with multi-agent collaboration...
Alpha: Here's your comprehensive quantum computing analysis

[System Control/Status Terminal]
Status: All agents online
CPU: 15% | Memory: 45% | Ollama: Online
Last backup: 2 hours ago
```

## 📚 Knowledge Management (Zettelkasten)

### Understanding Zettelkasten

*"The Zettelkasten method, perfected in 2073, creates a living knowledge base that grows more intelligent over time. Each note connects to others, forming a web of understanding that transcends linear thinking."*

### Creating Notes

#### Basic Note Creation
```bash
# Via CLI
Gamma: "Create a note about machine learning"
System: Note created: "Machine Learning Fundamentals"
        Linked to: "AI Basics", "Statistics", "Programming"

# Via GUI
Type in center panel: "Take notes on neural networks"
Gamma automatically creates and links notes
```

#### Note Format
```markdown
# Neural Networks Fundamentals

Neural networks are computational models inspired by biological neurons.

## Key Concepts
- Neurons and layers
- Activation functions
- Backpropagation
- Training algorithms

## Connections
- [[Machine Learning]]
- [[Deep Learning]]
- [[Backpropagation Algorithm]]

Tags: #neural-networks #machine-learning #ai
```

### Searching and Linking

#### Search Commands
```bash
/search neural networks    # Full-text search
/tags machine-learning     # Search by tags
/link neural networks      # Show connections
```

#### Automatic Linking
The system automatically:
- Links related concepts
- Suggests connections
- Creates knowledge graphs
- Identifies patterns

### Example Knowledge Session
```
You: "I'm learning about blockchain technology"
Gamma: "I've created a new note and linked it to your existing 
       knowledge about cryptography and distributed systems. 
       I found 3 related notes in your knowledge base."

You: "Show me connections to blockchain"
Gamma: "Blockchain connects to:
       - Cryptography (5 links)
       - Distributed Systems (3 links)
       - Digital Currency (2 links)
       - Smart Contracts (1 link)"
```

## ✅ Task Management

### Creating Tasks

#### Natural Language Task Creation
```bash
You: "I need to finish my project by Friday"
Delta: "I've created a task: 'Complete project'
       Due: Friday
       Priority: High
       Estimated time: 8 hours
       Would you like me to break this down into subtasks?"

You: "Break it down"
Delta: "Subtasks created:
       1. Research phase (2 hours)
       2. Development (4 hours)
       3. Testing (1 hour)
       4. Documentation (1 hour)"
```

#### Task Commands
```bash
/tasks list              # List all tasks
/tasks add "New task"    # Add task
/tasks complete 1        # Mark task complete
/tasks priority 1 high   # Set priority
/tasks due 1 2024-01-15  # Set due date
```

### Task Categories and Projects

#### Organizing Tasks
```bash
# Create project
/project create "Website Redesign"

# Add tasks to project
/task add "Design homepage" --project "Website Redesign"
/task add "Implement backend" --project "Website Redesign"

# View project tasks
/project tasks "Website Redesign"
```

#### Task Statistics
```bash
/stats tasks             # Task completion statistics
/stats productivity      # Productivity metrics
/stats time              # Time tracking data
```

### Example Task Session
```
You: "I have a lot of work this week"
Delta: "Let me analyze your current workload:
       - 5 active tasks
       - 3 due this week
       - Estimated 15 hours remaining
       
       I recommend prioritizing:
       1. Project presentation (due Wednesday)
       2. Code review (due Thursday)
       3. Documentation (due Friday)
       
       Would you like me to reschedule anything?"
```

## 🔧 Configuration and Customization

### User Profiles

#### Creating Profiles
```bash
# During setup or via command
/profile create developer
/profile create researcher
/profile create student
```

#### Profile Settings
```json
{
  "name": "Developer",
  "work_style": "Flexible",
  "interests": ["programming", "AI", "productivity"],
  "communication_style": "Concise",
  "task_management": "GTD",
  "knowledge_organization": "Zettelkasten"
}
```

#### Switching Profiles
```bash
/profile switch developer
/profile switch researcher
```

### System Configuration

#### Environment Variables
```bash
export B3_DEBUG_MODE=true
export B3_DEFAULT_MODEL=llama2
export B3_GUI_THEME=retro
export B3_MAX_MEMORY_MB=4096
```

#### Configuration File
```json
{
  "ai_models": {
    "default": {
      "model_name": "llama2",
      "temperature": 0.7
    }
  },
  "gui": {
    "theme": "retro",
    "font_size": 12
  },
  "resources": {
    "max_memory_mb": 2048
  }
}
```

## 📊 System Monitoring

### Resource Monitoring

#### Real-time Status
```bash
/status              # Current system status
/status detailed     # Detailed resource information
/status history      # Historical data
```

#### Monitoring Data
- **CPU Usage**: Current and historical CPU utilization
- **Memory Usage**: RAM usage and availability
- **Disk Usage**: Storage space monitoring
- **Ollama Status**: AI model availability
- **Database Sizes**: Storage usage
- **Agent Performance**: Response times and success rates

#### Example Status Output
```
System Status:
Time: 2024-01-15T14:30:00
CPU: 25.3%
Memory: 67.8%
Disk: 45.2%
Ollama: Online (llama2, mistral)
DB Sizes: conversations.db (2.1MB), tasks.db (0.8MB)
Agent Performance:
  Alpha: 1.2s avg, 98% success
  Beta: 2.1s avg, 95% success
  Gamma: 0.8s avg, 99% success
  Delta: 0.9s avg, 97% success
```

### Alerts and Throttling

#### Resource Alerts
The system automatically alerts when:
- CPU usage > 90%
- Memory usage > 95%
- Disk usage > 95%
- Agent response time > 5 seconds

#### Throttling
When resources are high:
- Agent requests are queued
- Response times may increase
- Non-critical operations are delayed
- Automatic resource optimization

## 🔄 Backup and Restore

### Automatic Backups

#### Backup Schedule
- **Automatic**: Every 24 hours
- **Manual**: `/backup` command
- **Before Updates**: Automatic backup before system updates

#### Backup Contents
- Conversation history
- Task data
- Zettelkasten notes
- User profiles
- Configuration settings

### Manual Backup/Restore

#### Creating Backup
```bash
/backup                    # Create backup now
/backup --name "project1"  # Named backup
/backup --compress         # Compressed backup
```

#### Restoring Data
```bash
/restore list              # List available backups
/restore "backup_20240115" # Restore specific backup
/restore --preview         # Preview backup contents
```

## 🎯 Example Workflows

### Research Workflow
```
1. User: "Research quantum computing applications"
2. Alpha: Coordinates the research process
3. Beta: Gathers and analyzes information
4. Gamma: Organizes findings in Zettelkasten
5. Delta: Creates follow-up tasks
6. Alpha: Presents comprehensive summary
```

### Project Planning Workflow
```
1. User: "Plan my website redesign project"
2. Delta: Creates project structure and tasks
3. Beta: Researches best practices and tools
4. Gamma: Documents requirements and specifications
5. Alpha: Coordinates timeline and resources
6. Delta: Sets up milestones and deadlines
```

### Learning Workflow
```
1. User: "I want to learn machine learning"
2. Gamma: Creates learning path in Zettelkasten
3. Beta: Researches resources and courses
4. Delta: Creates study schedule and tasks
5. Alpha: Monitors progress and adjusts plan
6. Gamma: Links new knowledge to existing concepts
```

## 🆘 Help and Support

### Built-in Help

#### Help Commands
```bash
/help              # General help
/help agents       # Agent-specific help
/help commands     # Command reference
/help examples     # Usage examples
/help troubleshooting # Common issues
```

#### Contextual Help
- Agents provide help based on context
- GUI shows hints and tips
- Error messages include suggestions
- Tutorial mode for new users

### Troubleshooting

#### Common Issues
1. **Ollama Not Running**
   ```bash
   # Start Ollama
   ollama serve
   
   # Check status
   ollama list
   ```

2. **High Resource Usage**
   ```bash
   # Check system status
   /status
   
   # Reduce model size
   ollama pull llama2:7b
   ```

3. **Database Errors**
   ```bash
   # Backup and restore
   /backup
   /restore latest
   ```

## 🌟 Advanced Features

### Agent Communication

#### Direct Agent Messaging
```bash
# Send message to specific agent
Alpha: "Beta, research the latest AI developments"
Beta: "Research completed. Key findings:
      1. Multimodal AI breakthroughs
      2. Edge AI deployment
      3. AI ethics frameworks"
```

#### Multi-Agent Collaboration
```bash
# Complex request
You: "Create a comprehensive project plan for my startup"
Alpha: "Coordinating multi-agent analysis..."
Beta: "Market research and competitive analysis complete"
Gamma: "Knowledge base updated with industry insights"
Delta: "Project timeline and milestones created"
Alpha: "Here's your comprehensive startup plan..."
```

### Custom Workflows

#### Creating Custom Workflows
```python
# Define custom workflow
workflow = {
    "name": "Content Creation",
    "steps": [
        "Beta researches topic",
        "Gamma organizes information",
        "Alpha creates outline",
        "Delta schedules writing tasks"
    ]
}
```

#### Workflow Templates
- Research and Analysis
- Project Planning
- Content Creation
- Learning and Study
- Problem Solving

## 🔮 Future Features

### Planned Enhancements
- **Voice Interface**: Speech-to-text and text-to-speech
- **Mobile App**: iOS and Android applications
- **Cloud Sync**: Optional cloud synchronization
- **Plugin System**: Extensible functionality
- **Advanced Analytics**: Detailed productivity insights

### Community Features
- **Workflow Sharing**: Share custom workflows
- **Knowledge Exchange**: Collaborative knowledge bases
- **Agent Training**: Custom agent personalities
- **Integration APIs**: Connect with external tools

## 📞 Getting Help

### Support Resources
- **Documentation**: This user guide and API docs
- **GitHub Issues**: Bug reports and feature requests
- **Community Forum**: User discussions and tips
- **Email Support**: Direct support for complex issues

### Contributing
- **Bug Reports**: Help improve the system
- **Feature Requests**: Suggest new capabilities
- **Documentation**: Help improve guides
- **Code Contributions**: Join the development team

---

**"Your journey with B3PersonalAssistant is just beginning. Every interaction, every note, every task completed brings us closer to the future of AI assistance."**

— Prof. B3, Temporal Research Institute, 2073

*For technical details, see [API Documentation](API_DOCS.md). For troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).* 