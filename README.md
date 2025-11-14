# 🤖 B3PersonalAssistant

> **A Next-Generation Multi-Agent AI System for Personal Productivity & Creative Workflows**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-22%20passed-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange.svg)](.github/workflows/ci.yml)

## 🚀 Overview

B3PersonalAssistant is a sophisticated multi-agent AI system featuring **7 specialized agents** that collaborate to handle complex tasks, from research and task management to video processing and knowledge organization. Built with modern Python, comprehensive testing, and production-ready infrastructure.

### ✨ Key Features

- **🤖 7 Specialized AI Agents**: Alpha (Chief), Beta (Research), Gamma (Knowledge), Delta (Tasks), Epsilon (Creative), Zeta (Code), Eta (Evolution)
- **🖥️ Desktop Application**: PyQt6-based app with Research, Video, and Writing modes
- **📚 Interactive Onboarding**: First-run wizard and 7 step-by-step tutorials
- **🎬 Advanced Video Processing**: AI-powered video editing with themes, effects, and prompt-to-video creation
- **📚 Zettelkasten Integration**: Sophisticated knowledge management system
- **🗄️ Production Database**: SQLAlchemy-based persistence with conversation history
- **🔧 Modern DevOps**: Docker, CI/CD, health monitoring, comprehensive testing
- **🎨 Multiple Interfaces**: Desktop app, CLI, and GUI launchers

## 🏗️ Architecture

```
B3PersonalAssistant/
├── 🤖 Core Agents (7 specialized AI agents)
├── 🎬 Video Processing (AI-enhanced editing)
├── 📚 Knowledge Management (Zettelkasten)
├── 🗄️ Database Layer (SQLAlchemy + SQLite)
├── 🔧 Configuration (Environment-based)
├── 🧪 Testing (Pytest + 100% coverage)
├── 🐳 Deployment (Docker + Compose)
└── 📊 Monitoring (Health checks + metrics)
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Ollama** (for local AI models)
- **FFmpeg** (for video processing)

### Installation

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

### Docker (Recommended)

```bash
# Start with Docker Compose
docker-compose up -d

# Or build manually
docker build -t b3personalassistant .
docker run -p 8000:8000 b3personalassistant
```

## 🖥️ Desktop Application

B3PersonalAssistant includes a powerful **PyQt6 desktop application** designed for academic work, video editing, and writing.

### Features

- **🔬 Research Mode**: PDF viewing, annotation, note-taking
- **🎬 Video Mode**: Professional video editing with themes and AI-powered effects
- **✍️ Writing Mode**: Markdown editor with live preview and export
- **🤖 AI Integration**: Inline AI assistance in all modes
- **📚 First-Run Onboarding**: Interactive wizard for setup
- **🎓 Interactive Tutorials**: 7 step-by-step guides covering all features

### Running the Desktop App

```bash
# Install desktop dependencies
pip install -r requirements-desktop.txt

# Launch desktop app
python run_desktop.py
```

On first run, you'll be greeted with an onboarding wizard that will:
1. Collect your preferences (name, citation style, theme)
2. Create your workspace structure
3. Generate sample files for learning
4. Provide access to interactive tutorials

### Desktop App Modes

**Research Mode**
- Open and view PDFs side-by-side
- Take notes while reading
- Organize research papers
- AI-powered research assistance

**Video Mode**
- Load and preview videos
- Apply futuristic themes (Neon Cyberpunk, Matrix, Tron, Blade Runner, Synthwave)
- Export segments with effects
- Create AI-powered video remixes
- Generate videos from prompts using assets

**Writing Mode**
- Full-featured Markdown editor
- Live preview with syntax highlighting
- Export to PDF, Word, HTML
- AI writing assistance
- Citation management

### Onboarding & Tutorials

The desktop app includes a comprehensive onboarding system:

- **First-Run Wizard**: Set up preferences and workspace
- **7 Interactive Tutorials**: Learn all features step-by-step
  - Getting Started (5 min)
  - Research Mode (7 min)
  - Writing Mode (8 min)
  - Video Editing (10 min)
  - AI Agents (6 min)
  - Video Creation (10 min)
  - Organization & Workflow (8 min)
- **Progress Tracking**: Monitor tutorial completion
- **Quick Start Guide**: Always accessible from Help menu

Access tutorials anytime from **Help → Interactive Tutorials**

For detailed desktop app documentation, see [ONBOARDING_GUIDE.md](ONBOARDING_GUIDE.md) and [VIDEO_EDITING_GUIDE.md](VIDEO_EDITING_GUIDE.md)

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [🚀 Quick Start](QUICK_START.md) | Get up and running in minutes |
| [👤 User Guide](USER_GUIDE.md) | Complete user manual |
| [🖥️ Onboarding Guide](ONBOARDING_GUIDE.md) | Desktop app setup and tutorials |
| [🎬 Video Editing Guide](VIDEO_EDITING_GUIDE.md) | Complete video editing reference |
| [🎬 Video Workflow](VIDEO_WORKFLOW_GUIDE.md) | AI video processing guide |
| [📚 Zettelkasten](ZETTELKASTEN.md) | Knowledge management system |
| [🔌 API Documentation](API_DOCS.md) | Developer API reference |
| [🔧 Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| [🤝 Contributing](CONTRIBUTING.md) | How to contribute |

## 🤖 Agent System

### The 7 Agents

| Agent | Role | Specialization |
|-------|------|----------------|
| **Alpha (Α)** | Chief Assistant | Coordination, general assistance |
| **Beta (Β)** | Research Analyst | Research, data analysis, investigations |
| **Gamma (Γ)** | Knowledge Manager | Information organization, Zettelkasten |
| **Delta (Δ)** | Task Coordinator | Task management, scheduling, optimization |
| **Epsilon (Ε)** | Creative Assistant | Creative tasks, brainstorming, ideation |
| **Zeta (Ζ)** | Code Architect | Code review, optimization, architecture |
| **Eta (Η)** | Evolution Engineer | System improvement, capability enhancement |

### Agent Collaboration

Agents communicate and collaborate automatically:
- **Intelligent Routing**: Requests are routed to the most appropriate agent
- **Cross-Agent Communication**: Agents share information and coordinate tasks
- **Learning & Adaptation**: System improves based on user interactions

## 🎬 Video Processing Workflow

B3PersonalAssistant features an advanced AI-powered video processing system:

1. **Scene Detection**: Automatically identifies video segments
2. **AI Image Generation**: Creates custom visuals for each scene
3. **Text Overlay**: Adds dynamic text and graphics
4. **Multi-Agent Collaboration**: Different agents handle different aspects
5. **Export & Delivery**: Final video compilation and delivery

See [Video Workflow Guide](VIDEO_WORKFLOW_GUIDE.md) for detailed instructions.

## 🗄️ Database & Persistence

- **SQLAlchemy ORM**: Type-safe database operations
- **SQLite Storage**: Lightweight, file-based database
- **Conversation History**: Complete chat history with agents
- **Task Management**: Persistent task tracking
- **Knowledge Base**: Zettelkasten note system
- **System Metrics**: Performance monitoring data

## 🔧 Configuration

Environment-based configuration with `.env` file support:

```bash
# Copy example config
cp config.env.example .env

# Edit configuration
nano .env
```

Key configuration areas:
- **AI Models**: Ollama, OpenAI, Anthropic integration
- **System Resources**: Memory, CPU limits, concurrent tasks
- **Video Processing**: Quality, format, resolution settings
- **Security**: API keys, encryption settings
- **Monitoring**: Health checks, metrics collection

## 🧪 Testing

Comprehensive test suite with 100% coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=modules

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
isort --check-only .

# Run type checking
mypy core/ modules/ interfaces/
```

## 🐳 Deployment

### Production Deployment

```bash
# Start production system
python scripts/start_production.py

# Or use Docker
docker-compose -f docker-compose.yml up -d
```

### Health Monitoring

The system includes comprehensive health monitoring:
- **System Resources**: CPU, memory, disk usage
- **Agent Status**: Individual agent health and performance
- **Database Health**: Connection and performance metrics
- **Dependencies**: External service availability

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- **Code Style**: Black, isort, flake8 standards
- **Testing**: Pytest with comprehensive coverage
- **Documentation**: Clear, up-to-date docs
- **Pull Requests**: Review process and guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local AI model hosting
- **SQLAlchemy** for database management
- **MoviePy** for video processing
- **Rich** for beautiful terminal interfaces
- **Pytest** for comprehensive testing

## 📞 Support

- **📖 Documentation**: [User Guide](USER_GUIDE.md)
- **🔧 Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING.md)
- **🐛 Issues**: [GitHub Issues](https://github.com/PROF-B3/b3personalassistant/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/PROF-B3/b3personalassistant/discussions)

---

**Made with ❤️ by Prof. B3 and the B3PersonalAssistant Team** 