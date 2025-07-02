# B3PersonalAssistant Troubleshooting Guide 🔧

> *"Even the most advanced systems encounter challenges. This guide will help you navigate through temporal anomalies and restore optimal functionality."* — Prof. B3

## 🚨 Quick Diagnosis

### System Status Check
```bash
# Check if system is running properly
python run_assistant.py --diagnostic

# Check Ollama status
ollama list

# Check system resources
python -c "from modules.resources import ResourceMonitor; print(ResourceMonitor(Path('databases')).get_cli_status())"
```

## 🔍 Common Issues and Solutions

### 1. Ollama Connection Issues

#### Problem: "Ollama is not running or unreachable"
**Symptoms:**
- Error: "Connection refused" or "Ollama not found"
- Agents fail to respond
- System shows "Ollama: offline" in status

**Solutions:**

**A. Start Ollama Service**
```bash
# Start Ollama
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

**B. Install Ollama Models**
```bash
# Install required models
ollama pull llama2
ollama pull mistral

# Verify installation
ollama list
```

**C. Check Ollama Configuration**
```python
# In your config.json or environment
{
  "ai_models": {
    "default": {
      "base_url": "http://localhost:11434",
      "timeout": 30
    }
  }
}
```

**D. Alternative Ollama URL**
```bash
# If using custom Ollama server
export OLLAMA_HOST=http://your-server:11434
```

#### Problem: "Model not found"
**Symptoms:**
- Error: "Model 'llama2' not found"
- Agents fail to initialize

**Solutions:**
```bash
# Pull the model
ollama pull llama2

# Or use a different model
# Update config.json
{
  "ai_models": {
    "default": {
      "model_name": "mistral"
    }
  }
}
```

### 2. Database Issues

#### Problem: "Database locked or corrupted"
**Symptoms:**
- Error: "database is locked"
- Data not saving
- System crashes on startup

**Solutions:**

**A. Check Database Permissions**
```bash
# Ensure write permissions
chmod 755 databases/
chmod 644 databases/*.db
```

**B. Backup and Recreate**
```bash
# Create backup
cp databases/conversations.db databases/conversations.db.backup

# Remove corrupted database
rm databases/conversations.db

# System will recreate on next run
```

**C. Database Recovery**
```python
import sqlite3

# Try to recover database
conn = sqlite3.connect('databases/conversations.db')
conn.execute("PRAGMA integrity_check")
conn.close()
```

#### Problem: "User profile not found"
**Symptoms:**
- System asks for profile setup repeatedly
- Profile settings not saved

**Solutions:**
```bash
# Check if profile exists
ls -la databases/user_profile.json

# Recreate profile
python setup_user_profile.py

# Or create manually
echo '{"name": "User", "work_style": "Flexible"}' > databases/user_profile.json
```

### 3. Resource and Performance Issues

#### Problem: "High CPU/Memory usage"
**Symptoms:**
- System becomes slow
- Agents take long to respond
- System shows resource alerts

**Solutions:**

**A. Check Resource Usage**
```bash
# Monitor system resources
python -c "
from modules.resources import ResourceMonitor
from pathlib import Path
rm = ResourceMonitor(Path('databases'))
print(rm.get_cli_status())
"
```

**B. Optimize Model Settings**
```python
# Reduce model complexity
{
  "ai_models": {
    "default": {
      "model_name": "llama2:7b",  # Use smaller model
      "max_tokens": 1024,         # Reduce token limit
      "temperature": 0.5          # Lower temperature
    }
  }
}
```

**C. Enable Throttling**
```python
# Adjust throttling thresholds
{
  "resources": {
    "max_memory_mb": 2048,
    "max_cpu_percent": 80,
    "throttle_thresholds": {
      "cpu": 85.0,
      "memory": 90.0
    }
  }
}
```

#### Problem: "Slow agent responses"
**Symptoms:**
- Agents take >5 seconds to respond
- System feels unresponsive

**Solutions:**

**A. Check Agent Performance**
```python
# View agent performance stats
from modules.resources import ResourceMonitor
rm = ResourceMonitor(Path('databases'))
stats = rm.get_agent_performance()
for agent, data in stats.items():
    print(f"{agent}: {data['avg_time']:.2f}s avg")
```

**B. Optimize Model Configuration**
```python
# Use faster model settings
{
  "ai_models": {
    "default": {
      "model_name": "llama2:7b",
      "temperature": 0.3,
      "max_tokens": 512
    }
  }
}
```

**C. Check System Resources**
```bash
# Monitor system during operation
top -p $(pgrep -f "python.*run_assistant")
```

### 4. Interface Issues

#### Problem: "GUI not starting"
**Symptoms:**
- GUI window doesn't appear
- Tkinter errors
- Interface crashes

**Solutions:**

**A. Check Tkinter Installation**
```python
# Test Tkinter
import tkinter as tk
root = tk.Tk()
root.destroy()
print("Tkinter works!")
```

**B. Install GUI Dependencies**
```bash
# Install required packages
pip install tkinter pillow

# On Ubuntu/Debian
sudo apt-get install python3-tk
```

**C. Use CLI Alternative**
```bash
# Switch to CLI interface
export B3_INTERFACE=cli
python run_assistant.py
```

#### Problem: "CLI colors not working"
**Symptoms:**
- No colored output
- Plain text interface
- Rich library errors

**Solutions:**

**A. Install Rich Library**
```bash
pip install rich

# Verify installation
python -c "from rich import print; print('[red]Test[/red]')"
```

**B. Check Terminal Support**
```bash
# Test color support
python -c "
from rich.console import Console
console = Console()
console.print('[red]Red text[/red]')
"
```

**C. Disable Colors**
```bash
# Force plain text
export FORCE_COLOR=0
python run_assistant.py
```

### 5. Configuration Issues

#### Problem: "Configuration not loading"
**Symptoms:**
- Default settings always used
- Changes not saved
- Config file errors

**Solutions:**

**A. Check Config File**
```bash
# Verify config file exists
ls -la config.json

# Check file permissions
chmod 644 config.json
```

**B. Reset Configuration**
```bash
# Backup current config
cp config.json config.json.backup

# Remove and recreate
rm config.json
python run_assistant.py  # Will create new config
```

**C. Environment Variables**
```bash
# Set configuration via environment
export B3_DEBUG_MODE=true
export B3_DEFAULT_MODEL=llama2
export B3_GUI_THEME=retro
```

### 6. Agent Communication Issues

#### Problem: "Agents not communicating"
**Symptoms:**
- Agents work individually but not together
- Orchestrator errors
- Multi-agent workflows fail

**Solutions:**

**A. Check Orchestrator**
```python
# Test orchestrator
from core.orchestrator import Orchestrator
from modules.knowledge import KnowledgeManager
from modules.tasks import TaskManager
from modules.conversation import ConversationManager

# Initialize components
knowledge = KnowledgeManager()
tasks = TaskManager()
conversation = ConversationManager()

# Test orchestrator
orchestrator = Orchestrator(knowledge, tasks, conversation)
result = orchestrator.route_request("Test communication")
print(f"Success: {result.success}")
```

**B. Check Agent Registration**
```python
# Verify agents are registered
from core.orchestrator import AgentRole
print("Registered agents:", [role.value for role in AgentRole])
```

**C. Test Agent Communication**
```python
# Test direct agent communication
from core.agents import AlphaAgent, BetaAgent

alpha = AlphaAgent()
beta = BetaAgent()

# Test communication
response = alpha.send_message("Beta", "Test message")
print(f"Beta response: {response}")
```

### 7. Knowledge Management Issues

#### Problem: "Zettelkasten not working"
**Symptoms:**
- Notes not created
- Links not working
- Search not finding notes

**Solutions:**

**A. Check Knowledge Directory**
```bash
# Verify X/ directory exists
ls -la X/

# Create if missing
mkdir -p X/_metadata
```

**B. Test Knowledge Manager**
```python
# Test knowledge manager
from modules.knowledge import KnowledgeManager

km = KnowledgeManager()

# Create test note
note_id = km.create_note("Test Note", "Test content", tags=["test"])
print(f"Created note: {note_id}")

# Search notes
results = km.search_notes("test")
print(f"Found {len(results)} notes")
```

**C. Check Database**
```bash
# Verify knowledge database
ls -la X/_metadata/zettelkasten.db

# Check database integrity
sqlite3 X/_metadata/zettelkasten.db "PRAGMA integrity_check;"
```

### 8. Task Management Issues

#### Problem: "Tasks not saving"
**Symptoms:**
- Tasks disappear after restart
- Task creation fails
- No task history

**Solutions:**

**A. Check Task Database**
```bash
# Verify task database
ls -la databases/tasks.db

# Check database integrity
sqlite3 databases/tasks.db "PRAGMA integrity_check;"
```

**B. Test Task Manager**
```python
# Test task manager
from modules.tasks import TaskManager, TaskPriority

tm = TaskManager()

# Create test task
task_id = tm.create_task("Test Task", priority=TaskPriority.HIGH)
print(f"Created task: {task_id}")

# List tasks
tasks = tm.list_tasks()
print(f"Found {len(tasks)} tasks")
```

**C. Check Permissions**
```bash
# Ensure write permissions
chmod 755 databases/
chmod 644 databases/tasks.db
```

## 🔧 Advanced Troubleshooting

### System Diagnostics

#### Complete System Check
```bash
#!/bin/bash
echo "=== B3PersonalAssistant System Diagnostics ==="

echo "1. Python Environment"
python --version
pip list | grep -E "(ollama|rich|tkinter)"

echo "2. Ollama Status"
ollama list 2>/dev/null || echo "Ollama not found"

echo "3. Database Status"
ls -la databases/ 2>/dev/null || echo "Databases directory not found"

echo "4. Configuration"
ls -la config.json 2>/dev/null || echo "Config file not found"

echo "5. Resource Usage"
python -c "
from modules.resources import ResourceMonitor
from pathlib import Path
try:
    rm = ResourceMonitor(Path('databases'))
    print(rm.get_cli_status())
except Exception as e:
    print(f'Resource monitor error: {e}')
"
```

#### Performance Profiling
```python
import time
import cProfile
import pstats

def profile_system():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run system operations
    from core.config import get_config
    config = get_config()
    
    from modules.knowledge import KnowledgeManager
    km = KnowledgeManager()
    
    from modules.tasks import TaskManager
    tm = TaskManager()
    
    profiler.disable()
    
    # Print results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

# Run profiling
profile_system()
```

### Log Analysis

#### Enable Debug Logging
```python
import logging

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('b3_debug.log'),
        logging.StreamHandler()
    ]
)

# Run system with debug logging
python run_assistant.py
```

#### Analyze Logs
```bash
# Check for errors
grep -i error b3_debug.log

# Check for warnings
grep -i warning b3_debug.log

# Check agent performance
grep "agent.*response" b3_debug.log
```

### Recovery Procedures

#### Complete System Reset
```bash
#!/bin/bash
echo "=== Complete System Reset ==="

# Backup current data
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp -r databases/ backups/$(date +%Y%m%d_%H%M%S)/
cp -r X/ backups/$(date +%Y%m%d_%H%M%S)/

# Remove all data
rm -rf databases/*
rm -rf X/*
rm -f config.json
rm -f *.log

# Reinitialize system
python run_assistant.py
```

#### Selective Recovery
```bash
# Recover specific components
cp backups/latest/conversations.db databases/
cp backups/latest/user_profile.json databases/
cp backups/latest/config.json ./
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Run diagnostics** to gather system information
3. **Check logs** for error messages
4. **Try basic solutions** first
5. **Document your steps** and results

### Information to Provide

When reporting issues, include:

```bash
# System information
python --version
pip list
ollama --version

# Error logs
tail -n 50 b3_debug.log

# System status
python -c "from modules.resources import ResourceMonitor; print(ResourceMonitor(Path('databases')).get_cli_status())"

# Configuration
cat config.json
```

### Support Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community help
- **Documentation**: Check [User Guide](USER_GUIDE.md) and [API Docs](API_DOCS.md)
- **Email Support**: For complex issues requiring direct assistance

## 🔮 Prevention Tips

### Regular Maintenance

```bash
# Weekly maintenance script
#!/bin/bash

echo "=== Weekly B3PersonalAssistant Maintenance ==="

# 1. Create backup
python -c "
from core.orchestrator import Orchestrator
orchestrator = Orchestrator(None, None, None)
orchestrator.backup_data('weekly_backups')
"

# 2. Check system health
python -c "
from modules.resources import ResourceMonitor
rm = ResourceMonitor(Path('databases'))
dashboard = rm.get_status_dashboard()
print('System Health:', dashboard)
"

# 3. Clean old logs
find . -name "*.log" -mtime +7 -delete

# 4. Update models (optional)
ollama pull llama2:latest
```

### Best Practices

1. **Regular Backups**: Set up automatic daily backups
2. **Monitor Resources**: Keep an eye on system performance
3. **Update Regularly**: Keep Ollama models and Python packages updated
4. **Test Changes**: Test configuration changes in a safe environment
5. **Document Issues**: Keep notes of problems and solutions

---

**"Remember, every challenge is an opportunity to improve the system. Your troubleshooting efforts contribute to the collective knowledge that shapes the future of AI assistance."**

— Prof. B3, Temporal Research Institute, 2073

*For user documentation, see [User Guide](USER_GUIDE.md). For API reference, see [API Documentation](API_DOCS.md).* 