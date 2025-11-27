"""
Greek AI Agents for B3PersonalAssistant

This module provides backward-compatible imports from the new modular agent structure.

Implements seven specialized agents:
- Alpha (Α): Chief Assistant, coordinates, main interface
- Beta (Β): Analyst, research and insights
- Gamma (Γ): Knowledge Manager, Zettelkasten
- Delta (Δ): Task Coordinator, workflow and scheduling
- Epsilon (Ε): Creative Director, media and creative tasks
- Zeta (Ζ): Code Architect, code generation and technical solutions
- Eta (Η): Evolution Engineer, system improvement and optimization

All agents use Ollama models, communicate, and store conversations in SQLite.

This module provides the foundation for multi-agent AI collaboration, with each agent
specializing in different aspects of personal assistance. Agents can communicate with
each other through the orchestrator and adapt their responses based on user preferences.

Example:
    >>> from core.agents import AlphaAgent
    >>> alpha = AlphaAgent(user_profile={"communication_style": "friendly"})
    >>> response = alpha.act("Hello, how can you help me?")

Note:
    This module is now a wrapper that imports from the core.agents package.
    For new code, prefer importing directly from core.agents:

    from core.agents import AlphaAgent, BetaAgent, get_all_agents
"""

# Import all agents from the modular structure for backward compatibility
from core.agents import (
    AgentBase,
    AlphaAgent,
    BetaAgent,
    GammaAgent,
    DeltaAgent,
    EpsilonAgent,
    ZetaAgent,
    EtaAgent,
    get_all_agents,
)

# Also import constants for backward compatibility
from core.constants import (
    SIMPLE_MODEL,
    COMPLEX_MODEL,
    CONVERSATIONS_DB_PATH as DB_PATH,
)

__all__ = [
    "AgentBase",
    "AlphaAgent",
    "BetaAgent",
    "GammaAgent",
    "DeltaAgent",
    "EpsilonAgent",
    "ZetaAgent",
    "EtaAgent",
    "get_all_agents",
    "SIMPLE_MODEL",
    "COMPLEX_MODEL",
    "DB_PATH",
]
