"""
Self-Improvement System for B3PersonalAssistant.

Enables the system to analyze its own performance, detect capability gaps,
and coordinate improvements through Eta and Zeta agents.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ImprovementType(Enum):
    """Types of improvements."""
    CAPABILITY_GAP = "capability_gap"          # Missing functionality
    PERFORMANCE = "performance"                 # Performance optimization
    ERROR_PATTERN = "error_pattern"            # Recurring error fix
    USER_PATTERN = "user_pattern"              # User need pattern
    AGENT_COORDINATION = "agent_coordination"  # Better agent coordination
    CODE_QUALITY = "code_quality"              # Code improvement
    FEATURE_REQUEST = "feature_request"        # New feature


class ImprovementPriority(Enum):
    """Priority levels for improvements."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class ImprovementStatus(Enum):
    """Status of improvement implementations."""
    IDENTIFIED = "identified"
    ANALYZING = "analyzing"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CapabilityGap:
    """Represents a detected capability gap."""
    gap_id: str
    description: str
    frequency: int = 1  # How often this gap is encountered
    severity: str = "medium"  # low, medium, high, critical
    examples: List[str] = field(default_factory=list)
    first_detected: float = field(default_factory=time.time)
    last_detected: float = field(default_factory=time.time)
    suggested_solution: Optional[str] = None
    affected_agents: List[str] = field(default_factory=list)


@dataclass
class ImprovementProposal:
    """Proposed improvement to the system."""
    proposal_id: str
    improvement_type: ImprovementType
    priority: ImprovementPriority
    title: str
    description: str
    rationale: str
    proposed_by: str  # Agent that proposed it
    proposed_at: float = field(default_factory=time.time)
    status: ImprovementStatus = ImprovementStatus.IDENTIFIED
    estimated_impact: str = "medium"  # low, medium, high
    estimated_effort: str = "medium"  # low, medium, high
    affected_components: List[str] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'proposal_id': self.proposal_id,
            'improvement_type': self.improvement_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'rationale': self.rationale,
            'proposed_by': self.proposed_by,
            'proposed_at': self.proposed_at,
            'status': self.status.value,
            'estimated_impact': self.estimated_impact,
            'estimated_effort': self.estimated_effort,
            'affected_components': self.affected_components,
            'implementation_steps': self.implementation_steps,
            'success_metrics': self.success_metrics,
            'assigned_to': self.assigned_to,
            'completed_at': self.completed_at,
            'metadata': self.metadata
        }


class SelfImprovementEngine:
    """
    Engine for continuous self-improvement.

    Monitors system performance, detects patterns, identifies gaps,
    and coordinates improvements through agent collaboration.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize self-improvement engine.

        Args:
            storage_path: Path to store improvement data
        """
        self.logger = logging.getLogger("self_improvement")
        self.storage_path = storage_path or Path("databases/improvements")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage
        self.capability_gaps: Dict[str, CapabilityGap] = {}
        self.improvement_proposals: Dict[str, ImprovementProposal] = {}
        self.error_patterns: Dict[str, List[str]] = {}  # error_type -> [instances]
        self.user_patterns: Dict[str, int] = {}  # pattern -> frequency
        self.performance_metrics: Dict[str, List[float]] = {}  # metric -> values

        # Tracking
        self.improvement_counter = 0
        self.gap_counter = 0

        # Load existing data
        self._load_data()

        self.logger.info("Self-improvement engine initialized")

    def detect_capability_gap(
        self,
        description: str,
        example: str,
        severity: str = "medium",
        affected_agents: Optional[List[str]] = None
    ) -> str:
        """
        Detect and record a capability gap.

        Args:
            description: Description of the gap
            example: Example of the gap occurring
            severity: Severity level
            affected_agents: List of affected agents

        Returns:
            Gap ID
        """
        # Check if similar gap exists
        gap_id = self._find_similar_gap(description)

        if gap_id:
            # Update existing gap
            gap = self.capability_gaps[gap_id]
            gap.frequency += 1
            gap.last_detected = time.time()
            if example not in gap.examples:
                gap.examples.append(example)
            self.logger.info(f"Updated capability gap {gap_id} (frequency: {gap.frequency})")
        else:
            # Create new gap
            self.gap_counter += 1
            gap_id = f"gap_{self.gap_counter}_{int(time.time())}"
            gap = CapabilityGap(
                gap_id=gap_id,
                description=description,
                severity=severity,
                examples=[example],
                affected_agents=affected_agents or []
            )
            self.capability_gaps[gap_id] = gap
            self.logger.info(f"New capability gap detected: {gap_id} - {description}")

        # Auto-propose improvement for critical gaps
        if gap.severity == "critical" or gap.frequency >= 5:
            self._auto_propose_improvement(gap)

        self._save_data()
        return gap_id

    def record_error_pattern(self, error_type: str, error_message: str):
        """
        Record an error pattern for analysis.

        Args:
            error_type: Type of error
            error_message: Error message
        """
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []

        self.error_patterns[error_type].append(error_message)

        # Detect recurring errors
        if len(self.error_patterns[error_type]) >= 3:
            self.logger.warning(
                f"Recurring error pattern detected: {error_type} "
                f"({len(self.error_patterns[error_type])} occurrences)"
            )

            # Propose improvement
            self.propose_improvement(
                improvement_type=ImprovementType.ERROR_PATTERN,
                priority=ImprovementPriority.HIGH,
                title=f"Fix recurring error: {error_type}",
                description=f"Error '{error_type}' has occurred {len(self.error_patterns[error_type])} times",
                rationale="Recurring errors degrade user experience and system reliability",
                proposed_by="Eta",
                implementation_steps=[
                    f"Analyze root cause of {error_type}",
                    "Implement fix",
                    "Add test case to prevent regression"
                ]
            )

    def record_user_pattern(self, pattern: str):
        """
        Record a user interaction pattern.

        Args:
            pattern: Pattern description
        """
        self.user_patterns[pattern] = self.user_patterns.get(pattern, 0) + 1

        # Detect frequent patterns that could be optimized
        if self.user_patterns[pattern] >= 10:
            self.logger.info(f"Frequent user pattern: {pattern} ({self.user_patterns[pattern]} times)")

    def record_performance_metric(self, metric_name: str, value: float):
        """
        Record a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []

        self.performance_metrics[metric_name].append(value)

        # Keep only recent metrics
        if len(self.performance_metrics[metric_name]) > 100:
            self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-100:]

        # Detect performance degradation
        if len(self.performance_metrics[metric_name]) >= 10:
            recent = self.performance_metrics[metric_name][-10:]
            earlier = self.performance_metrics[metric_name][-20:-10] if len(self.performance_metrics[metric_name]) >= 20 else recent

            recent_avg = sum(recent) / len(recent)
            earlier_avg = sum(earlier) / len(earlier)

            # If performance degraded by more than 20%
            if recent_avg > earlier_avg * 1.2:
                self.logger.warning(
                    f"Performance degradation detected in {metric_name}: "
                    f"{earlier_avg:.2f} → {recent_avg:.2f}"
                )

    def propose_improvement(
        self,
        improvement_type: ImprovementType,
        priority: ImprovementPriority,
        title: str,
        description: str,
        rationale: str,
        proposed_by: str,
        estimated_impact: str = "medium",
        estimated_effort: str = "medium",
        affected_components: Optional[List[str]] = None,
        implementation_steps: Optional[List[str]] = None,
        success_metrics: Optional[List[str]] = None
    ) -> str:
        """
        Propose a new improvement.

        Args:
            improvement_type: Type of improvement
            priority: Priority level
            title: Short title
            description: Detailed description
            rationale: Why this improvement is needed
            proposed_by: Agent proposing the improvement
            estimated_impact: Estimated impact (low/medium/high)
            estimated_effort: Estimated effort (low/medium/high)
            affected_components: List of affected components
            implementation_steps: Steps to implement
            success_metrics: Metrics to measure success

        Returns:
            Proposal ID
        """
        self.improvement_counter += 1
        proposal_id = f"imp_{self.improvement_counter}_{int(time.time())}"

        proposal = ImprovementProposal(
            proposal_id=proposal_id,
            improvement_type=improvement_type,
            priority=priority,
            title=title,
            description=description,
            rationale=rationale,
            proposed_by=proposed_by,
            estimated_impact=estimated_impact,
            estimated_effort=estimated_effort,
            affected_components=affected_components or [],
            implementation_steps=implementation_steps or [],
            success_metrics=success_metrics or []
        )

        self.improvement_proposals[proposal_id] = proposal

        self.logger.info(
            f"New improvement proposal: {proposal_id} - {title} "
            f"[{priority.value}, {improvement_type.value}]"
        )

        self._save_data()
        return proposal_id

    def get_top_priorities(self, limit: int = 5) -> List[ImprovementProposal]:
        """
        Get top priority improvements.

        Args:
            limit: Maximum number to return

        Returns:
            List of top priority proposals
        """
        # Filter to non-completed proposals
        active_proposals = [
            p for p in self.improvement_proposals.values()
            if p.status not in [ImprovementStatus.COMPLETED, ImprovementStatus.CANCELLED]
        ]

        # Sort by priority (descending) and then by age
        sorted_proposals = sorted(
            active_proposals,
            key=lambda p: (p.priority.value, -p.proposed_at),
            reverse=True
        )

        return sorted_proposals[:limit]

    def get_capability_gaps(self, min_frequency: int = 1) -> List[CapabilityGap]:
        """
        Get detected capability gaps.

        Args:
            min_frequency: Minimum frequency to include

        Returns:
            List of capability gaps
        """
        gaps = [g for g in self.capability_gaps.values() if g.frequency >= min_frequency]
        return sorted(gaps, key=lambda g: g.frequency, reverse=True)

    def update_proposal_status(
        self,
        proposal_id: str,
        status: ImprovementStatus,
        assigned_to: Optional[str] = None
    ):
        """
        Update status of an improvement proposal.

        Args:
            proposal_id: Proposal ID
            status: New status
            assigned_to: Agent assigned to implement
        """
        if proposal_id not in self.improvement_proposals:
            self.logger.warning(f"Proposal {proposal_id} not found")
            return

        proposal = self.improvement_proposals[proposal_id]
        old_status = proposal.status
        proposal.status = status

        if assigned_to:
            proposal.assigned_to = assigned_to

        if status == ImprovementStatus.COMPLETED:
            proposal.completed_at = time.time()

        self.logger.info(
            f"Proposal {proposal_id} status: {old_status.value} → {status.value}"
        )

        self._save_data()

    def _find_similar_gap(self, description: str) -> Optional[str]:
        """Find similar existing gap."""
        # Simple similarity check (could be improved with NLP)
        desc_lower = description.lower()
        for gap_id, gap in self.capability_gaps.items():
            if gap.description.lower() in desc_lower or desc_lower in gap.description.lower():
                return gap_id
        return None

    def _auto_propose_improvement(self, gap: CapabilityGap):
        """Automatically propose improvement for a gap."""
        # Check if already proposed
        for proposal in self.improvement_proposals.values():
            if gap.gap_id in proposal.metadata.get('gap_ids', []):
                return  # Already proposed

        # Create proposal
        priority = ImprovementPriority.CRITICAL if gap.severity == "critical" else ImprovementPriority.HIGH

        proposal_id = self.propose_improvement(
            improvement_type=ImprovementType.CAPABILITY_GAP,
            priority=priority,
            title=f"Address capability gap: {gap.description[:50]}",
            description=f"Gap detected {gap.frequency} times. {gap.description}",
            rationale=f"This capability is frequently needed (frequency: {gap.frequency})",
            proposed_by="Eta",
            estimated_impact="high",
            affected_components=gap.affected_agents,
            implementation_steps=[
                "Analyze gap requirements",
                "Design solution",
                "Implement functionality",
                "Add tests",
                "Deploy and monitor"
            ],
            success_metrics=[
                "Gap frequency drops to zero",
                "User satisfaction improves",
                "No related errors"
            ]
        )

        # Link gap to proposal
        self.improvement_proposals[proposal_id].metadata['gap_ids'] = [gap.gap_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get self-improvement statistics."""
        return {
            'total_gaps': len(self.capability_gaps),
            'active_gaps': len([g for g in self.capability_gaps.values() if g.frequency >= 3]),
            'total_proposals': len(self.improvement_proposals),
            'proposals_by_status': {
                status.value: len([
                    p for p in self.improvement_proposals.values()
                    if p.status == status
                ])
                for status in ImprovementStatus
            },
            'proposals_by_priority': {
                priority.value: len([
                    p for p in self.improvement_proposals.values()
                    if p.priority == priority
                ])
                for priority in ImprovementPriority
            },
            'error_patterns': len(self.error_patterns),
            'user_patterns': len(self.user_patterns),
            'performance_metrics': len(self.performance_metrics)
        }

    def _save_data(self):
        """Save improvement data to disk."""
        try:
            # Save capability gaps
            gaps_file = self.storage_path / "capability_gaps.json"
            with open(gaps_file, 'w') as f:
                gaps_data = {
                    gap_id: {
                        'gap_id': gap.gap_id,
                        'description': gap.description,
                        'frequency': gap.frequency,
                        'severity': gap.severity,
                        'examples': gap.examples[:10],  # Limit examples
                        'first_detected': gap.first_detected,
                        'last_detected': gap.last_detected,
                        'suggested_solution': gap.suggested_solution,
                        'affected_agents': gap.affected_agents
                    }
                    for gap_id, gap in self.capability_gaps.items()
                }
                json.dump(gaps_data, f, indent=2)

            # Save proposals
            proposals_file = self.storage_path / "improvement_proposals.json"
            with open(proposals_file, 'w') as f:
                proposals_data = {
                    pid: p.to_dict()
                    for pid, p in self.improvement_proposals.items()
                }
                json.dump(proposals_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save improvement data: {e}")

    def _load_data(self):
        """Load improvement data from disk."""
        try:
            # Load capability gaps
            gaps_file = self.storage_path / "capability_gaps.json"
            if gaps_file.exists():
                with open(gaps_file, 'r') as f:
                    gaps_data = json.load(f)
                    for gap_id, data in gaps_data.items():
                        self.capability_gaps[gap_id] = CapabilityGap(**data)
                self.logger.info(f"Loaded {len(self.capability_gaps)} capability gaps")

            # Load proposals
            proposals_file = self.storage_path / "improvement_proposals.json"
            if proposals_file.exists():
                with open(proposals_file, 'r') as f:
                    proposals_data = json.load(f)
                    for pid, data in proposals_data.items():
                        # Convert enums
                        data['improvement_type'] = ImprovementType(data['improvement_type'])
                        data['priority'] = ImprovementPriority(data['priority'])
                        data['status'] = ImprovementStatus(data['status'])
                        self.improvement_proposals[pid] = ImprovementProposal(**data)
                self.logger.info(f"Loaded {len(self.improvement_proposals)} improvement proposals")

        except Exception as e:
            self.logger.error(f"Failed to load improvement data: {e}")


# Global self-improvement engine instance
_global_engine: Optional[SelfImprovementEngine] = None


def get_improvement_engine() -> SelfImprovementEngine:
    """Get or create the global self-improvement engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = SelfImprovementEngine()
    return _global_engine


def reset_improvement_engine():
    """Reset the global improvement engine (useful for testing)."""
    global _global_engine
    _global_engine = SelfImprovementEngine()
