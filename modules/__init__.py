"""
B3PersonalAssistant Modules

This package contains the functional modules of the personal assistant system.
"""

from .conversation import ConversationManager
from .knowledge import KnowledgeManager
from .tasks import TaskManager
from .resources import ResourceMonitor

__all__ = [
    'ConversationManager',
    'KnowledgeManager', 
    'TaskManager',
    'ResourceMonitor'
] 