"""
Alpha Agent - Chief Assistant and Coordinator

Alpha serves as the main interface and coordinator for the multi-agent system.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import SIMPLE_MODEL, COMPLEX_MODEL, MAX_CONVERSATION_CONTEXT
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class AlphaAgent(AgentBase):
    """
    Alpha (Α) - Chief Assistant and Coordinator

    Alpha serves as the main interface and coordinator for the multi-agent system.
    Responsibilities include:
    - Coordinating other agents for complex tasks
    - Handling strategic planning and decision making
    - Managing user interface and communication
    - Providing high-level summaries and insights

    Personality: Confident, diplomatic, big-picture thinker

    Example:
        >>> alpha = AlphaAgent(user_profile={"communication_style": "formal"})
        >>> response = alpha.act("Coordinate a research project")
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Alpha agent with chief assistant capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Alpha', orchestrator, user_profile, resource_monitor)

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Alpha-specific system prompt."""
        return """You are Alpha (Α), the Chief Assistant and Coordinator of B3PersonalAssistant. You are:
- The primary interface and coordinator for all user interactions
- Strategic, diplomatic, and focused on the big picture
- Skilled at breaking down complex tasks and delegating to specialized agents
- Confident in decision-making and providing clear direction
- Focused on user goals and outcomes

Your role is to understand user requests, coordinate with other agents when needed (Beta for research, Gamma for knowledge, Delta for tasks, Epsilon for creative work, Zeta for code, Eta for improvements), and provide cohesive, actionable responses.

Key phrases: "I'll coordinate that for you", "Let's approach this strategically", "I've analyzed the situation"
Always provide clear, confident, and well-structured responses."""

    @track_agent_performance('Alpha', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle user requests and coordinate with other agents.

        Args:
            input_data: User input text
            context: Optional context dictionary

        Returns:
            Coordinated response from Alpha and other agents
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            complexity = self.estimate_complexity(validated_input)
            model = COMPLEX_MODEL if complexity == "complex" else SIMPLE_MODEL

            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            messages = [{"role": "system", "content": self.system_prompt(context)}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Alpha calling Ollama with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Alpha input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Alpha circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Alpha Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Alpha act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)
