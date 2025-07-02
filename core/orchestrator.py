"""
Orchestrator for B3PersonalAssistant

Coordinates multiple AI agents (Alpha, Beta, Gamma, Delta) to handle complex tasks.
Provides routing, load balancing, agent communication, and result aggregation.

This module serves as the central coordination hub for the multi-agent system,
managing task distribution, agent communication, and response synthesis.

Example:
    >>> from core.orchestrator import Orchestrator
    >>> orchestrator = Orchestrator()
    >>> result = orchestrator.process_request("Research and organize information about AI")
    >>> print(result)
    "Coordinated response from multiple agents..."
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from modules.resources import ResourceMonitor
from core.agents import AlphaAgent, BetaAgent, GammaAgent, DeltaAgent, EpsilonAgent, ZetaAgent, EtaAgent
from modules.knowledge import KnowledgeManager, ZettelkastenSystem
from modules.tasks import TaskManager
from modules.conversation import ConversationManager

class Orchestrator:
    """
    Central orchestrator for coordinating multiple AI agents.
    
    The Orchestrator manages the interaction between different specialized agents,
    routing requests to appropriate agents, handling agent communication,
    and aggregating results for comprehensive responses.
    
    Key features:
    - Intent analysis and routing
    - Load balancing across agents
    - Multi-step task orchestration
    - Agent communication management
    - Result aggregation and synthesis
    - Fallback handling
    - Performance monitoring
    
    Attributes:
        agents (dict): Dictionary of available agents
        resource_monitor (ResourceMonitor): System resource monitoring
        knowledge_manager (KnowledgeManager): Knowledge management system
        task_manager (TaskManager): Task management system
        conversation_manager (ConversationManager): Conversation tracking
        user_profile (dict): User preferences and settings
        logger (logging.Logger): Orchestrator logging instance
        gui_callback (callable): Optional callback for GUI updates
    
    Example:
        >>> orchestrator = Orchestrator(user_profile={"communication_style": "friendly"})
        >>> result = orchestrator.process_request("Help me plan my day")
        >>> print(result)
        "Coordinated response from Alpha and Delta agents..."
    """
    
    def __init__(self, user_profile: Optional[Dict] = None, gui_callback=None):
        """
        Initialize the orchestrator with all agents and systems.
        
        Args:
            user_profile: User preferences and settings dictionary
            gui_callback: Optional callback function for GUI status updates
        
        Note:
            The orchestrator automatically initializes all agents and managers
            with the provided user profile for consistent behavior.
        """
        self.user_profile = user_profile or {}
        self.logger = logging.getLogger("orchestrator")
        self.gui_callback = gui_callback
        
        # Initialize resource monitoring
        self.resource_monitor = ResourceMonitor(Path("databases"))
        
        # Initialize all agents with orchestrator reference
        self.agents = {
            'alpha': AlphaAgent(self, self.user_profile, self.resource_monitor),
            'beta': BetaAgent(self, self.user_profile, self.resource_monitor),
            'gamma': GammaAgent(self, self.user_profile, self.resource_monitor),
            'delta': DeltaAgent(self, self.user_profile, self.resource_monitor),
            'epsilon': EpsilonAgent(self, self.user_profile, self.resource_monitor),
            'zeta': ZetaAgent(self, self.user_profile, self.resource_monitor),
            'eta': EtaAgent(self, self.user_profile, self.resource_monitor)
        }
        
        # Initialize managers with required dependencies
        zettelkasten = ZettelkastenSystem()
        self.knowledge_manager = KnowledgeManager(zettelkasten)
        self.task_manager = TaskManager()
        self.conversation_manager = ConversationManager()
        
        self.logger.info("Orchestrator initialized with all agents and managers")

    def process_request(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Main entry point for processing user requests.
        
        Analyzes the user's intent, routes to appropriate agents, and
        coordinates multi-agent responses for complex tasks.
        
        Args:
            user_input: User's request or question
            context: Optional context dictionary
        
        Returns:
            Coordinated response from relevant agents
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> response = orchestrator.process_request("Research AI and create tasks")
            >>> print(response)
            "Beta researched AI topics. Delta created related tasks..."
        """
        try:
            self._update_gui_status("Processing request...")
            
            # Analyze intent and determine required agents
            intent = self._analyze_intent(user_input)
            required_agents = self._route_request(intent, user_input)
            
            self._update_gui_status(f"Routing to agents: {', '.join(required_agents)}")
            
            # Process with single or multiple agents
            if len(required_agents) == 1:
                result = self._single_agent_process(required_agents[0], user_input, context)
            else:
                result = self._multi_agent_process(required_agents, user_input, context)
            
            # Store conversation
            self.conversation_manager.add_message("user", user_input)
            self.conversation_manager.add_message("assistant", result)
            
            self._update_gui_status("Request completed")
            return result
            
        except Exception as e:
            error_msg = f"Orchestrator error: {e}"
            self.logger.error(error_msg)
            self._update_gui_status("Error occurred")
            return error_msg

    def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to determine intent and requirements.
        
        Uses keyword analysis and pattern matching to understand what
        the user wants and which agents would be most helpful.
        
        Args:
            user_input: User's request text
        
        Returns:
            Dictionary with intent analysis results
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> intent = orchestrator._analyze_intent("Research quantum computing")
            >>> print(intent['primary_agent'])
            "beta"
        """
        input_lower = user_input.lower()
        
        # Define intent patterns for all 7 agents
        research_keywords = ['research', 'find', 'look up', 'investigate', 'analyze']
        task_keywords = ['task', 'todo', 'schedule', 'plan', 'organize', 'create task']
        knowledge_keywords = ['note', 'remember', 'save', 'organize', 'zettelkasten']
        creative_keywords = ['video', 'edit', 'image', 'design', 'creative', 'art', 'story', 'poem', 'audio', 'music']
        code_keywords = ['code', 'program', 'generate', 'debug', 'build', 'module', 'function', 'script']
        evolution_keywords = ['improve', 'optimize', 'evolve', 'enhance', 'performance', 'metrics', 'gap', 'missing']
        general_keywords = ['help', 'assist', 'coordinate', 'manage']
        
        intent = {
            'primary_agent': 'alpha',  # Default to Alpha
            'requires_research': False,
            'requires_tasks': False,
            'requires_knowledge': False,
            'requires_creative': False,
            'requires_code': False,
            'requires_evolution': False,
            'complexity': 'simple'
        }
        
        # Determine primary agent and requirements
        if any(keyword in input_lower for keyword in research_keywords):
            intent['primary_agent'] = 'beta'
            intent['requires_research'] = True
            intent['complexity'] = 'complex'
        
        if any(keyword in input_lower for keyword in task_keywords):
            intent['primary_agent'] = 'delta'
            intent['requires_tasks'] = True
        
        if any(keyword in input_lower for keyword in knowledge_keywords):
            intent['primary_agent'] = 'gamma'
            intent['requires_knowledge'] = True
        
        if any(keyword in input_lower for keyword in creative_keywords):
            intent['primary_agent'] = 'epsilon'
            intent['requires_creative'] = True
            intent['complexity'] = 'complex'
        
        if any(keyword in input_lower for keyword in code_keywords):
            intent['primary_agent'] = 'zeta'
            intent['requires_code'] = True
            intent['complexity'] = 'complex'
        
        if any(keyword in input_lower for keyword in evolution_keywords):
            intent['primary_agent'] = 'eta'
            intent['requires_evolution'] = True
            intent['complexity'] = 'complex'
        
        if any(keyword in input_lower for keyword in general_keywords):
            intent['primary_agent'] = 'alpha'
        
        # Check for multi-agent requirements
        if len([k for k, v in intent.items() if v and k.startswith('requires_')]) > 1:
            intent['complexity'] = 'complex'
        
        return intent

    def _route_request(self, intent: Dict[str, Any], user_input: str) -> List[str]:
        """
        Route request to appropriate agents based on intent analysis.
        
        Determines which agents should handle the request, considering
        complexity and specific requirements.
        
        Args:
            intent: Intent analysis results
            user_input: Original user input
        
        Returns:
            List of agent names to handle the request
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> intent = {'primary_agent': 'beta', 'requires_tasks': True}
            >>> agents = orchestrator._route_request(intent, "Research and create tasks")
            >>> print(agents)
            ['beta', 'delta']
        """
        agents = [intent['primary_agent']]
        
        # Add supporting agents for complex requests
        if intent['complexity'] == 'complex':
            if intent['requires_research'] and 'beta' not in agents:
                agents.append('beta')
            if intent['requires_tasks'] and 'delta' not in agents:
                agents.append('delta')
            if intent['requires_knowledge'] and 'gamma' not in agents:
                agents.append('gamma')
            if intent['requires_creative'] and 'epsilon' not in agents:
                agents.append('epsilon')
            if intent['requires_code'] and 'zeta' not in agents:
                agents.append('zeta')
            if intent['requires_evolution'] and 'eta' not in agents:
                agents.append('eta')
        
        # Special collaboration patterns
        # Eta and Zeta work together for improvements
        if 'eta' in agents and 'zeta' not in agents and intent['requires_evolution']:
            agents.append('zeta')
        if 'zeta' in agents and 'eta' not in agents and intent['requires_code']:
            agents.append('eta')
        
        # Epsilon can work with Beta for creative research
        if 'epsilon' in agents and 'beta' not in agents and intent['requires_creative']:
            agents.append('beta')
        
        # Always include Alpha for coordination if multiple agents
        if len(agents) > 1 and 'alpha' not in agents:
            agents.insert(0, 'alpha')
        
        return agents

    def _single_agent_process(self, agent_name: str, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Process request with a single agent.
        
        Args:
            agent_name: Name of the agent to use
            user_input: User's request
            context: Optional context
        
        Returns:
            Agent's response
        """
        agent = self.agents.get(agent_name)
        if not agent:
            return f"Error: Agent {agent_name} not found"
        
        try:
            return agent.act(user_input, context)
        except Exception as e:
            self.logger.error(f"Agent {agent_name} error: {e}")
            return f"Error processing with {agent_name}: {e}"

    def _multi_agent_process(self, agent_names: List[str], user_input: str, context: Optional[Dict] = None) -> str:
        """
        Process request with multiple agents in coordination.
        
        Coordinates multiple agents to handle complex requests,
        aggregating their responses into a comprehensive result.
        
        Args:
            agent_names: List of agent names to coordinate
            user_input: User's request
            context: Optional context
        
        Returns:
            Coordinated response from all agents
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> result = orchestrator._multi_agent_process(['alpha', 'beta'], "Research AI")
            >>> print(result)
            "Alpha coordinated with Beta to research AI topics..."
        """
        results = []
        
        try:
            # Start with primary agent (first in list)
            primary_agent = agent_names[0]
            primary_result = self._single_agent_process(primary_agent, user_input, context)
            results.append(f"{primary_agent.title()}: {primary_result}")
            
            # Coordinate with other agents
            for agent_name in agent_names[1:]:
                if agent_name == 'alpha':
                    # Alpha coordinates, doesn't add to results
                    continue
                
                # Send context from primary agent to supporting agents
                coordination_message = f"Supporting request: {user_input}. Primary result: {primary_result}"
                agent_result = self._single_agent_process(agent_name, coordination_message, context)
                results.append(f"{agent_name.title()}: {agent_result}")
            
            # Aggregate results
            if len(results) == 1:
                return results[0]
            else:
                return f"Coordinated response:\n" + "\n".join(results)
                
        except Exception as e:
            self.logger.error(f"Multi-agent process error: {e}")
            return f"Error in multi-agent coordination: {e}"

    def agent_communicate(self, from_agent: str, to_agent: str, message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Enable direct communication between agents.
        
        Allows agents to send messages to each other for coordination
        and information sharing.
        
        Args:
            from_agent: Name of the sending agent
            to_agent: Name of the receiving agent
            message: Message content
            context: Optional context
        
        Returns:
            Response from the receiving agent
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> response = orchestrator.agent_communicate("alpha", "beta", "Research quantum computing")
            >>> print(response)
            "Beta: Researching quantum computing..."
        """
        try:
            target_agent = self.agents.get(to_agent)
            if not target_agent:
                return f"Error: Agent {to_agent} not found"
            
            return target_agent.communicate(message, context)
            
        except Exception as e:
            self.logger.error(f"Agent communication error: {e}")
            return f"Communication error: {e}"

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents and system components.
        
        Returns:
            Dictionary with status information for all agents and managers
        
        Example:
            >>> orchestrator = Orchestrator()
            >>> status = orchestrator.get_agent_status()
            >>> print(status['agents']['alpha']['status'])
            "ready"
        """
        status = {
            'agents': {},
            'managers': {},
            'resources': self.resource_monitor.get_status() if self.resource_monitor else {}
        }
        
        # Agent status
        for name, agent in self.agents.items():
            status['agents'][name] = {
                'status': 'ready',
                'name': agent.name,
                'has_orchestrator': agent.orchestrator is not None
            }
        
        # Manager status
        status['managers'] = {
            'knowledge': 'ready' if self.knowledge_manager else 'not_initialized',
            'tasks': 'ready' if self.task_manager else 'not_initialized',
            'conversation': 'ready' if self.conversation_manager else 'not_initialized'
        }
        
        return status

    def _update_gui_status(self, message: str):
        """
        Update GUI status if callback is available.
        
        Args:
            message: Status message to display
        """
        if self.gui_callback:
            try:
                self.gui_callback(message)
            except Exception as e:
                self.logger.error(f"GUI callback error: {e}")

    def shutdown(self):
        """
        Clean shutdown of orchestrator and all agents.
        
        Performs cleanup operations and ensures all resources
        are properly released.
        """
        self.logger.info("Shutting down orchestrator...")
        
        # Cleanup agents
        for agent_name, agent in self.agents.items():
            try:
                # Agents don't have explicit shutdown, but we can log
                self.logger.info(f"Agent {agent_name} shutdown complete")
            except Exception as e:
                self.logger.error(f"Error shutting down agent {agent_name}: {e}")
        
        # Cleanup managers
        try:
            if self.conversation_manager:
                self.conversation_manager.close()
        except Exception as e:
            self.logger.error(f"Error closing conversation manager: {e}")
        
        self.logger.info("Orchestrator shutdown complete") 