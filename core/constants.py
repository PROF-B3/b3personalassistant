"""
Application Constants for B3PersonalAssistant

Centralized constants to avoid magic numbers and strings throughout the codebase.
"""

from typing import Final

# ===========================
# Database Configuration
# ===========================

# Database paths
DB_DIR: Final[str] = "databases"
CONVERSATIONS_DB: Final[str] = f"{DB_DIR}/conversations.db"
TASKS_DB: Final[str] = f"{DB_DIR}/tasks.db"
KNOWLEDGE_DB: Final[str] = f"{DB_DIR}/knowledge.db"
RESOURCES_DB: Final[str] = f"{DB_DIR}/resources.db"

# Migration settings
MIGRATION_TABLE_NAME: Final[str] = "schema_migrations"

# ===========================
# Validation Constants
# ===========================

# Input validation
MAX_INPUT_LENGTH: Final[int] = 10000  # 10K characters
MAX_CONTEXT_SIZE: Final[int] = 50000  # 50K characters
MIN_INPUT_LENGTH: Final[int] = 1
MAX_FILENAME_LENGTH: Final[int] = 255

# File size limits
MAX_FILE_SIZE_MB: Final[int] = 100
LARGE_FILE_WARNING_MB: Final[int] = 100

# ===========================
# Resilience Configuration
# ===========================

# Circuit breaker defaults
CIRCUIT_BREAKER_FAILURE_THRESHOLD: Final[int] = 5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD: Final[int] = 2
CIRCUIT_BREAKER_TIMEOUT_SECONDS: Final[float] = 60.0

# Retry configuration
DEFAULT_MAX_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RETRY_BASE_DELAY: Final[float] = 1.0
DEFAULT_RETRY_MAX_DELAY: Final[float] = 60.0
DEFAULT_RETRY_EXPONENTIAL_BASE: Final[float] = 2.0

# Timeout configuration
DEFAULT_TIMEOUT_SECONDS: Final[float] = 120.0
OLLAMA_TIMEOUT_SECONDS: Final[float] = 180.0

# ===========================
# AI Model Configuration
# ===========================

# Model selection
SIMPLE_MODEL: Final[str] = "llama3.2:3b"
COMPLEX_MODEL: Final[str] = "mixtral"

# Model parameters
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_TOKENS: Final[int] = 2048
DEFAULT_TOP_P: Final[float] = 0.9

# ===========================
# Agent Configuration
# ===========================

# Agent names
AGENT_ALPHA: Final[str] = "Alpha"
AGENT_BETA: Final[str] = "Beta"
AGENT_GAMMA: Final[str] = "Gamma"
AGENT_DELTA: Final[str] = "Delta"
AGENT_EPSILON: Final[str] = "Epsilon"
AGENT_ZETA: Final[str] = "Zeta"
AGENT_ETA: Final[str] = "Eta"

VALID_AGENT_NAMES: Final[tuple] = (
    AGENT_ALPHA, AGENT_BETA, AGENT_GAMMA, AGENT_DELTA,
    AGENT_EPSILON, AGENT_ZETA, AGENT_ETA
)

# ===========================
# Task Management
# ===========================

# Task priorities
PRIORITY_URGENT_SCORE: Final[int] = 40
PRIORITY_HIGH_SCORE: Final[int] = 30
PRIORITY_MEDIUM_SCORE: Final[int] = 20
PRIORITY_LOW_SCORE: Final[int] = 10

# Task timing
OVERDUE_PRIORITY_BOOST: Final[int] = 100
DUE_SOON_3_DAYS_BOOST: Final[int] = 50
DUE_SOON_7_DAYS_BOOST: Final[int] = 25
DEPENDENCY_MULTIPLIER: Final[int] = 15
BLOCKING_PENALTY: Final[int] = 20

# Workflow analysis
EFFICIENCY_THRESHOLD_LOW: Final[float] = 70.0
COMPLETION_RATE_THRESHOLD: Final[float] = 60.0
URGENT_TASKS_THRESHOLD: Final[int] = 5
IN_PROGRESS_TASKS_THRESHOLD: Final[int] = 10
BLOCKED_TASKS_THRESHOLD: Final[int] = 3

# Time estimates
DEFAULT_TASK_HOURS: Final[float] = 2.0
DEFAULT_WORK_HOURS_PER_DAY: Final[float] = 8.0

# ===========================
# Conversation Management
# ===========================

# History limits
DEFAULT_CONVERSATION_HISTORY_LIMIT: Final[int] = 10
MAX_CONVERSATION_HISTORY_LIMIT: Final[int] = 100

# Search limits
DEFAULT_SEARCH_LIMIT: Final[int] = 50
MAX_SEARCH_RESULTS: Final[int] = 200

# Satisfaction scoring
MIN_SATISFACTION_SCORE: Final[int] = 1
MAX_SATISFACTION_SCORE: Final[int] = 5

# ===========================
# Knowledge Management
# ===========================

# Directory structure
KNOWLEDGE_BASE_DEFAULT: Final[str] = "knowledge_base"
ZETTELKASTEN_METADATA_DIR: Final[str] = "_metadata"

# Category directories
CATEGORY_MAIN_TOPICS: Final[str] = "1"
CATEGORY_SECONDARY_TOPICS: Final[str] = "2"
CATEGORY_FREQUENT_ACCESS: Final[str] = "A"
CATEGORY_QUOTES_EXCERPTS: Final[str] = "Z"

ZETTELKASTEN_CATEGORIES: Final[tuple] = (
    CATEGORY_MAIN_TOPICS,
    CATEGORY_SECONDARY_TOPICS,
    CATEGORY_FREQUENT_ACCESS,
    CATEGORY_QUOTES_EXCERPTS
)

# ID generation
ZETTEL_SUB_NOTE_THRESHOLD: Final[int] = 1000

# ===========================
# UI Configuration
# ===========================

# Window dimensions
DEFAULT_WINDOW_WIDTH: Final[int] = 1400
DEFAULT_WINDOW_HEIGHT: Final[int] = 900
DEFAULT_WINDOW_X: Final[int] = 100
DEFAULT_WINDOW_Y: Final[int] = 100

# Splitter proportions (percentages)
SIDEBAR_FILE_TREE_RATIO: Final[int] = 70
SIDEBAR_AGENTS_RATIO: Final[int] = 30
WORKSPACE_MAIN_RATIO: Final[int] = 70
WORKSPACE_CHAT_RATIO: Final[int] = 30
MAIN_SIDEBAR_WIDTH: Final[int] = 250
MAIN_WORKSPACE_WIDTH: Final[int] = 1150

# Update intervals (milliseconds)
STATUS_UPDATE_INTERVAL_MS: Final[int] = 2000
RESOURCE_MONITOR_INTERVAL_MS: Final[int] = 5000

# ===========================
# Resource Monitoring
# ===========================

# Thresholds
CPU_WARNING_THRESHOLD: Final[float] = 80.0
MEMORY_WARNING_THRESHOLD: Final[float] = 85.0
DISK_WARNING_THRESHOLD: Final[float] = 90.0

# Update rates
RESOURCE_CHECK_INTERVAL_SECONDS: Final[int] = 5

# ===========================
# Logging Configuration
# ===========================

# Log levels
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEBUG_LOG_LEVEL: Final[str] = "DEBUG"
ERROR_LOG_LEVEL: Final[str] = "ERROR"

# Log formatting
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log file sizes
MAX_LOG_FILE_SIZE_MB: Final[int] = 10
MAX_LOG_BACKUP_COUNT: Final[int] = 5

# Structured logging configuration
import os
LOG_LEVEL: Final[str] = os.environ.get("B3_LOG_LEVEL", DEFAULT_LOG_LEVEL)
LOG_FILE_PATH: Final[str] = os.environ.get("B3_LOG_FILE", "logs/b3assistant.log")
LOG_FORMAT_JSON: Final[bool] = os.environ.get("B3_LOG_FORMAT_JSON", "false").lower() == "true"
LOG_MAX_BYTES: Final[int] = MAX_LOG_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
LOG_BACKUP_COUNT: Final[int] = MAX_LOG_BACKUP_COUNT

# ===========================
# Network Configuration
# ===========================

# Git operations
GIT_PUSH_MAX_RETRIES: Final[int] = 4
GIT_RETRY_DELAYS_SECONDS: Final[tuple] = (2, 4, 8, 16)

# ===========================
# Security Configuration
# ===========================

# Allowed fields for dynamic SQL (whitelist)
ALLOWED_CONVERSATION_UPDATE_FIELDS: Final[set] = {
    'end_time', 'sentiment', 'quality_score',
    'user_satisfaction', 'context_summary'
}

# Dangerous patterns for input validation
DANGEROUS_PATTERNS: Final[tuple] = (
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',  # JavaScript protocol
    r'on\w+\s*=',  # Event handlers
    r'<iframe',  # Iframes
    r'<embed',  # Embeds
    r'<object',  # Objects
)

# SQL injection patterns
SQL_INJECTION_PATTERNS: Final[tuple] = (
    r";\s*DROP\s+TABLE",
    r";\s*DELETE\s+FROM",
    r";\s*UPDATE\s+",
    r"UNION\s+SELECT",
    r"--\s*$",
    r"/\*.*\*/",
)

# ===========================
# Environment Variables
# ===========================

# Environment variable names
ENV_ZETTELKASTEN_PATH: Final[str] = "B3_ZETTELKASTEN_PATH"
ENV_OPENAI_API_KEY: Final[str] = "B3_OPENAI_API_KEY"
ENV_ANTHROPIC_API_KEY: Final[str] = "B3_ANTHROPIC_API_KEY"
ENV_LOG_LEVEL: Final[str] = "B3_LOG_LEVEL"
ENV_DATABASE_PATH: Final[str] = "B3_DATABASE_PATH"

# ===========================
# File Type Extensions
# ===========================

# Document types
PDF_EXTENSION: Final[str] = ".pdf"
MARKDOWN_EXTENSIONS: Final[tuple] = (".md", ".txt")
VIDEO_EXTENSIONS: Final[tuple] = (".mp4", ".avi", ".mov", ".mkv")
IMAGE_EXTENSIONS: Final[tuple] = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# ===========================
# Performance Metrics
# ===========================

# Time windows for metrics
METRICS_WINDOW_30_DAYS: Final[int] = 30
METRICS_WINDOW_7_DAYS: Final[int] = 7
METRICS_WINDOW_24_HOURS: Final[int] = 1

# Performance thresholds
SLOW_QUERY_THRESHOLD_MS: Final[int] = 100
SLOW_OPERATION_THRESHOLD_MS: Final[int] = 1000

# ===========================
# Version Information
# ===========================

# Application version
APP_VERSION: Final[str] = "0.1.0-alpha"
MIN_PYTHON_VERSION: Final[tuple] = (3, 8)

# Schema versions
CURRENT_SCHEMA_VERSION: Final[int] = 1
