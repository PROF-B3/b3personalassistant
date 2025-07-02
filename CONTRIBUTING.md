# 🤝 Contributing Guide

> **How to contribute to B3PersonalAssistant**

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Standards](#code-standards)
4. [Testing](#testing)
5. [Pull Request Process](#pull-request-process)
6. [Documentation](#documentation)
7. [Community Guidelines](#community-guidelines)

## 🚀 Getting Started

### Before You Start

1. **Check existing issues** - Your idea might already be discussed
2. **Read the documentation** - Understand the project structure
3. **Join discussions** - Ask questions in GitHub Discussions
4. **Start small** - Begin with documentation or small fixes

### What We're Looking For

- **Bug fixes** - Help improve stability
- **Feature enhancements** - Add new capabilities
- **Documentation** - Improve guides and examples
- **Testing** - Add tests and improve coverage
- **Performance** - Optimize existing code
- **UI/UX** - Improve interfaces and user experience

## 🔧 Development Setup

### Prerequisites

```bash
# Required tools
- Python 3.9+
- Git
- Ollama (for AI models)
- FFmpeg (for video processing)
```

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/PROF-B3/b3personalassistant.git
cd b3personalassistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Initialize database
python scripts/init_database.py

# Run tests to verify setup
pytest tests/ -v
```

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python run_assistant.py
pytest tests/ -v

# Run linting and formatting
black .
isort .
flake8 .

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

## 📝 Code Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# Good: Clear, readable code
def process_user_request(request: str) -> dict:
    """Process user request and return response."""
    try:
        result = orchestrator.process_request(request)
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Bad: Unclear, hard to read
def proc_req(r):
    try:
        return {"s":True,"r":orchestrator.process_request(r)}
    except:
        return {"s":False,"e":"error"}
```

### Naming Conventions

```python
# Classes: PascalCase
class VideoProcessor:
    pass

# Functions and variables: snake_case
def process_video():
    video_path = "input.mp4"

# Constants: UPPER_SNAKE_CASE
MAX_CONCURRENT_TASKS = 5
DEFAULT_MODEL = "llama2"

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Documentation Standards

```python
def create_futuristic_remix(video_path: str, theme: str = "neon_cyberpunk") -> list:
    """
    Create AI-enhanced video segments with futuristic effects.
    
    Args:
        video_path: Path to input video file
        theme: Visual theme for processing (default: "neon_cyberpunk")
    
    Returns:
        List of processed video segment paths
    
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If theme is not supported
    
    Example:
        >>> result = create_futuristic_remix("input.mp4", "green_solarpunk")
        >>> print(f"Created {len(result)} segments")
    """
    # Implementation here
    pass
```

### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import requests
import sqlalchemy as sa
from rich.console import Console

# Local imports
from core.orchestrator import Orchestrator
from modules.video_processing import VideoProcessor
from databases.manager import DatabaseManager
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest tests/ --cov=core --cov=modules --cov-report=html

# Run specific test
pytest tests/test_core.py::test_orchestrator_initialization -v
```

### Writing Tests

```python
import pytest
from core.orchestrator import Orchestrator

class TestOrchestrator:
    """Test cases for Orchestrator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = Orchestrator()
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator is not None
        assert hasattr(self.orchestrator, 'agents')
    
    def test_process_request(self):
        """Test request processing."""
        result = self.orchestrator.process_request("Hello")
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.parametrize("request_text", [
        "Research AI",
        "Create task",
        "Save note"
    ])
    def test_various_requests(self, request_text):
        """Test different types of requests."""
        result = self.orchestrator.process_request(request_text)
        assert result is not None
```

### Test Guidelines

1. **Test coverage** - Aim for 90%+ coverage
2. **Test isolation** - Each test should be independent
3. **Meaningful names** - Test names should describe what they test
4. **Assertions** - Use specific assertions, not just `assert True`
5. **Mocking** - Mock external dependencies (Ollama, file system)

## 🔄 Pull Request Process

### Before Submitting

1. **Update documentation** - Add/update relevant docs
2. **Add tests** - Include tests for new features
3. **Run checks** - Ensure all tests pass and code is formatted
4. **Self-review** - Review your own code before submitting

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Added tests for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process

1. **Automated checks** - CI/CD pipeline runs tests and linting
2. **Code review** - At least one maintainer reviews the PR
3. **Discussion** - Address any feedback or questions
4. **Merge** - PR is merged once approved

## 📚 Documentation

### Documentation Standards

1. **Keep it current** - Update docs when code changes
2. **Be clear** - Use simple, clear language
3. **Include examples** - Show how to use features
4. **Cross-reference** - Link related documentation

### Documentation Types

- **README.md** - Project overview and quick start
- **User Guide** - Complete user manual
- **API Documentation** - Developer reference
- **Code comments** - Inline documentation
- **Tutorials** - Step-by-step guides

### Updating Documentation

```bash
# Update user guide
edit_file USER_GUIDE.md

# Update API docs
edit_file API_DOCS.md

# Update README
edit_file README.md

# Check links
python -c "import markdown; print('Links valid')"
```

## 🌟 Community Guidelines

### Code of Conduct

1. **Be respectful** - Treat everyone with respect
2. **Be inclusive** - Welcome contributors of all backgrounds
3. **Be constructive** - Provide helpful, constructive feedback
4. **Be patient** - Remember that everyone is learning

### Communication

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Pull Requests** - For code contributions
- **Email** - For sensitive or private matters

### Recognition

Contributors are recognized in:
- **README.md** - Contributor list
- **Release notes** - Feature acknowledgments
- **Documentation** - Author credits
- **GitHub** - Commit history and PRs

## 🚀 Getting Help

### Development Resources

- **[User Guide](USER_GUIDE.md)** - Complete system manual
- **[API Documentation](API_DOCS.md)** - Developer reference
- **[Quick Start](QUICK_START.md)** - Get up and running
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues

### Community Support

- **[GitHub Issues](https://github.com/PROF-B3/b3personalassistant/issues)** - Bug reports
- **[Discussions](https://github.com/PROF-B3/b3personalassistant/discussions)** - Questions and ideas
- **[Wiki](https://github.com/PROF-B3/b3personalassistant/wiki)** - Community knowledge

### Development Tools

```bash
# Code formatting
black .
isort .

# Linting
flake8 .
mypy core/ modules/

# Testing
pytest tests/ -v --cov

# Pre-commit hooks
pre-commit run --all-files
```

## 📋 Contribution Checklist

Before submitting your contribution:

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Self-review completed
- [ ] PR description filled out
- [ ] All CI checks passing

---

**Thank you for contributing to B3PersonalAssistant! Your contributions help make this project better for everyone.**

For questions or support, reach out in [GitHub Discussions](https://github.com/PROF-B3/b3personalassistant/discussions). 