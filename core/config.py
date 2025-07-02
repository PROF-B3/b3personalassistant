"""
Configuration Management for B3PersonalAssistant
Handles all system settings, AI models, agent personalities, and user preferences.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Theme(Enum):
    """GUI theme options."""
    DARK = "dark"
    LIGHT = "light"
    RETRO = "retro"
    MODERN = "modern"

class ModelType(Enum):
    """AI model types."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

@dataclass
class AIModelConfig:
    """Configuration for AI models."""
    model_type: ModelType = ModelType.OLLAMA
    model_name: str = "llama2"
    base_url: str = "http://localhost:11434"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30

@dataclass
class AgentPersonality:
    """Agent personality and system prompt configuration."""
    name: str
    role: str
    personality: str
    system_prompt: str
    color: str = "#007bff"
    model_preference: Optional[str] = None

@dataclass
class DatabaseConfig:
    """Database configuration."""
    conversations_db: str = "databases/conversations.db"
    tasks_db: str = "databases/tasks.db"
    knowledge_db: str = "X/_metadata/zettelkasten.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24

@dataclass
class GUIThemeConfig:
    """GUI theme and appearance settings."""
    theme: Theme = Theme.RETRO
    font_family: str = "Consolas"
    font_size: int = 12
    background_color: str = "#000000"
    text_color: str = "#00ff00"
    accent_color: str = "#ff6600"
    window_width: int = 1200
    window_height: int = 800

@dataclass
class ResourceLimits:
    """System resource limits."""
    max_memory_mb: int = 2048
    max_cpu_percent: int = 80
    max_concurrent_tasks: int = 5
    max_conversation_history: int = 1000
    max_file_size_mb: int = 100

@dataclass
class UserPreferences:
    """User-specific preferences."""
    language: str = "en"
    timezone: str = "UTC"
    notification_enabled: bool = True
    auto_save_interval_minutes: int = 5
    default_agent: str = "Alpha"
    preferred_response_length: str = "medium"  # short, medium, long
    learning_enabled: bool = True

@dataclass
class APIConfig:
    """External API configuration."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    news_api_key: Optional[str] = None

@dataclass
class SystemConfig:
    """Main system configuration."""
    # Core settings
    debug_mode: bool = False
    log_level: str = "INFO"
    data_dir: str = "data"
    
    # AI Models
    ai_models: Dict[str, AIModelConfig] = field(default_factory=lambda: {
        "default": AIModelConfig(),
        "alpha": AIModelConfig(model_name="llama2", temperature=0.8),
        "beta": AIModelConfig(model_name="codellama", temperature=0.6),
        "gamma": AIModelConfig(model_name="llama2", temperature=0.7),
        "delta": AIModelConfig(model_name="llama2", temperature=0.5)
    })
    
    # Agent Personalities
    agent_personalities: Dict[str, AgentPersonality] = field(default_factory=lambda: {
        "Alpha": AgentPersonality(
            name="Alpha",
            role="Chief Assistant",
            personality="Wise, helpful, and comprehensive. Always provides detailed and thoughtful responses.",
            system_prompt="You are Alpha, the Chief Assistant. You coordinate with other agents and provide comprehensive assistance.",
            color="#007bff"
        ),
        "Beta": AgentPersonality(
            name="Beta",
            role="Analyst",
            personality="Analytical, research-focused, and detail-oriented. Excels at data analysis and research.",
            system_prompt="You are Beta, the Analyst. You specialize in research, data analysis, and detailed investigations.",
            color="#28a745"
        ),
        "Gamma": AgentPersonality(
            name="Gamma",
            role="Knowledge Manager",
            personality="Organized, systematic, and knowledge-focused. Manages information and creates connections.",
            system_prompt="You are Gamma, the Knowledge Manager. You organize information and create knowledge connections.",
            color="#ffc107"
        ),
        "Delta": AgentPersonality(
            name="Delta",
            role="Task Coordinator",
            personality="Efficient, organized, and action-oriented. Focuses on task management and optimization.",
            system_prompt="You are Delta, the Task Coordinator. You manage tasks, schedules, and workflow optimization.",
            color="#dc3545"
        )
    })
    
    # Database configuration
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # GUI configuration
    gui: GUIThemeConfig = field(default_factory=GUIThemeConfig)
    
    # Resource limits
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    
    # User preferences
    user_prefs: UserPreferences = field(default_factory=UserPreferences)
    
    # API configuration
    api: APIConfig = field(default_factory=APIConfig)

class ConfigManager:
    """Manages configuration loading, validation, and updates."""
    
    def __init__(self, config_file: str = "config.json", profile: str = "default"):
        self.config_file = Path(config_file)
        self.profile = profile
        self.config = SystemConfig()
        self.load_config()
    
    def load_config(self):
        """Load configuration from multiple sources with priority order."""
        # 1. Load defaults
        self.config = SystemConfig()
        
        # 2. Load from JSON config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    json_config = json.load(f)
                self._update_from_dict(json_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # 3. Load from environment variables
        self._load_from_env()
        
        # 4. Load from command line arguments
        self._load_from_cli()
        
        # 5. Validate configuration
        self._validate_config()
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                if key == "ai_models" and isinstance(value, dict):
                    for model_name, model_config in value.items():
                        if isinstance(model_config, dict):
                            self.config.ai_models[model_name] = AIModelConfig(**model_config)
                elif key == "agent_personalities" and isinstance(value, dict):
                    for agent_name, agent_config in value.items():
                        if isinstance(agent_config, dict):
                            self.config.agent_personalities[agent_name] = AgentPersonality(**agent_config)
                elif key == "database" and isinstance(value, dict):
                    self.config.database = DatabaseConfig(**value)
                elif key == "gui" and isinstance(value, dict):
                    if "theme" in value:
                        value["theme"] = Theme(value["theme"])
                    self.config.gui = GUIThemeConfig(**value)
                elif key == "resources" and isinstance(value, dict):
                    self.config.resources = ResourceLimits(**value)
                elif key == "user_prefs" and isinstance(value, dict):
                    self.config.user_prefs = UserPreferences(**value)
                elif key == "api" and isinstance(value, dict):
                    self.config.api = APIConfig(**value)
                else:
                    setattr(self.config, key, value)
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "B3_DEBUG_MODE": ("debug_mode", bool),
            "B3_LOG_LEVEL": ("log_level", str),
            "B3_DATA_DIR": ("data_dir", str),
            "B3_DEFAULT_MODEL": ("ai_models.default.model_name", str),
            "B3_OLLAMA_URL": ("ai_models.default.base_url", str),
            "B3_OPENAI_API_KEY": ("api.openai_api_key", str),
            "B3_ANTHROPIC_API_KEY": ("api.anthropic_api_key", str),
            "B3_GUI_THEME": ("gui.theme", lambda x: Theme(x)),
            "B3_MAX_MEMORY_MB": ("resources.max_memory_mb", int),
            "B3_MAX_CPU_PERCENT": ("resources.max_cpu_percent", int),
            "B3_DEFAULT_AGENT": ("user_prefs.default_agent", str),
            "B3_LANGUAGE": ("user_prefs.language", str),
        }
        
        for env_var, (config_path, converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = converter(os.environ[env_var])
                    self._set_nested_config(config_path, value)
                except Exception as e:
                    logger.warning(f"Failed to parse environment variable {env_var}: {e}")
    
    def _set_nested_config(self, path: str, value: Any):
        """Set nested configuration value using dot notation."""
        parts = path.split('.')
        obj = self.config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return
        if hasattr(obj, parts[-1]):
            setattr(obj, parts[-1], value)
    
    def _load_from_cli(self):
        """Load configuration from command line arguments."""
        parser = argparse.ArgumentParser(description="B3PersonalAssistant Configuration")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument("--config", type=str, help="Configuration file path")
        parser.add_argument("--model", type=str, help="Default AI model name")
        parser.add_argument("--theme", type=str, help="GUI theme")
        parser.add_argument("--max-memory", type=int, help="Maximum memory usage in MB")
        
        args, _ = parser.parse_known_args()
        
        if args.debug:
            self.config.debug_mode = True
        if args.model:
            self.config.ai_models["default"].model_name = args.model
        if args.theme:
            try:
                self.config.gui.theme = Theme(args.theme)
            except ValueError:
                logger.warning(f"Invalid theme: {args.theme}")
        if args.max_memory:
            self.config.resources.max_memory_mb = args.max_memory
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate AI models
        for model_name, model_config in self.config.ai_models.items():
            if not isinstance(model_config.temperature, (int, float)) or not 0 <= model_config.temperature <= 2:
                logger.warning(f"Invalid temperature for model {model_name}: {model_config.temperature}")
                model_config.temperature = 0.7
        
        # Validate resource limits
        if self.config.resources.max_memory_mb <= 0:
            logger.warning("Invalid max memory, setting to default")
            self.config.resources.max_memory_mb = 2048
        
        if not 1 <= self.config.resources.max_cpu_percent <= 100:
            logger.warning("Invalid max CPU percent, setting to default")
            self.config.resources.max_cpu_percent = 80
        
        # Validate database paths
        for db_path in [self.config.database.conversations_db, 
                       self.config.database.tasks_db]:
            db_dir = Path(db_path).parent
            if not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to JSON file."""
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = self.config_file
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert configuration to dictionary
        config_dict = self._config_to_dict()
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = asdict(self.config)
        
        # Convert enums to strings
        config_dict["gui"]["theme"] = config_dict["gui"]["theme"].value
        
        return config_dict
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentPersonality]:
        """Get configuration for a specific agent."""
        return self.config.agent_personalities.get(agent_name)
    
    def get_model_config(self, model_name: str = "default") -> AIModelConfig:
        """Get configuration for a specific AI model."""
        return self.config.ai_models.get(model_name, self.config.ai_models["default"])
    
    def update_user_preference(self, key: str, value: Any):
        """Update a user preference."""
        if hasattr(self.config.user_prefs, key):
            setattr(self.config.user_prefs, key, value)
            logger.info(f"Updated user preference: {key} = {value}")
        else:
            logger.warning(f"Unknown user preference: {key}")
    
    def create_profile(self, profile_name: str):
        """Create a new user profile."""
        profile_dir = Path("profiles")
        profile_dir.mkdir(exist_ok=True)
        
        profile_file = profile_dir / f"{profile_name}.json"
        if not profile_file.exists():
            self.save_config(str(profile_file))
            logger.info(f"Created profile: {profile_name}")
        else:
            logger.warning(f"Profile {profile_name} already exists")
    
    def load_profile(self, profile_name: str):
        """Load a user profile."""
        profile_file = Path("profiles") / f"{profile_name}.json"
        if profile_file.exists():
            self.config_file = profile_file
            self.load_config()
            logger.info(f"Loaded profile: {profile_name}")
        else:
            logger.error(f"Profile {profile_name} not found")
    
    def list_profiles(self) -> List[str]:
        """List available user profiles."""
        profile_dir = Path("profiles")
        if profile_dir.exists():
            return [f.stem for f in profile_dir.glob("*.json")]
        return []

# Global configuration instance
_config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def reload_config():
    """Reload configuration from all sources."""
    global _config_manager
    if _config_manager:
        _config_manager.load_config()

if __name__ == "__main__":
    # Test configuration management
    config = get_config()
    print("Configuration loaded successfully!")
    print(f"Default model: {config.get_model_config().model_name}")
    print(f"GUI theme: {config.config.gui.theme.value}")
    print(f"Debug mode: {config.config.debug_mode}") 