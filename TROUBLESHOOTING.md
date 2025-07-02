# 🔧 Troubleshooting Guide

> **Solutions to common issues with B3PersonalAssistant**

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Problems](#performance-problems)
4. [Configuration Issues](#configuration-issues)
5. [Database Problems](#database-problems)
6. [Video Processing Issues](#video-processing-issues)
7. [Agent System Issues](#agent-system-issues)
8. [Getting Help](#getting-help)

## 🚀 Installation Issues

### Import Errors

**Problem:** `ModuleNotFoundError` or import failures

**Solutions:**
```bash
# Install dependencies
pip install -r requirements-minimal.txt

# For development
pip install -r requirements-dev.txt

# Check Python version (requires 3.9+)
python --version

# Verify installation
python test_imports.py
```

### Ollama Connection Issues

**Problem:** Cannot connect to Ollama or models not found

**Solutions:**
```bash
# Start Ollama service
ollama serve

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull a model
ollama pull llama2

# Check available models
ollama list

# Verify connection
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

### Permission Errors

**Problem:** File permission or access denied errors

**Solutions:**
```bash
# Check file permissions
ls -la

# Fix permissions
chmod +x run_assistant.py
chmod -R 755 .

# Run as administrator (Windows)
# Right-click PowerShell and "Run as Administrator"

# Check disk space
df -h
```

## ⚡ Runtime Errors

### Configuration Errors

**Problem:** Missing environment variables or config files

**Solutions:**
```bash
# Copy example configuration
cp config.env.example .env

# Edit configuration
nano .env

# Set required variables
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
export DEBUG_MODE=false
```

### Database Errors

**Problem:** Database connection or initialization failures

**Solutions:**
```bash
# Initialize database
python scripts/init_database.py

# Check database status
python -c "from databases.manager import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"

# Reset database (WARNING: loses data)
rm databases/b3_assistant.db
python scripts/init_database.py
```

### Agent Initialization Errors

**Problem:** Agents fail to start or initialize

**Solutions:**
```bash
# Check agent configuration
cat config/agents.json

# Test individual agents
python -c "from core.agents import AlphaAgent; agent = AlphaAgent(); print(agent.get_status())"

# Reset agent state
rm -rf logs/
python run_assistant.py
```

## 🐌 Performance Problems

### High Memory Usage

**Problem:** System runs out of memory or becomes slow

**Solutions:**
```bash
# Check memory usage
free -h
top

# Use smaller model
ollama pull llama2:7b

# Reduce concurrent tasks
export MAX_CONCURRENT_TASKS=2

# Enable memory optimization
export OPTIMIZE_MEMORY=true
```

### Slow Response Times

**Problem:** Agents take too long to respond

**Solutions:**
```bash
# Check system resources
python scripts/start_production.py --health-check

# Use faster model
ollama pull llama2:7b

# Reduce model complexity
export MODEL_COMPLEXITY=low

# Enable caching
export ENABLE_CACHE=true
```

### CPU Overload

**Problem:** High CPU usage affecting system performance

**Solutions:**
```bash
# Check CPU usage
htop

# Limit CPU cores
export MAX_CPU_CORES=4

# Enable throttling
export ENABLE_THROTTLING=true

# Use background processing
python scripts/start_production.py --background
```

## ⚙️ Configuration Issues

### Environment Variables Not Loading

**Problem:** Configuration changes not taking effect

**Solutions:**
```bash
# Reload environment
source .env

# Restart the application
pkill -f run_assistant.py
python run_assistant.py

# Check loaded variables
python -c "from core.config import ConfigManager; config = ConfigManager(); print(config.get('OLLAMA_BASE_URL'))"
```

### Agent Configuration Errors

**Problem:** Agents not behaving as expected

**Solutions:**
```bash
# Validate agent config
python -c "import json; config = json.load(open('config/agents.json')); print('Valid config')"

# Reset agent config
cp config/agents.json config/agents.json.backup
# Edit config/agents.json manually

# Test agent capabilities
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); print(o.get_agent('alpha').get_capabilities())"
```

## 🗄️ Database Problems

### Database Corruption

**Problem:** Database errors or corrupted data

**Solutions:**
```bash
# Create backup
cp databases/b3_assistant.db databases/backup_$(date +%Y%m%d).db

# Check database integrity
python -c "from databases.manager import DatabaseManager; db = DatabaseManager(); print(db.check_integrity())"

# Restore from backup
cp databases/backup_20240101.db databases/b3_assistant.db

# Reinitialize if needed
python scripts/init_database.py
```

### Database Lock Issues

**Problem:** Database locked or busy errors

**Solutions:**
```bash
# Check for running processes
ps aux | grep python

# Kill hanging processes
pkill -f b3_assistant

# Wait and retry
sleep 5
python run_assistant.py

# Use different database path
export DATABASE_PATH=databases/b3_assistant_new.db
```

## 🎬 Video Processing Issues

### FFmpeg Not Found

**Problem:** Video processing fails due to missing FFmpeg

**Solutions:**
```bash
# Install FFmpeg (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Windows)
# Download from https://ffmpeg.org/download.html

# Verify installation
ffmpeg -version
```

### Video Processing Errors

**Problem:** Video processing fails or produces errors

**Solutions:**
```bash
# Check video file
ffprobe input.mp4

# Use smaller video for testing
ffmpeg -i input.mp4 -t 30 -c copy test_30s.mp4

# Check available formats
python -c "from modules.video_processing import VideoProcessor; p = VideoProcessor(); print(p.get_supported_formats())"

# Enable debug mode
export DEBUG_MODE=true
python demo_video_workflow.py
```

### Memory Issues During Video Processing

**Problem:** Out of memory during video processing

**Solutions:**
```python
# Use lower quality settings
processor.process_video(
    input_path="video.mp4",
    output_dir="output/",
    theme="neon_cyberpunk",
    quality="medium",
    resolution="1280x720",
    segment_duration=30
)

# Process in smaller chunks
processor.process_video(
    input_path="video.mp4",
    output_dir="output/",
    theme="neon_cyberpunk",
    max_segments=5
)
```

## 🤖 Agent System Issues

### Agent Communication Failures

**Problem:** Agents not communicating or coordinating properly

**Solutions:**
```bash
# Check agent status
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); print(o.get_system_status())"

# Restart orchestrator
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); o.restart()"

# Test agent communication
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); print(o.process_request('test communication'))"
```

### Agent Model Issues

**Problem:** Agents using wrong or unavailable models

**Solutions:**
```bash
# Check available models
ollama list

# Pull required model
ollama pull llama2

# Update agent configuration
# Edit config/agents.json to use available models

# Test model availability
python -c "from core.agents import BaseAgent; agent = BaseAgent('test', 'test', 'llama2'); print(agent.test_model())"
```

### Agent Performance Issues

**Problem:** Specific agents performing poorly

**Solutions:**
```bash
# Check agent performance
python -c "from monitoring.health_check import HealthChecker; h = HealthChecker(); print(h.get_agent_status())"

# Restart specific agent
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); o.restart_agent('alpha')"

# Update agent model
python -c "from core.orchestrator import Orchestrator; o = Orchestrator(); o.get_agent('alpha').update_model('llama2:7b')"
```

## 🔍 Debugging Techniques

### Enable Debug Mode

```bash
# Enable debug logging
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Run with debug output
python run_assistant.py --verbose

# Check logs
tail -f logs/b3_assistant_*.log
```

### System Health Check

```bash
# Run comprehensive health check
python scripts/start_production.py --health-check

# Check specific components
python -c "from monitoring.health_check import HealthChecker; h = HealthChecker(); print(h.check_all())"
```

### Performance Monitoring

```bash
# Monitor system resources
htop

# Check disk usage
df -h

# Monitor network
netstat -tuln

# Check processes
ps aux | grep python
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Enable debug mode** and check logs
3. **Try the solutions** listed above
4. **Gather information** about your system

### Information to Include

When reporting issues, include:

```bash
# System information
python --version
pip list
uname -a

# Configuration
cat .env
cat config/agents.json

# Error logs
tail -n 50 logs/b3_assistant_*.log

# Health check
python scripts/start_production.py --health-check
```

### Support Channels

- **📖 Documentation**: [User Guide](USER_GUIDE.md)
- **🔌 API Reference**: [API Documentation](API_DOCS.md)
- **🐛 GitHub Issues**: [Report bugs](https://github.com/PROF-B3/b3personalassistant/issues)
- **💬 Discussions**: [Ask questions](https://github.com/PROF-B3/b3personalassistant/discussions)

### Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| **Import errors** | `pip install -r requirements-minimal.txt` |
| **Ollama connection** | `ollama serve` |
| **Database errors** | `python scripts/init_database.py` |
| **Video processing** | Install FFmpeg |
| **High memory usage** | Use smaller model (`llama2:7b`) |
| **Slow performance** | Reduce concurrent tasks |
| **Configuration issues** | Copy and edit `.env` file |

---

**Still having issues? Check the [User Guide](USER_GUIDE.md) for detailed instructions or ask in [GitHub Discussions](https://github.com/PROF-B3/b3personalassistant/discussions).** 