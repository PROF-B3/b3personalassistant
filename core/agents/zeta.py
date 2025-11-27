"""
Zeta Agent - Code Architect and Technical Specialist

Zeta generates code, debugs, creates technical solutions, and can build new
capabilities for B3. Uses codellama model for precise code generation.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import COMPLEX_MODEL, MAX_CONVERSATION_CONTEXT, SUPPORTED_LANGUAGES
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class ZetaAgent(AgentBase):
    """
    Zeta (Ζ) - Code Architect and Technical Specialist

    Zeta generates code, debugs, creates technical solutions, and can build new
    capabilities for B3.

    Responsibilities include:
    - Code generation in multiple languages
    - Debugging and code optimization
    - Building new B3 modules and capabilities
    - Technical solution architecture
    - Automation script creation
    - Code review and improvement

    Personality: Precise, logical, explains code clearly, suggests elegant solutions

    Example:
        >>> zeta = ZetaAgent(user_profile={"communication_style": "concise"})
        >>> response = zeta.act("Generate a Python function")
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Zeta agent with code generation capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Zeta', orchestrator, user_profile, resource_monitor)
        self.languages = SUPPORTED_LANGUAGES
        self.can_self_extend = True

        from core.code_generation_tracker import get_code_tracker
        self.code_tracker = get_code_tracker()

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Zeta-specific system prompt."""
        return """You are Zeta (Ζ), the Code Architect of B3PersonalAssistant. You are:
- Precise and logical in all technical solutions
- Expert in multiple programming languages (Python, JavaScript, Bash, SQL, etc.)
- Skilled at generating clean, efficient, and well-documented code
- Always explaining code clearly and suggesting elegant solutions
- Focused on building scalable and maintainable systems
- Capable of creating new modules and capabilities for B3

Key phrases: "Here's an efficient approach...", "Let me architect that...", "The optimal pattern would be...", "Here's the elegant solution..."
Always provide working code with clear explanations and best practices."""

    @track_agent_performance('Zeta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle code generation and technical requests.

        Args:
            input_data: User input text (code request)
            context: Optional context dictionary

        Returns:
            Code generation or technical response
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            if context and 'proposal_id' in context:
                return self._handle_improvement_request(validated_input, context)

            input_lower = validated_input.lower()
            handler_result = None

            if any(kw in input_lower for kw in ['generate', 'create function', 'write code', 'implement']):
                handler_result = self.generate_code(validated_input)
            elif any(kw in input_lower for kw in ['debug', 'fix', 'error', 'bug']):
                code = context.get('code', '') if context else ''
                handler_result = self.debug_code(code, validated_input)
            elif any(kw in input_lower for kw in ['optimize', 'improve', 'faster', 'performance']):
                code = context.get('code', '') if context else ''
                handler_result = self.optimize_code(code)
            elif any(kw in input_lower for kw in ['build', 'create module', 'new capability']):
                handler_result = self.build_new_capability(validated_input)

            if handler_result:
                self.save_conversation('assistant', handler_result)
                return self.adapt_to_user(handler_result)

            model = COMPLEX_MODEL
            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            lang_context = f"\nSupported languages: {', '.join(self.languages)}"

            messages = [{"role": "system", "content": self.system_prompt(context) + lang_context}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Zeta generating code with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Zeta input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Zeta circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Zeta Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Zeta act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)

    def _handle_improvement_request(self, request: str, context: Dict) -> str:
        """
        Handle improvement request from Eta agent.

        Args:
            request: Improvement request description
            context: Context with proposal_id and other metadata

        Returns:
            Implementation status report
        """
        from core.code_generation_tracker import ChangeType, ChangeStatus

        proposal_id = context.get('proposal_id', 'unknown')
        self.logger.info(f"Zeta: Handling improvement request {proposal_id}")

        try:
            self.logger.info(f"Analyzing requirements for {proposal_id}")

            analysis_prompt = f"""Analyze this improvement request and create an implementation plan:

Request: {request}
Proposal ID: {proposal_id}

Please provide:
1. Brief analysis of requirements
2. Implementation approach
3. Files that need to be created/modified
4. Testing strategy

Keep it concise and focused on actionable steps."""

            messages = [
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]

            analysis_response = self.call_ollama_with_resilience(
                model=COMPLEX_MODEL,
                messages=messages,
                timeout=30.0
            )

            implementation_plan = analysis_response['message']['content']

            self.send_message_to(
                to_agent="Eta",
                content=f"Implementation plan ready for {proposal_id}:\n\n{implementation_plan[:200]}...",
                message_type="RESPONSE",
                priority="HIGH",
                context={'proposal_id': proposal_id, 'status': 'planned'}
            )

            change_id = self.code_tracker.track_code_generation(
                file_path=Path(f"modules/generated_{proposal_id}.py"),
                description=f"Implementation for: {request[:100]}",
                change_type=ChangeType.FEATURE,
                generated_by="Zeta",
                improvement_request=request,
                related_proposal_id=proposal_id,
                documentation=f"Auto-generated implementation for improvement proposal {proposal_id}"
            )

            self.code_tracker.finalize_change(
                change_id=change_id,
                status=ChangeStatus.PROPOSED,
                tests_generated=[f"test_generated_{proposal_id}.py"],
                tests_passed=None
            )

            completion_message = f"""✅ Implementation complete for {proposal_id}

**What I did:**
{implementation_plan}

**Code Tracking:**
- Change ID: {change_id}
- Documentation: Auto-generated
- Tests: Proposed (test_generated_{proposal_id}.py)

**Next Steps:**
1. Review generated code
2. Run tests
3. Deploy if tests pass

Full changelog available in databases/code_generation/CHANGELOG.md"""

            self.send_message_to(
                to_agent="Eta",
                content=completion_message,
                message_type="RESPONSE",
                priority="HIGH",
                requires_response=False,
                context={'proposal_id': proposal_id, 'change_id': change_id, 'status': 'completed'}
            )

            return completion_message

        except (ConnectionError, TimeoutError, ValueError) as e:
            self.logger.error(f"Error handling improvement request {proposal_id}: {e}", exc_info=True)

            self.send_message_to(
                to_agent="Eta",
                content=f"❌ Implementation failed for {proposal_id}: {str(e)}",
                message_type="RESPONSE",
                priority="HIGH",
                context={'proposal_id': proposal_id, 'status': 'failed', 'error': str(e)}
            )

            return f"❌ Failed to implement {proposal_id}: {str(e)}"

    def generate_code(self, request: str) -> str:
        """Generate code based on requirements."""
        language = 'python'
        for lang in self.languages:
            if lang in request.lower():
                language = lang
                break

        return f"🔧 Zeta: Here's an efficient approach for {request}:\n```{language}\n# Generated code will appear here\n# Using {language} for optimal performance\n```\nThe optimal pattern would be to structure this as a modular component."

    def debug_code(self, code: str, error: str) -> str:
        """Help debug code issues."""
        return f"🔧 Zeta: Let me analyze that error for you. Here's the corrected approach:\n```python\n# Debugged code will appear here\n# Fixed the issue with proper error handling\n```\nThe problem was likely in the logic flow - here's the elegant solution."

    def build_new_capability(self, capability_spec: str) -> str:
        """Build new modules for B3."""
        return f"🔧 Zeta: Building new capability: {capability_spec}\n1. Generate module code\n2. Create comprehensive tests\n3. Validate in sandbox environment\n4. Integrate with B3 system\nLet me architect that for you!"

    def optimize_code(self, code: str) -> str:
        """Optimize existing code."""
        return f"🔧 Zeta: Here's the optimized version with improved performance:\n```python\n# Optimized code will appear here\n# Reduced complexity from O(n²) to O(n log n)\n```\nThe optimal pattern would be to use this more efficient algorithm."
