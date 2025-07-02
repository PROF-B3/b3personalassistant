# Contributing to B3PersonalAssistant 🤝

> *"Every contribution to this project is a step toward the future of AI assistance."* — Prof. B3

Thank you for your interest in contributing to B3PersonalAssistant! This document provides guidelines for developers who want to contribute to the project.

## 🌟 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Ollama (for testing AI features)
- Basic understanding of multi-agent systems

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/B3PersonalAssistant.git
   cd B3PersonalAssistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## 🏗️ Project Structure

```
B3PersonalAssistant/
├── core/                 # Core system components
│   ├── agents.py        # AI agent implementations
│   ├── orchestrator.py  # Agent coordination
│   └── config.py        # Configuration management
├── modules/             # Feature modules
│   ├── conversation.py  # Chat and memory
│   ├── knowledge.py     # Zettelkasten system
│   ├── tasks.py         # Task management
│   └── resources.py     # System monitoring
├── interfaces/          # User interfaces
│   ├── gui_launcher.py  # Retro terminal GUI
│   └── cli_launcher.py  # Rich CLI
├── tutorial/            # Examples and tests
├── databases/           # Data storage
└── X/                   # Zettelkasten notes
```

## 📝 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable and function names

### Code Formatting
```bash
# Format code with Black
black B3PersonalAssistant/

# Sort imports with isort
isort B3PersonalAssistant/

# Check code style with flake8
flake8 B3PersonalAssistant/
```

### Documentation Standards
- Use Google-style docstrings for all functions and classes
- Include type hints in docstrings
- Add examples for complex functions
- Update README.md for user-facing changes

### Example Docstring
```python
def process_user_input(input_data: str, context: Optional[Dict] = None) -> str:
    """Process user input and return appropriate response.
    
    Args:
        input_data: The user's input string
        context: Optional context dictionary for additional information
        
    Returns:
        Processed response string
        
    Raises:
        ValueError: If input_data is empty
        
    Example:
        >>> process_user_input("Hello", {"user_id": 123})
        "Hello! How can I help you today?"
    """
    if not input_data.strip():
        raise ValueError("Input data cannot be empty")
    
    # Processing logic here
    return f"Processed: {input_data}"
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tutorial/

# Run specific test file
python -m pytest tutorial/test_agents.py

# Run with coverage
python -m pytest --cov=B3PersonalAssistant tutorial/

# Run performance tests
python -m pytest tutorial/test_performance.py
```

### Writing Tests
- Create tests for all new features
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (Ollama API, file system)

### Example Test
```python
import pytest
from unittest.mock import Mock, patch
from core.agents import AlphaAgent

class TestAlphaAgent:
    def test_agent_initialization(self):
        """Test that AlphaAgent initializes correctly."""
        agent = AlphaAgent()
        assert agent.name == "Alpha"
        assert agent.orchestrator is None
    
    @patch('ollama.Client')
    def test_agent_response(self, mock_ollama):
        """Test agent response generation."""
        mock_ollama.return_value.chat.return_value = {
            'message': {'content': 'Test response'}
        }
        
        agent = AlphaAgent()
        response = agent.act("Hello")
        
        assert "Test response" in response
        mock_ollama.return_value.chat.assert_called_once()
```

## 🔧 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code following coding standards
- Add tests for new functionality
- Update documentation
- Test locally

### 3. Commit Changes
```bash
git add .
git commit -m "feat: add new agent communication feature

- Add send_message method to AgentBase
- Implement agent-to-agent communication
- Add tests for communication functionality
- Update documentation"
```

### 4. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No new warnings or errors
- [ ] Performance impact is considered

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Screenshots (if applicable)
Add screenshots for UI changes
```

## 🎯 Contribution Areas

### High Priority
- **Agent Communication**: Improve inter-agent messaging
- **Error Handling**: Enhance error recovery mechanisms
- **Performance**: Optimize response times and resource usage
- **Testing**: Increase test coverage

### Medium Priority
- **New Agents**: Add specialized agents for specific domains
- **UI Improvements**: Enhance GUI and CLI interfaces
- **Integration**: Add support for external APIs
- **Documentation**: Improve user guides and API docs

### Low Priority
- **Plugins**: Create plugin system for extensibility
- **Mobile**: Develop mobile interface
- **Cloud Sync**: Add optional cloud synchronization

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Test with latest version
3. Reproduce the issue
4. Gather system information

### Bug Report Template
```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10, macOS 12]
- Python: [e.g., 3.9.7]
- B3PersonalAssistant: [e.g., 1.0.0]
- Ollama: [e.g., 0.1.0]

## Additional Information
Logs, screenshots, etc.
```

## 🚀 Feature Requests

### Before Requesting
1. Check if feature already exists
2. Consider implementation complexity
3. Think about user impact
4. Prepare use case examples

### Feature Request Template
```markdown
## Feature Description
Clear description of the feature

## Use Case
How this feature would be used

## Implementation Ideas
Optional suggestions for implementation

## Priority
High/Medium/Low

## Additional Context
Any other relevant information
```

## 📚 Documentation

### Contributing to Documentation
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples and screenshots
- Follow markdown best practices

### Documentation Structure
- **README.md**: Project overview and quick start
- **USER_GUIDE.md**: Comprehensive user documentation
- **API_DOCS.md**: Technical API reference
- **CONTRIBUTING.md**: This file
- **TROUBLESHOOTING.md**: Common issues and solutions

## 🏆 Recognition

### Contributors
- All contributors will be listed in the README
- Significant contributions will be highlighted
- Contributors will be mentioned in release notes

### Contribution Levels
- **Bronze**: 1-5 contributions
- **Silver**: 6-15 contributions
- **Gold**: 16+ contributions
- **Platinum**: Core maintainer level

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow project guidelines

### Communication
- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Be patient with responses
- Help maintain a positive community

## 📞 Getting Help

### Resources
- [GitHub Issues](https://github.com/yourusername/B3PersonalAssistant/issues)
- [GitHub Discussions](https://github.com/yourusername/B3PersonalAssistant/discussions)
- [Documentation](https://github.com/yourusername/B3PersonalAssistant/wiki)

### Questions
- Check existing issues and discussions
- Search documentation
- Ask in GitHub Discussions
- Create a new issue if needed

---

**Thank you for contributing to the future of AI assistance!** 

*"Every line of code you write today shapes the intelligence of tomorrow."* — Prof. B3 