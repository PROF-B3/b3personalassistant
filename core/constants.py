"""
Constants for B3PersonalAssistant

This module centralizes all magic numbers, configuration values, and constants
used throughout the application. This improves maintainability by having all
configurable values in one place.
"""

from pathlib import Path

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Ollama model selection for different complexity levels
SIMPLE_MODEL = "llama3.2:3b"  # Fast, good for simple tasks
COMPLEX_MODEL = "mixtral"     # Slower, better for complex analysis

# Default timeout for Ollama API calls (seconds)
DEFAULT_OLLAMA_TIMEOUT = 30.0

# Retry configuration for API calls
MAX_RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.0
RETRY_MAX_DELAY = 10.0

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Default database directory
DATABASE_DIR = Path("databases")

# SQLite database paths
CONVERSATIONS_DB_PATH = "databases/conversations.db"
TASKS_DB_PATH = "databases/tasks.db"
KNOWLEDGE_DB_PATH = "X/_metadata/zettelkasten.db"

# =============================================================================
# INPUT VALIDATION
# =============================================================================

# Maximum input length for user requests
MAX_INPUT_LENGTH = 10000

# =============================================================================
# CIRCUIT BREAKER CONFIGURATION
# =============================================================================

# Circuit breaker thresholds
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
CIRCUIT_BREAKER_TIMEOUT = 60.0

# =============================================================================
# RESOURCE MONITORING
# =============================================================================

# Ollama health check timeout (seconds)
OLLAMA_HEALTH_TIMEOUT = 2.0

# Resource throttling thresholds (percentage)
CPU_THROTTLE_THRESHOLD = 95.0
MEMORY_THROTTLE_THRESHOLD = 90.0
DISK_THROTTLE_THRESHOLD = 95.0

# Performance tracking intervals
METRICS_COLLECTION_INTERVAL = 60.0  # seconds

# =============================================================================
# CONVERSATION HISTORY
# =============================================================================

# Default limit for conversation history retrieval
DEFAULT_CONVERSATION_HISTORY_LIMIT = 10

# Maximum conversation history for AI context
MAX_CONVERSATION_CONTEXT = 5

# =============================================================================
# KNOWLEDGE MANAGEMENT (ZETTELKASTEN)
# =============================================================================

# Default base path for Zettelkasten notes
ZETTELKASTEN_BASE_PATH = "X"

# Search results limits
DEFAULT_SEARCH_LIMIT = 5
MAX_SEARCH_RESULTS = 100

# =============================================================================
# TASK MANAGEMENT
# =============================================================================

# Default number of tasks to display
DEFAULT_TASK_LIST_LIMIT = 10

# Seconds in a day (for date calculations)
SECONDS_PER_DAY = 86400

# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

# Agent names (Greek letters)
AGENT_NAMES = [
    "Alpha",    # Chief Assistant
    "Beta",     # Analyst/Researcher
    "Gamma",    # Knowledge Manager
    "Delta",    # Task Coordinator
    "Epsilon",  # Creative Director
    "Zeta",     # Code Architect
    "Eta",      # Evolution Engineer
]

# Supported programming languages for code generation
SUPPORTED_LANGUAGES = ['python', 'javascript', 'bash', 'sql', 'html', 'css']

# =============================================================================
# ACADEMIC SEARCH
# =============================================================================

# Default academic search sources
DEFAULT_SEARCH_SOURCES = ["arxiv", "crossref", "semantic_scholar"]

# Maximum papers to return
DEFAULT_PAPER_LIMIT = 5

# =============================================================================
# DOCUMENT PROCESSING
# =============================================================================

# Truncation limits for display
ABSTRACT_TRUNCATE_LENGTH = 200
TITLE_TRUNCATE_LENGTH = 50
MESSAGE_TRUNCATE_LENGTH = 100

# =============================================================================
# UI PRIORITY ICONS
# =============================================================================

PRIORITY_ICONS = {
    "URGENT": "🔴",
    "HIGH": "🟡",
    "NORMAL": "🟢",
    "LOW": "⚪",
}

STATUS_ICONS = {
    "TODO": "⬜",
    "IN_PROGRESS": "🔄",
    "COMPLETED": "✅",
    "BLOCKED": "🚫",
    "CANCELLED": "❌",
}
