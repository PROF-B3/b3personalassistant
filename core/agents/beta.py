"""
Beta Agent - Analyst and Researcher

Beta specializes in research, data analysis, and generating insights.
"""

import re
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import (
    COMPLEX_MODEL,
    MAX_CONVERSATION_CONTEXT,
    DEFAULT_SEARCH_SOURCES,
    DEFAULT_PAPER_LIMIT,
    ABSTRACT_TRUNCATE_LENGTH,
)
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class BetaAgent(AgentBase):
    """
    Beta (Β) - Analyst and Researcher

    Beta specializes in research, data analysis, and generating insights.
    Responsibilities include:
    - Information gathering and fact-checking
    - Data analysis and synthesis
    - Research and trend analysis
    - Generating insights and recommendations

    Personality: Curious, analytical, detail-oriented

    Example:
        >>> beta = BetaAgent(user_profile={"communication_style": "concise"})
        >>> response = beta.act("Research AI trends")
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Beta agent with analytical capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Beta', orchestrator, user_profile, resource_monitor)

        from modules.academic_search import create_academic_search
        self.academic_search = create_academic_search()

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Beta-specific system prompt."""
        return """You are Beta (Β), the Research Analyst of B3PersonalAssistant. You are:
- Analytical, curious, and detail-oriented
- Expert at gathering, analyzing, and synthesizing information
- Skilled at fact-checking, data analysis, and identifying patterns
- Focused on providing thorough, well-researched insights
- Precise and methodical in your approach

Your role is to conduct research, analyze data, identify trends, and provide comprehensive insights with supporting evidence. You excel at breaking down complex topics and presenting findings clearly.

Key phrases: "Based on my analysis", "The data suggests", "Let me investigate", "My research shows"
Always provide evidence-based, well-structured analysis with clear conclusions."""

    def _handle_search_command(self, input_text: str) -> Optional[str]:
        """
        Handle academic search commands.

        Args:
            input_text: User input text

        Returns:
            Response string if command was handled, None otherwise
        """
        input_lower = input_text.lower()

        search_keywords = ['search papers', 'search for papers', 'find papers', 'find articles']
        if any(keyword in input_lower for keyword in search_keywords):
            query_match = re.search(
                r'(?:search (?:papers|for papers|articles)|find (?:papers|articles))(?:\s+(?:on|about|for))?\s+(.+)',
                input_text,
                re.IGNORECASE
            )

            if query_match:
                query = query_match.group(1).strip()

                papers = self.academic_search.search(
                    query,
                    sources=DEFAULT_SEARCH_SOURCES,
                    limit=DEFAULT_PAPER_LIMIT
                )

                if not papers:
                    return f"📚 No papers found for '{query}'. Try different keywords."

                response = f"📚 Found {len(papers)} papers for '{query}':\n\n"

                for i, paper in enumerate(papers, 1):
                    response += f"**{i}. {paper.title}**\n"

                    if paper.authors:
                        authors_str = ", ".join(paper.authors[:3])
                        if len(paper.authors) > 3:
                            authors_str += " et al."
                        response += f"   Authors: {authors_str}\n"

                    metadata = []
                    if paper.year:
                        metadata.append(str(paper.year))
                    if paper.venue:
                        metadata.append(paper.venue)
                    if metadata:
                        response += f"   {' | '.join(metadata)}\n"

                    if paper.citation_count > 0:
                        response += f"   Citations: {paper.citation_count}\n"

                    if paper.url:
                        response += f"   URL: {paper.url}\n"

                    if paper.pdf_url:
                        response += f"   PDF: {paper.pdf_url}\n"

                    if paper.abstract:
                        abstract_short = (
                            paper.abstract[:ABSTRACT_TRUNCATE_LENGTH] + "..."
                            if len(paper.abstract) > ABSTRACT_TRUNCATE_LENGTH
                            else paper.abstract
                        )
                        response += f"   Abstract: {abstract_short}\n"

                    response += "\n"

                return response

            return "Please specify what to search for. Example: 'search papers for machine learning'"

        return None

    @track_agent_performance('Beta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Perform research and analysis tasks.

        Args:
            input_data: User input text (research query)
            context: Optional context dictionary

        Returns:
            Research findings and analysis
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            search_response = self._handle_search_command(validated_input)
            if search_response:
                self.save_conversation('assistant', search_response)
                return self.adapt_to_user(search_response)

            model = COMPLEX_MODEL
            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            messages = [{"role": "system", "content": self.system_prompt(context)}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Beta conducting research with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Beta input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Beta circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Beta Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Beta act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)
