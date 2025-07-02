# B3 Personal Assistant 🤖

> **A Multi-Agent AI System for Intelligent Personal Assistance**

B3 Personal Assistant is an advanced AI system featuring 7 specialized agents that work together to provide comprehensive personal assistance, from creative projects to technical tasks and knowledge management.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🌟 Key Features

### 🤖 **7 Specialized AI Agents**
- **Alpha (Α)**: Chief Coordinator & Project Manager
- **Beta (Β)**: Research Analyst & Data Specialist  
- **Gamma (Γ)**: Knowledge Manager & Zettelkasten
- **Delta (Δ)**: Task Coordinator & Workflow Optimizer
- **Epsilon (Ε)**: Creative Director & Media Specialist
- **Zeta (Ζ)**: Code Architect & Technical Specialist
- **Eta (Η)**: Evolution Engineer & System Improver

### 🎯 **Core Capabilities**
- **Multi-Agent Collaboration**: Agents communicate and coordinate seamlessly
- **Creative Projects**: Video editing, image manipulation, creative writing
- **Technical Solutions**: Code generation, debugging, automation
- **Knowledge Management**: Zettelkasten system with intelligent connections
- **Task Management**: Project planning, workflow optimization
- **Research & Analysis**: Data-driven insights and trend analysis
- **System Evolution**: Continuous learning and improvement

### 🎬 **Advanced Video Processing**
- Scene detection and automatic segmentation
- AI image generation and integration
- Futuristic text overlays and effects
- Multi-platform export optimization
- Collaborative workflow orchestration

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/b3personalassistant.git
cd b3personalassistant

# Install dependencies
pip install -r requirements-minimal.txt

# For development
pip install -r requirements-dev.txt
```

### 2. Setup

```bash
# Initialize the system
python setup_user_profile.py

# Or run directly
python -m B3PersonalAssistant
```

### 3. Basic Usage

```python
from core.orchestrator import Orchestrator

# Initialize the system
orchestrator = Orchestrator()

# Ask for help with a complex project
response = orchestrator.process_request(
    "I need to create a video montage with AI-generated effects"
)
print(response)
```

## 📖 Documentation

### 📚 **Core Guides**
- **[User Guide](USER_GUIDE.md)** - Complete user manual
- **[Quick Start](QUICK_START.md)** - Get up and running fast
- **[API Documentation](API_DOCS.md)** - Technical reference
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### 🎬 **Video Workflow**
- **[Video Workflow Guide](VIDEO_WORKFLOW_GUIDE.md)** - Complete video editing tutorial
- **[Video Workflow Summary](VIDEO_WORKFLOW_SUMMARY.md)** - Quick reference

### 🔧 **Development**
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

## 🎯 Use Cases

### 🎨 **Creative Projects**
```python
# Create a futuristic video remix
orchestrator.process_request("""
    Transform my 23-minute video into 60-second segments 
    with futuristic themes and AI-generated imagery
""")
```

### 💻 **Technical Tasks**
```python
# Generate code and optimize performance
orchestrator.process_request("""
    Create a Python function for data analysis 
    and optimize it for large datasets
""")
```

### 📚 **Knowledge Management**
```python
# Research and organize information
orchestrator.process_request("""
    Research AI trends and create a Zettelkasten 
    entry with connections to related topics
""")
```

### ⚡ **Workflow Optimization**
```python
# Optimize complex workflows
orchestrator.process_request("""
    Analyze my current workflow and suggest 
    improvements for efficiency
""")
```

## 🏗️ Architecture

### **Multi-Agent System**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alpha (Α)     │    │   Beta (Β)      │    │  Gamma (Γ)      │
│   Coordinator   │    │   Researcher    │    │  Knowledge      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │   (Central Hub) │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Delta (Δ)     │    │  Epsilon (Ε)    │    │   Zeta (Ζ)      │
│   Optimizer     │    │   Creative      │    │   Technical     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Eta (Η)       │
                    │   Evolution     │
                    └─────────────────┘
```

### **Core Components**
- **Orchestrator**: Central coordination hub
- **Agents**: Specialized AI assistants
- **Modules**: Core functionality (conversation, tasks, knowledge)
- **Interfaces**: CLI and GUI launchers
- **Databases**: Conversation and knowledge storage

## 🎬 Video Processing Example

The B3 system excels at collaborative video editing workflows:

```python
# Complete video editing workflow
async def create_futuristic_remix(video_path):
    """
    Alpha coordinates the project
    Beta researches futuristic themes
    Epsilon creates visual treatment plans
    Zeta implements technical pipeline
    Delta optimizes the workflow
    Eta monitors performance
    Gamma documents the process
    """
    return await orchestrate_video_workflow(video_path, orchestrator)
```

**Output**: 23 unique 60-second segments with AI-generated imagery, futuristic text overlays, and thematic effects.

## 🔧 Configuration

### **Agent Configuration**
```json
{
  "agents": {
    "alpha": {
      "role": "Chief Assistant & Coordinator",
      "model": "mixtral:latest",
      "capabilities": ["coordination", "planning", "communication"]
    }
  }
}
```

### **Video Processing**
```python
# Install video dependencies
pip install moviepy scenedetect pillow numpy

# Configure themes
FUTURISTIC_THEMES = {
    'neon_cyberpunk': {'colors': ['cyan', 'magenta'], 'effects': ['glitch']},
    'green_solarpunk': {'colors': ['lightgreen', 'gold'], 'effects': ['organic']}
}
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Test specific agents
python tutorial/11_test_all_agents.py

# Test video workflow
python demo_video_workflow.py
```

## 📊 Performance

### **System Requirements**
- **CPU**: 4+ cores (32 cores available for parallel processing)
- **RAM**: 8GB+ (127.9GB available)
- **Storage**: 10GB+ (9.3TB available)
- **Python**: 3.8+

### **Capabilities**
- **Parallel Processing**: Multiple agents work simultaneously
- **Resource Monitoring**: Real-time performance tracking
- **Scalability**: Handles complex multi-phase projects
- **Learning**: Continuous improvement through Eta agent

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai) for local AI models
- Inspired by multi-agent AI research
- Community-driven development

## 📞 Support

- **Documentation**: [User Guide](USER_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/b3personalassistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/b3personalassistant/discussions)

---

**B3 Personal Assistant** - Transforming personal productivity through intelligent multi-agent collaboration! 🚀

*Made with ❤️ by the B3 community* 