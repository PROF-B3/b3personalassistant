"""
B3PersonalAssistant - Multi-Agent AI Personal Assistant

A sophisticated personal assistant system that leverages local Ollama models
to provide comprehensive assistance through four specialized Greek AI agents:
Alpha, Beta, Gamma, and Delta.
"""

__version__ = "1.0.0"
__author__ = "B3PersonalAssistant Team"
__email__ = "contact@b3personalassistant.com"
__description__ = "A multi-agent AI personal assistant system using local Ollama models"

# Import main components for easy access
from core.config import ConfigManager
# from .core.orchestrator import AgentOrchestrator
from .core.agents import AlphaAgent, BetaAgent, GammaAgent, DeltaAgent

from .modules.conversation import ConversationManager
# from .modules.knowledge import ZettelkastenManager
from .modules.tasks import TaskManager
from .modules.resources import ResourceMonitor

from .interfaces.gui_launcher import launch_gui
# from .interfaces.cli_launcher import CLILauncher

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    
    # Core components
    'ConfigManager',
    # 'AgentOrchestrator',
    'AlphaAgent',
    'BetaAgent', 
    'GammaAgent',
    'DeltaAgent',
    
    # Modules
    'ConversationManager',
    # 'ZettelkastenManager',
    'TaskManager',
    'ResourceMonitor',
    
    # Interfaces
    'launch_gui',
    # 'CLILauncher',
]


def get_version():
    """Get the current version of B3PersonalAssistant"""
    return __version__


def get_info():
    """Get basic information about B3PersonalAssistant"""
    return {
        'name': 'B3PersonalAssistant',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'description': __description__,
    }


# Quick setup function for easy initialization
def setup_assistant(config_path=None):
    """
    Quick setup function to initialize all components
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        dict: Dictionary containing all initialized components
    """
    from pathlib import Path
    
    # Load configuration
    if config_path:
        config_manager = ConfigManager(str(config_path))
        config = config_manager.config
    else:
        config_manager = ConfigManager()
        config = config_manager.config
    
    # Initialize components
    # orchestrator = AgentOrchestrator(config)
    # conversation_manager = ConversationManager(config.databases_dir / "conversations")
    # zettelkasten_manager = ZettelkastenManager(config.zettelkasten_dir)
    # task_manager = TaskManager(config.databases_dir / "tasks")
    # resource_monitor = ResourceMonitor(config.databases_dir / "resources")
    
    return {
        'config': config,
        # 'orchestrator': orchestrator,
        # 'conversation_manager': conversation_manager,
        # 'zettelkasten_manager': zettelkasten_manager,
        # 'task_manager': task_manager,
        # 'resource_monitor': resource_monitor,
    } 