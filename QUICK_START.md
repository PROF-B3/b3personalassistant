# B3PersonalAssistant Quick Start Guide ⚡

> *"Welcome to the future of personal assistance. This guide will get you up and running in minutes."* — Prof. B3

## 🚀 Installation (5 minutes)

### Prerequisites
- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running

### Step 1: Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download

# Start Ollama
ollama serve
```

### Step 2: Install B3PersonalAssistant
```bash
# Clone the repository
git clone https://github.com/yourusername/B3PersonalAssistant.git
cd B3PersonalAssistant

# Install dependencies
pip install -r requirements.txt

# Download a model (optional, will download automatically)
ollama pull llama2
```

### Step 3: First Launch
```bash
python run_assistant.py
```

## 👋 Your First Experience

### 1. Prof. B3's Welcome Message
You'll see a message from 2073 introducing the system:
```
[Temporal Transfer Protocol Initiated]

Greetings, user. I am Prof. B3, transmitting this message from the year 2073...
```

### 2. Profile Setup
Answer a few questions to personalize your experience:
- Your name
- Work style (morning person, night owl, etc.)
- Areas of interest
- Preferred communication style
- Task management preferences

### 3. Choose Your Interface
- **GUI**: Retro terminal with three panels
- **CLI**: Command-line interface with rich formatting

## 🎯 Your First Tasks

### Basic Commands
```bash
# Get help
/help

# Check system status
/status

# See examples
/examples

# Clear chat
/clear
```

### Chat with Alpha (Chief Assistant)
```
You: Hello Alpha, I'm new here
Alpha: Welcome! I'm Alpha, your chief assistant. I coordinate with other 
      agents to help you with research, knowledge management, and task 
      planning. What would you like to work on today?
```

### Try a Research Task
```
You: Research quantum computing
Alpha: I'll coordinate Beta for research, Gamma for knowledge organization, 
      and Delta for task management. Let's create a comprehensive plan.

Beta: Based on my research, quantum computing uses quantum mechanical 
      phenomena to process information. Key concepts include qubits, 
      superposition, and entanglement...

Gamma: I've created Zettelkasten notes on quantum computing and linked 
       them to your existing knowledge base...

Delta: I've created follow-up tasks for deeper exploration...
```

## 📚 Knowledge Management

### Create Your First Note
```
You: Take notes on machine learning
Gamma: I've created a note on machine learning and linked it to related 
       concepts. I found connections to your existing knowledge about 
       programming and statistics.
```

### Search Your Knowledge
```bash
/search machine learning
/tags ai
/link neural networks
```

### View Connections
```
You: Show me connections to blockchain
Gamma: Blockchain connects to:
       - Cryptography (5 links)
       - Distributed Systems (3 links)
       - Digital Currency (2 links)
```

## ✅ Task Management

### Create Your First Task
```
You: I need to finish my project by Friday
Delta: I've created a task: 'Complete project'
       Due: Friday
       Priority: High
       Estimated time: 8 hours
       
       Would you like me to break this down into subtasks?
```

### Manage Tasks
```bash
/tasks list              # List all tasks
/tasks add "New task"    # Add task
/tasks complete 1        # Mark task complete
/tasks priority 1 high   # Set priority
```

### Project Organization
```bash
/project create "Website Redesign"
/task add "Design homepage" --project "Website Redesign"
/project tasks "Website Redesign"
```

## 🔧 Configuration

### Environment Variables
```bash
# Enable debug mode
export B3_DEBUG_MODE=true

# Set default model
export B3_DEFAULT_MODEL=llama2

# Choose interface
export B3_INTERFACE=cli  # or gui
```

### User Profiles
```bash
# Create different profiles
/profile create developer
/profile create researcher
/profile create student

# Switch profiles
/profile switch developer
```

## 🎮 Interface Tips

### GUI Interface
- **Left Panel**: Agent collaboration and communication
- **Center Panel**: Main user interaction
- **Right Panel**: System status and controls

**Keyboard Shortcuts:**
- **Tab**: Cycle between input boxes
- **Enter**: Send message
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text

**Commands:**
- `/export`: Export panel content
- `/clear`: Clear panel
- `/hint`: Show help

### CLI Interface
**Main Menu Options:**
1. Chat with Alpha
2. Research mode (Beta)
3. Knowledge management (Gamma)
4. Task management (Delta)
5. System status
6. Settings
7. Exit

**Commands:**
- `/help`: Show help
- `/status`: System status
- `/examples`: Example workflows
- `/backup`: Create backup
- `/restore`: Restore from backup

## 🔄 Example Workflows

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

## 🆘 Getting Help

### Built-in Help
```bash
/help              # General help
/help agents       # Agent-specific help
/help commands     # Command reference
/help examples     # Usage examples
```

### Common Issues

**Ollama Not Running:**
```bash
# Start Ollama
ollama serve

# Check status
ollama list
```

**High Resource Usage:**
```bash
# Check system status
/status

# Use smaller model
ollama pull llama2:7b
```

**Database Issues:**
```bash
# Create backup
/backup

# Restore from backup
/restore latest
```

## 📊 System Monitoring

### Check System Health
```bash
/status              # Current status
/status detailed     # Detailed information
/status history      # Historical data
```

### Monitor Resources
- **CPU Usage**: Current and historical CPU utilization
- **Memory Usage**: RAM usage and availability
- **Disk Usage**: Storage space monitoring
- **Ollama Status**: AI model availability
- **Agent Performance**: Response times and success rates

### Alerts and Throttling
The system automatically:
- Alerts when resources are high
- Throttles operations when needed
- Optimizes performance automatically

## 🔄 Backup and Restore

### Automatic Backups
- **Schedule**: Every 24 hours
- **Manual**: `/backup` command
- **Before Updates**: Automatic backup before system updates

### Manual Backup/Restore
```bash
/backup                    # Create backup now
/backup --name "project1"  # Named backup
/restore list              # List available backups
/restore "backup_20240115" # Restore specific backup
```

## 🎯 Next Steps

### 1. Explore Examples
```bash
/examples
```
Try the pre-built workflows to see what's possible.

### 2. Customize Your Profile
```bash
/profile edit
```
Adjust your preferences and work style.

### 3. Create Your First Project
```
You: Help me plan a project
Delta: I'll help you create a comprehensive project plan. 
      What type of project are you working on?
```

### 4. Build Your Knowledge Base
```
You: Take notes on [your topic of interest]
Gamma: I'll create notes and link them to your existing knowledge.
```

### 5. Set Up Regular Workflows
- Daily task planning with Delta
- Weekly knowledge review with Gamma
- Monthly project assessment with Alpha

## 🔮 Advanced Features

### Agent Communication
```
You: "Alpha, ask Beta to research AI trends"
Alpha: "Beta, research the latest AI developments"
Beta: "Research completed. Key findings:
       1. Multimodal AI breakthroughs
       2. Edge AI deployment
       3. AI ethics frameworks"
```

### Custom Workflows
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

### Performance Optimization
- Monitor system resources
- Adjust model settings
- Use appropriate model sizes
- Enable throttling when needed

## 📞 Support

### Resources
- **[User Guide](USER_GUIDE.md)**: Comprehensive documentation
- **[API Documentation](API_DOCS.md)**: Technical reference
- **[Troubleshooting](TROUBLESHOOTING.md)**: Common issues and solutions
- **[Zettelkasten Guide](ZETTELKASTEN.md)**: Knowledge management methodology

### Getting Help
- **Built-in Help**: Use `/help` commands
- **GitHub Issues**: Bug reports and feature requests
- **Community Forum**: User discussions and tips
- **Email Support**: Direct support for complex issues

---

**"You're now ready to experience the future of personal assistance. Every interaction, every note, every task completed brings us closer to the intelligent systems of tomorrow."**

— Prof. B3, Temporal Research Institute, 2073

*For detailed documentation, see [User Guide](USER_GUIDE.md). For troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).* 