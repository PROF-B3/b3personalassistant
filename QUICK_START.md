# 🚀 Quick Start Guide

> **Get B3PersonalAssistant up and running in under 5 minutes**

## 📋 Prerequisites

- **Python 3.9+**
- **Git**
- **Ollama** (for local AI models)
- **FFmpeg** (for video processing)

## ⚡ Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/PROF-B3/b3personalassistant.git
cd b3personalassistant

# Install dependencies
pip install -r requirements-minimal.txt

# Initialize database
python scripts/init_database.py

# Run the assistant
python run_assistant.py
```

### Option 2: Docker (Recommended)

```bash
# Clone and start with Docker Compose
git clone https://github.com/PROF-B3/b3personalassistant.git
cd b3personalassistant
docker-compose up -d
```

### Option 3: Development Setup

```bash
# Clone and install dev dependencies
git clone https://github.com/PROF-B3/b3personalassistant.git
cd b3personalassistant
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Start development mode
python run_assistant.py
```

## 🎯 First Steps

### 1. Basic Interaction

```python
# Start the assistant
python run_assistant.py

# Or use the CLI
python -m interfaces.cli_launcher
```

### 2. Try These Commands

```
Hello, I'm new to B3PersonalAssistant
→ Alpha will welcome you and explain the system

Research the latest AI trends
→ Beta will gather and analyze information

Create a task to learn Python
→ Delta will set up a structured learning plan

Save this information about machine learning
→ Gamma will organize it in your knowledge base
```

### 3. Video Processing (Optional)

```python
# Process a video with AI enhancements
python demo_video_workflow.py

# Or use the video workflow directly
from modules.video_processing import process_video
process_video("your_video.mp4", theme="neon_cyberpunk")
```

## 🔧 Configuration

### Environment Setup

```bash
# Copy the example configuration
cp config.env.example .env

# Edit key settings
nano .env
```

**Essential Settings:**
```bash
# AI Model Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# System Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO

# Video Processing
VIDEO_SEGMENT_DURATION=60
VIDEO_FPS=30
```

### Ollama Setup

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama service
ollama serve
```

## 🧪 Testing Your Installation

### Run the Test Suite

```bash
# All tests
pytest tests/ -v

# Specific test categories
pytest tests/test_core.py -v
pytest tests/ -k "agent" -v
```

### Health Check

```bash
# Check system health
python -c "from monitoring.health_check import HealthChecker; print('System healthy!')"

# Or run the health check script
python scripts/start_production.py --health-check
```

## 🎬 Quick Video Workflow

### Basic Video Processing

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

### Advanced Workflow

```python
# Use the full collaborative workflow
from demo_video_workflow import create_futuristic_remix

# Create AI-enhanced video segments
result = create_futuristic_remix("your_video.mp4")
print(f"Created {len(result)} segments")
```

## 🗄️ Database Management

### Initialize Database

```bash
# Create database with sample data
python scripts/init_database.py

# Check database status
python -c "from databases.manager import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"
```

### Backup and Restore

```bash
# Backup database
cp databases/b3_assistant.db databases/backup_$(date +%Y%m%d).db

# Restore from backup
cp databases/backup_20240101.db databases/b3_assistant.db
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | `pip install -r requirements-minimal.txt` |
| **Ollama connection** | `ollama serve` and check `OLLAMA_BASE_URL` |
| **Video processing** | Install FFmpeg: `sudo apt install ffmpeg` |
| **Database errors** | Run `python scripts/init_database.py` |
| **Permission errors** | Check file permissions and ownership |

### Logs and Debugging

```bash
# Enable debug mode
export DEBUG_MODE=true

# Check logs
tail -f logs/b3_assistant_*.log

# Run with verbose output
python run_assistant.py --verbose
```

## 📚 Next Steps

### Learn More

- **[User Guide](USER_GUIDE.md)** - Complete system manual
- **[API Documentation](API_DOCS.md)** - Developer reference
- **[Video Workflow](VIDEO_WORKFLOW_GUIDE.md)** - Advanced video processing
- **[Zettelkasten](ZETTELKASTEN.md)** - Knowledge management

### Advanced Features

- **Multi-Agent Collaboration**: Agents work together automatically
- **Custom Themes**: Create your own video processing themes
- **API Integration**: Connect with external services
- **Production Deployment**: Scale for production use

### Community

- **[GitHub Issues](https://github.com/PROF-B3/b3personalassistant/issues)** - Report bugs
- **[Discussions](https://github.com/PROF-B3/b3personalassistant/discussions)** - Ask questions
- **[Contributing](CONTRIBUTING.md)** - Help improve the project

---

**🎉 Congratulations! You're ready to explore the power of multi-agent AI collaboration!**

Need help? Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or ask in [GitHub Discussions](https://github.com/PROF-B3/b3personalassistant/discussions). 