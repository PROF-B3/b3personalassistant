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
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration

# Install pre-commit hooks
pre-commit install

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

# Run ALL quality checks at once (recommended)
make quality

# Or run individual checks:
make format        # Format code with black and isort
make lint          # Run flake8 and pylint
make type-check    # Run mypy type checking
make security-check # Run bandit security scan
make test          # Run tests
make test-coverage # Run tests with coverage report

# Commit changes (pre-commit hooks will run automatically)
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

## 📝 Code Standards

> **📖 For detailed quality standards, see [CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md)**

### Python Style Guide

We follow **PEP 8** with these modifications:
- **Line length**: 100 characters (not 79)
- **Formatting**: Use Black for automatic formatting
- **Import sorting**: Use isort
- **Type hints**: Required for all new code in `core/` module

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

### Security Guidelines

**Critical security rules (see [CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md#security-guidelines) for details):**

1. ✅ **Always validate user input** using `InputValidator`
2. ✅ **Use parameterized queries** to prevent SQL injection
3. ✅ **Validate file paths** to prevent path traversal attacks
4. ✅ **Store secrets in environment variables** (use `.env` file, never hardcode)
5. ✅ **Implement timeouts** for all external operations
6. ✅ **Use specific exceptions** (never bare `except:` or catch-all `Exception`)

```python
# Good ✅ - Secure database query
cursor.execute(
    "SELECT * FROM users WHERE email = ?",
    (user_email,)
)

# Bad ❌ - SQL injection vulnerability
cursor.execute(
    f"SELECT * FROM users WHERE email = '{user_email}'"
)

# Good ✅ - Validate and sanitize input
from core.validators import InputValidator

validator = InputValidator()
safe_input = validator.validate_and_sanitize(user_input)

# Good ✅ - Secure file path handling
from pathlib import Path

validated_path = Path(file_path).resolve()
if not validated_path.is_relative_to(base_dir):
    raise ValueError("Invalid file path")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test markers
pytest -m unit            # Fast unit tests only
pytest -m integration     # Integration tests
pytest -m "not slow"      # Skip slow tests

# Run with coverage (use Makefile command)
make test-coverage

# Or run pytest directly
pytest tests/ --cov=core --cov=modules --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_validators.py -v

# Run specific test
pytest tests/test_core.py::test_orchestrator_initialization -v
```

### Coverage Requirements

- **Core modules** (`core/`): 90% coverage target
- **Feature modules** (`modules/`): 80% coverage target
- **UI modules** (`interfaces/`): 70% coverage target

View coverage report: `htmlcov/index.html` after running `make test-coverage`

### Writing Tests

```python
import pytest
from core.validators import InputValidator
from core.exceptions import InputValidationError

# Use pytest markers for test categorization
@pytest.mark.unit
def test_validator_rejects_empty_input():
    """Unit test: fast, isolated, no external dependencies."""
    validator = InputValidator()
    with pytest.raises(InputValidationError, match="too short"):
        validator.validate_and_sanitize("")

@pytest.mark.integration
def test_database_migration_workflow(temp_db):
    """Integration test: tests component interactions."""
    from core.database_migrations import MigrationManager

    manager = MigrationManager(temp_db)
    manager.migrate_up()
    assert manager.get_current_version() > 0

@pytest.mark.slow
def test_bulk_insert_performance():
    """Performance test: may take longer to run."""
    from core.performance import PerformanceTimer

    with PerformanceTimer("bulk_insert") as timer:
        # Perform bulk operation
        pass
    assert timer.elapsed_ms < 1000, "Operation too slow"

# Use parametrized tests for multiple scenarios
@pytest.mark.parametrize("dangerous_input", [
    "<script>alert(1)</script>",
    "javascript:void(0)",
    '<img onerror="alert(1)">',
])
def test_dangerous_patterns(dangerous_input):
    """Test validation rejects dangerous patterns."""
    validator = InputValidator()
    with pytest.raises(InputValidationError):
        validator.validate_and_sanitize(dangerous_input)
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
# Use Makefile commands (recommended)
make help          # Show all available commands
make quality       # Run ALL quality checks
make format        # Format code with black and isort
make lint          # Run flake8 and pylint
make type-check    # Run mypy type checking
make security-check # Run bandit security scan
make test          # Run tests
make test-coverage # Run tests with coverage report
make clean         # Clean build artifacts

# Or run tools individually
black .
isort .
flake8 core/ modules/
mypy core/ modules/
pylint core/ modules/
bandit -r core/ modules/

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