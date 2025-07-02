.PHONY: help install install-dev test lint format clean docs build dist

help: ## Show this help message
	@echo "B3PersonalAssistant - Multi-Agent AI Personal Assistant"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	python -m pytest tutorial/ -v --cov=B3PersonalAssistant

test-quick: ## Run tests quickly
	python -m pytest tutorial/ -x

lint: ## Run linting checks
	flake8 B3PersonalAssistant/
	mypy B3PersonalAssistant/
	bandit -r B3PersonalAssistant/

format: ## Format code with black and isort
	black B3PersonalAssistant/
	isort B3PersonalAssistant/

format-check: ## Check code formatting
	black --check B3PersonalAssistant/
	isort --check-only B3PersonalAssistant/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

docs: ## Build documentation
	@echo "Documentation is in markdown format in the root directory"
	@echo "Available docs: README.md, USER_GUIDE.md, API_DOCS.md, etc."

build: ## Build the package
	python -m build

dist: clean build ## Create distribution packages

run: ## Run the assistant
	python run_assistant.py

run-gui: ## Run the GUI interface
	python -m B3PersonalAssistant.interfaces.gui_launcher

run-cli: ## Run the CLI interface
	python -m B3PersonalAssistant.interfaces.cli_launcher

setup-profile: ## Set up user profile
	python setup_user_profile.py

backup: ## Create backup of data
	python -c "from core.orchestrator import Orchestrator; Orchestrator().backup_data()"

restore: ## Restore from backup (specify backup file)
	@echo "Usage: make restore BACKUP_FILE=backup_20240115.tar.gz"
	python -c "from core.orchestrator import Orchestrator; Orchestrator().restore_data('$(BACKUP_FILE)')"

check-system: ## Check system status
	python -c "from modules.resources import ResourceMonitor; print(ResourceMonitor(Path('databases')).get_cli_status())"

install-ollama: ## Install Ollama (macOS/Linux)
	curl -fsSL https://ollama.ai/install.sh | sh

pull-models: ## Pull required Ollama models
	ollama pull llama2
	ollama pull mistral

all: install-dev format lint test ## Run all checks (install, format, lint, test) 