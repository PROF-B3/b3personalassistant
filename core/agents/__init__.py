"""
B3PersonalAssistant Agent Package

This package contains all specialized AI agents for the multi-agent system:
- Alpha (Α): Chief Assistant, coordinates, main interface
- Beta (Β): Analyst, research and insights
- Gamma (Γ): Knowledge Manager, Zettelkasten
- Delta (Δ): Task Coordinator, workflow and scheduling
- Epsilon (Ε): Creative Director, media and creative tasks
- Zeta (Ζ): Code Architect, code generation and technical solutions
- Eta (Η): Evolution Engineer, system improvement and optimization

Usage:
    from core.agents import AlphaAgent, get_all_agents

    # Create individual agent
    alpha = AlphaAgent()
    response = alpha.act("Hello")

    # Create all agents
    agents = get_all_agents()
"""

from typing import Dict

from core.agents.base import AgentBase
from core.agents.alpha import AlphaAgent
from core.agents.beta import BetaAgent
from core.agents.gamma import GammaAgent
from core.agents.delta import DeltaAgent
from core.agents.epsilon import EpsilonAgent
from core.agents.zeta import ZetaAgent
from core.agents.eta import EtaAgent


def get_all_agents() -> Dict[str, AgentBase]:
    """
    Instantiate all agents and return as a dictionary.

    Creates instances of all seven Greek agents (Alpha, Beta, Gamma, Delta,
    Epsilon, Zeta, Eta) for use in the multi-agent system.

    Returns:
        Dictionary mapping agent names to agent instances

    Example:
        >>> agents = get_all_agents()
        >>> print(agents.keys())
        dict_keys(['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta'])
        >>> response = agents['alpha'].act("Hello")
    """
    return {
        "alpha": AlphaAgent(),
        "beta": BetaAgent(),
        "gamma": GammaAgent(),
        "delta": DeltaAgent(),
        "epsilon": EpsilonAgent(),
        "zeta": ZetaAgent(),
        "eta": EtaAgent(),
    }


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
]
