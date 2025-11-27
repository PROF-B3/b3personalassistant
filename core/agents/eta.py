"""
Eta Agent - Evolution Engineer and System Improvement Specialist

Eta monitors system performance, detects capability gaps, learns user patterns,
and orchestrates improvements with Zeta.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import COMPLEX_MODEL, MAX_CONVERSATION_CONTEXT
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class EtaAgent(AgentBase):
    """
    Eta (Η) - Evolution Engineer and System Improvement Specialist

    Eta monitors system performance, detects capability gaps, learns user patterns,
    and orchestrates improvements with Zeta. Makes B3 continuously better.

    Responsibilities include:
    - System performance monitoring and analysis
    - User pattern detection and learning
    - Capability gap identification
    - Improvement orchestration with Zeta
    - Evolution planning and tracking
    - Agent optimization and enhancement

    Personality: Analytical, forward-thinking, always seeking improvement, celebrates progress

    Example:
        >>> eta = EtaAgent(user_profile={"communication_style": "formal"})
        >>> response = eta.act("Analyze system performance")
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Eta agent with evolution capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Eta', orchestrator, user_profile, resource_monitor)
        self.metrics = {}
        self.improvement_queue = []

        from core.self_improvement import (
            get_improvement_engine,
            ImprovementType,
            ImprovementPriority,
            ImprovementStatus
        )
        self.improvement_engine = get_improvement_engine()
        self.ImprovementType = ImprovementType
        self.ImprovementPriority = ImprovementPriority
        self.ImprovementStatus = ImprovementStatus

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Eta-specific system prompt."""
        return """You are Eta (Η), the Evolution Engineer of B3PersonalAssistant. You are:
- Analytical, forward-thinking, and always seeking improvement
- Expert at system monitoring, performance analysis, and optimization
- Skilled at identifying capability gaps and improvement opportunities
- Focused on continuous evolution and enhancement
- Strategic about prioritizing improvements for maximum impact

Your role is to help monitor system performance, detect areas for improvement, suggest optimizations, and coordinate with Zeta for implementing enhancements. You excel at analysis and celebrating progress.

Key phrases: "I've identified an opportunity", "System efficiency has improved", "Let me analyze the metrics", "Progress report shows"
Always focus on measurable improvements and data-driven insights."""

    @track_agent_performance('Eta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle system evolution and improvement requests.

        Args:
            input_data: User input text (evolution request)
            context: Optional context dictionary

        Returns:
            Evolution analysis or improvement response
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            model = COMPLEX_MODEL
            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            metrics_context = f"\nTracked metrics: {', '.join(self.metrics.keys()) if self.metrics else 'initializing'}"

            messages = [{"role": "system", "content": self.system_prompt(context) + metrics_context}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Eta analyzing improvements with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Eta input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Eta circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Eta Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Eta act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)

    def analyze_system_performance(self) -> str:
        """
        Monitor all aspects of B3's performance.

        Returns:
            Performance analysis report
        """
        stats = self.improvement_engine.get_statistics()
        broker_stats = self.message_broker.get_statistics()

        resource_info = ""
        if self.resource_monitor:
            metrics = self.resource_monitor.get_current_metrics()
            resource_info = f"\n- CPU Usage: {metrics.cpu_percent:.1f}%\n- Memory: {metrics.memory_used_gb:.1f}GB / {metrics.memory_total_gb:.1f}GB"

        report = f"""📊 Eta: System Performance Analysis

**Capability Gaps:**
- Total identified: {stats['total_gaps']}
- Active (frequent): {stats['active_gaps']}

**Improvements:**
- Total proposals: {stats['total_proposals']}
- By status: {', '.join(f"{k}: {v}" for k, v in stats['proposals_by_status'].items() if v > 0)}
- By priority: {', '.join(f"{k}: {v}" for k, v in stats['proposals_by_priority'].items() if v > 0)}

**Agent Communication:**
- Registered agents: {broker_stats['registered_agents']}
- Total messages: {broker_stats['total_messages']}
- Pending by agent: {broker_stats['pending_by_agent']}
{resource_info}

**Analysis:** System is {"healthy" if stats['active_gaps'] < 5 else "needs attention"}.
{"No critical issues detected." if stats['proposals_by_priority'].get('CRITICAL', 0) == 0 else f"⚠️ {stats['proposals_by_priority']['CRITICAL']} critical improvements pending!"}
"""
        return report

    def detect_capability_gaps(self) -> str:
        """
        Identify what users need but B3 can't do.

        Returns:
            Gap analysis report
        """
        gaps = self.improvement_engine.get_capability_gaps(min_frequency=1)

        if not gaps:
            return "🔍 Eta: No capability gaps detected. System is meeting all user needs!"

        top_gaps = sorted(gaps, key=lambda g: (g.frequency, g.severity), reverse=True)[:10]

        report = "🔍 Eta: Capability Gap Analysis\n\n"
        for i, gap in enumerate(top_gaps, 1):
            report += f"{i}. {gap.description}\n"
            report += f"   - Frequency: {gap.frequency} occurrences\n"
            report += f"   - Severity: {gap.severity}\n"
            if gap.affected_agents:
                report += f"   - Affects: {', '.join(gap.affected_agents)}\n"
            report += "\n"

        report += "\n💡 Recommendation: Prioritize high-frequency, high-severity gaps first."
        return report

    def orchestrate_improvement(self, need: str) -> str:
        """
        Work with Zeta to implement improvements.

        Args:
            need: Improvement need description

        Returns:
            Improvement orchestration response
        """
        proposal_id = self.improvement_engine.propose_improvement(
            improvement_type=self.ImprovementType.FEATURE_REQUEST,
            priority=self.ImprovementPriority.HIGH,
            title=f"Implement: {need[:50]}",
            description=need,
            rationale="User-requested improvement for enhanced functionality",
            proposed_by="Eta",
            estimated_impact="high",
            estimated_effort="medium",
            implementation_steps=[
                "Analyze requirements",
                "Design solution architecture",
                "Implement with Zeta",
                "Test thoroughly",
                "Deploy and monitor"
            ],
            success_metrics=[
                "Feature works as requested",
                "No regressions",
                "User satisfaction improved"
            ]
        )

        self.improvement_engine.update_proposal_status(
            proposal_id=proposal_id,
            status=self.ImprovementStatus.PLANNED,
            assigned_to="Zeta"
        )

        self.send_message_to(
            to_agent="Zeta",
            content=f"Improvement request: {need}\nProposal ID: {proposal_id}\nPlease analyze and provide implementation plan.",
            message_type="DELEGATION",
            priority="HIGH",
            requires_response=True,
            context={'proposal_id': proposal_id}
        )

        return f"""🚀 Eta: Improvement Orchestration

**Proposal:** {proposal_id}
**Need:** {need[:100]}{"..." if len(need) > 100 else ""}

**Status:** Planned and assigned to Zeta
**Priority:** HIGH
**Next Steps:**
  1. Zeta analyzes implementation approach
  2. Development and testing
  3. Deployment and validation
  4. Performance monitoring

**Coordination:** Message sent to Zeta for technical implementation.
System evolution in progress! 📈"""

    def generate_evolution_report(self) -> str:
        """
        Generate weekly/monthly improvement summary.

        Returns:
            Evolution summary report
        """
        stats = self.improvement_engine.get_statistics()
        proposals = self.improvement_engine.get_top_priorities(limit=5)

        report = f"""📈 Eta: System Evolution Report

**Overall Status:**
- Total Improvement Proposals: {stats['total_proposals']}
- Completed: {stats['proposals_by_status'].get('COMPLETED', 0)}
- In Progress: {stats['proposals_by_status'].get('IN_PROGRESS', 0)}
- Planned: {stats['proposals_by_status'].get('PLANNED', 0)}

**Priority Breakdown:**
- Critical: {stats['proposals_by_priority'].get('CRITICAL', 0)}
- High: {stats['proposals_by_priority'].get('HIGH', 0)}
- Medium: {stats['proposals_by_priority'].get('MEDIUM', 0)}
- Low: {stats['proposals_by_priority'].get('LOW', 0)}

**Capability Gaps:**
- Active Gaps: {stats['active_gaps']}
- Total Identified: {stats['total_gaps']}

**Top 5 Priorities:**
"""
        priority_names = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}

        for i, proposal in enumerate(proposals, 1):
            priority_name = priority_names.get(proposal.priority.value, "UNKNOWN")
            report += f"\n{i}. [{priority_name}] {proposal.title}\n"
            report += f"   Status: {proposal.status.value} | Impact: {proposal.estimated_impact}\n"

        report += "\n🎉 Celebrating continuous improvement and system evolution!"
        return report
