#!/usr/bin/env python3
"""
Test script for self-improvement features.
Tests capability gap detection, improvement proposals, and evolution tracking.
"""

import sys
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.self_improvement import (
    get_improvement_engine,
    reset_improvement_engine,
    ImprovementType,
    ImprovementPriority,
    ImprovementStatus,
    SelfImprovementEngine
)
from core.agents import EtaAgent
from core.agent_communication import reset_message_broker

# Test storage path
TEST_STORAGE_PATH = Path("databases/test_improvements")


def cleanup_test_data():
    """Clean up test data directory."""
    if TEST_STORAGE_PATH.exists():
        shutil.rmtree(TEST_STORAGE_PATH)


def get_test_engine():
    """Get a test improvement engine with clean state."""
    cleanup_test_data()
    return SelfImprovementEngine(storage_path=TEST_STORAGE_PATH)


def test_engine_initialization():
    """Test improvement engine initialization."""
    print("Testing improvement engine initialization...")

    engine = get_test_engine()

    assert engine is not None, "Engine should exist"
    assert len(engine.capability_gaps) == 0, "Should start with no gaps"
    assert len(engine.improvement_proposals) == 0, "Should start with no proposals"

    print("  ✓ Improvement engine initializes correctly")
    return True


def test_capability_gap_detection():
    """Test capability gap detection and tracking."""
    print("Testing capability gap detection...")

    engine = get_test_engine()

    # Detect a new gap
    gap_id = engine.detect_capability_gap(
        description="Unable to process video files",
        example="User asked to analyze mp4 file but feature not implemented",
        severity="high",
        affected_agents=["Beta", "Gamma"]
    )

    assert gap_id is not None, "Should return gap ID"
    assert len(engine.capability_gaps) == 1, "Should have 1 gap"

    gap = engine.capability_gaps[gap_id]
    assert gap.description == "Unable to process video files", "Description should match"
    assert gap.frequency == 1, "Initial frequency should be 1"
    assert gap.severity == "high", "Severity should match"
    assert "Beta" in gap.affected_agents, "Beta should be affected"

    # Detect same gap again (should increment frequency)
    gap_id2 = engine.detect_capability_gap(
        description="Unable to process video files",
        example="Another request to process video",
        severity="high",
        affected_agents=["Beta"]
    )

    assert gap_id2 == gap_id, "Should return same gap ID"
    assert gap.frequency == 2, "Frequency should increment to 2"
    assert len(gap.examples) == 2, "Should have 2 examples"

    print("  ✓ Capability gap detection works correctly")
    return True


def test_improvement_proposal_creation():
    """Test improvement proposal creation."""
    print("Testing improvement proposal creation...")

    engine = get_test_engine()

    # Create a proposal
    proposal_id = engine.propose_improvement(
        improvement_type=ImprovementType.FEATURE_REQUEST,
        priority=ImprovementPriority.HIGH,
        title="Add video processing capability",
        description="Implement video file analysis using MoviePy",
        rationale="Multiple user requests for video processing",
        proposed_by="Eta",
        estimated_impact="high",
        estimated_effort="medium",
        implementation_steps=[
            "Install MoviePy dependencies",
            "Create video processing module",
            "Integrate with Beta agent",
            "Test with sample videos"
        ],
        success_metrics=[
            "Can process common video formats (mp4, avi, mov)",
            "Extract metadata and thumbnails",
            "No performance degradation"
        ]
    )

    assert proposal_id is not None, "Should return proposal ID"
    assert len(engine.improvement_proposals) == 1, "Should have 1 proposal"

    proposal = engine.improvement_proposals[proposal_id]
    assert proposal.title == "Add video processing capability", "Title should match"
    assert proposal.status == ImprovementStatus.IDENTIFIED, "Initial status should be IDENTIFIED"
    assert proposal.priority == ImprovementPriority.HIGH, "Priority should be HIGH"
    assert len(proposal.implementation_steps) == 4, "Should have 4 steps"

    print("  ✓ Improvement proposal creation works correctly")
    return True


def test_proposal_status_updates():
    """Test proposal status updates."""
    print("Testing proposal status updates...")

    engine = get_test_engine()

    # Create proposal
    proposal_id = engine.propose_improvement(
        improvement_type=ImprovementType.ERROR_PATTERN,
        priority=ImprovementPriority.CRITICAL,
        title="Fix memory leak in conversation history",
        description="Conversation history grows unbounded",
        rationale="System crashes after long sessions",
        proposed_by="Eta"
    )

    proposal = engine.improvement_proposals[proposal_id]
    assert proposal.status == ImprovementStatus.IDENTIFIED, "Should start as IDENTIFIED"

    # Update to PLANNED
    engine.update_proposal_status(proposal_id, ImprovementStatus.PLANNED, assigned_to="Zeta")
    assert proposal.status == ImprovementStatus.PLANNED, "Should be PLANNED"
    assert proposal.assigned_to == "Zeta", "Should be assigned to Zeta"

    # Update to IN_PROGRESS
    engine.update_proposal_status(
        proposal_id,
        ImprovementStatus.IN_PROGRESS
    )
    assert proposal.status == ImprovementStatus.IN_PROGRESS, "Should be IN_PROGRESS"

    # Update to COMPLETED
    engine.update_proposal_status(
        proposal_id,
        ImprovementStatus.COMPLETED
    )
    assert proposal.status == ImprovementStatus.COMPLETED, "Should be COMPLETED"
    assert proposal.completed_at is not None, "Should have completion time"

    print("  ✓ Proposal status updates work correctly")
    return True


def test_get_capability_gaps():
    """Test getting capability gaps with filtering."""
    print("Testing get_capability_gaps...")

    engine = get_test_engine()

    # Create multiple gaps
    engine.detect_capability_gap("Gap 1", "Example 1", "low", ["Alpha"])
    engine.detect_capability_gap("Gap 2", "Example 2", "high", ["Beta"])

    # Increment frequency of Gap 1
    for _ in range(5):
        engine.detect_capability_gap("Gap 1", "Another example", "low", ["Alpha"])

    # Get all gaps
    all_gaps = engine.get_capability_gaps()
    assert len(all_gaps) == 2, "Should have 2 gaps"

    # Get frequent gaps (frequency >= 3)
    frequent_gaps = engine.get_capability_gaps(min_frequency=3)
    assert len(frequent_gaps) == 1, "Should have 1 frequent gap"
    assert frequent_gaps[0].description == "Gap 1", "Should be Gap 1"
    assert frequent_gaps[0].frequency == 6, "Should have frequency 6"

    # Verify gaps have correct properties
    for gap in all_gaps:
        assert gap.severity in ["low", "high"], "Gap should have valid severity"

    print("  ✓ get_capability_gaps filtering works correctly")
    return True


def test_get_top_priorities():
    """Test getting top priority proposals."""
    print("Testing get_top_priorities...")

    engine = get_test_engine()

    # Create proposals with different priorities
    engine.propose_improvement(
        ImprovementType.FEATURE_REQUEST,
        ImprovementPriority.LOW,
        "Low priority feature",
        "Description",
        "Rationale",
        "Eta"
    )

    engine.propose_improvement(
        ImprovementType.ERROR_PATTERN,
        ImprovementPriority.CRITICAL,
        "Critical bug fix",
        "Description",
        "Rationale",
        "Eta"
    )

    engine.propose_improvement(
        ImprovementType.PERFORMANCE,
        ImprovementPriority.HIGH,
        "High priority optimization",
        "Description",
        "Rationale",
        "Eta"
    )

    # Get top 2 priorities
    top_priorities = engine.get_top_priorities(limit=2)
    assert len(top_priorities) == 2, "Should return 2 proposals"

    # Should be sorted by priority (CRITICAL > HIGH > MEDIUM > LOW)
    assert top_priorities[0].priority == ImprovementPriority.CRITICAL, "First should be CRITICAL"
    assert top_priorities[1].priority == ImprovementPriority.HIGH, "Second should be HIGH"

    print("  ✓ get_top_priorities works correctly")
    return True


def test_statistics():
    """Test statistics generation."""
    print("Testing statistics...")

    engine = get_test_engine()

    # Create some gaps and proposals
    engine.detect_capability_gap("Gap 1", "Example", "high", ["Alpha"])
    engine.detect_capability_gap("Gap 1", "Example", "high", ["Alpha"])  # Increment to 2
    engine.detect_capability_gap("Gap 1", "Example", "high", ["Alpha"])  # Increment to 3 (active)
    engine.detect_capability_gap("Gap 2", "Example", "low", ["Beta"])

    prop1 = engine.propose_improvement(
        ImprovementType.FEATURE_REQUEST,
        ImprovementPriority.HIGH,
        "Feature 1",
        "Desc",
        "Rationale",
        "Eta"
    )

    prop2 = engine.propose_improvement(
        ImprovementType.ERROR_PATTERN,
        ImprovementPriority.CRITICAL,
        "Bug 1",
        "Desc",
        "Rationale",
        "Eta"
    )

    engine.update_proposal_status(prop1, ImprovementStatus.IN_PROGRESS)
    engine.update_proposal_status(prop2, ImprovementStatus.COMPLETED)

    # Get statistics
    stats = engine.get_statistics()

    assert stats['total_gaps'] == 2, "Should have 2 gaps"
    assert stats['active_gaps'] == 1, "Should have 1 active gap (frequency >= 3)"
    assert stats['total_proposals'] == 2, "Should have 2 proposals"
    assert stats['proposals_by_status']['in_progress'] == 1, "Should have 1 in progress"
    assert stats['proposals_by_status']['completed'] == 1, "Should have 1 completed"
    assert stats['proposals_by_priority'][2] == 1, "Should have 1 HIGH priority (value=2)"
    assert stats['proposals_by_priority'][3] == 1, "Should have 1 CRITICAL priority (value=3)"

    print("  ✓ Statistics generation works correctly")
    return True


def test_eta_integration():
    """Test Eta agent integration with improvement engine."""
    print("Testing Eta agent integration...")

    reset_improvement_engine()
    reset_message_broker()

    eta = EtaAgent()

    # Test analyze_system_performance
    report = eta.analyze_system_performance()
    assert "System Performance Analysis" in report, "Should contain analysis header"
    assert "Capability Gaps" in report, "Should contain gap info"
    assert "Improvements" in report, "Should contain improvement info"

    print("  ✓ analyze_system_performance works")

    # Test detect_capability_gaps
    engine = get_improvement_engine()

    # Add some gaps first
    engine.detect_capability_gap("Test gap 1", "Example", "high", ["Alpha"])
    engine.detect_capability_gap("Test gap 2", "Example", "medium", ["Beta"])

    gaps_report = eta.detect_capability_gaps()
    assert "Capability Gap Analysis" in gaps_report, "Should contain header"

    print("  ✓ detect_capability_gaps works")

    # Test orchestrate_improvement
    improvement_report = eta.orchestrate_improvement("Add support for PDF processing")
    assert "Improvement Orchestration" in improvement_report, "Should contain header"
    assert "Proposal" in improvement_report, "Should contain proposal info"
    assert "Zeta" in improvement_report, "Should mention Zeta"

    print("  ✓ orchestrate_improvement works")

    # Test generate_evolution_report
    evolution_report = eta.generate_evolution_report()
    assert "System Evolution Report" in evolution_report, "Should contain header"
    assert "Overall Status" in evolution_report, "Should contain status"

    print("  ✓ generate_evolution_report works")

    print("  ✓ Eta agent integration works correctly")
    return True


def test_auto_proposal_from_gap():
    """Test automatic proposal creation from critical/frequent gaps."""
    print("Testing auto-proposal from critical gaps...")

    engine = get_test_engine()

    # Create a critical gap (should auto-create proposal)
    gap_id = engine.detect_capability_gap(
        description="System crashes on large files",
        example="User uploaded 2GB file, system crashed",
        severity="critical",
        affected_agents=["Beta", "Gamma"]
    )

    # Should auto-create proposal for critical gap
    proposals = list(engine.improvement_proposals.values())
    assert len(proposals) >= 1, "Should auto-create proposal for critical gap"

    # Find the auto-created proposal
    auto_proposal = None
    for p in proposals:
        if "large files" in p.description.lower() or "critical" in p.description.lower():
            auto_proposal = p
            break

    assert auto_proposal is not None, "Should have auto-created proposal"
    assert auto_proposal.priority == ImprovementPriority.CRITICAL, "Should be CRITICAL priority"

    print("  ✓ Auto-proposal from critical gaps works correctly")
    return True


def test_persistence():
    """Test data persistence to disk."""
    print("Testing data persistence...")

    engine = get_test_engine()

    # Create some data
    gap_id = engine.detect_capability_gap("Test gap", "Example", "high", ["Alpha"])
    proposal_id = engine.propose_improvement(
        ImprovementType.FEATURE_REQUEST,
        ImprovementPriority.HIGH,
        "Test feature",
        "Description",
        "Rationale",
        "Eta"
    )

    # Data should be saved to disk
    gaps_file = TEST_STORAGE_PATH / 'capability_gaps.json'
    proposals_file = TEST_STORAGE_PATH / 'improvement_proposals.json'

    assert gaps_file.exists(), "Gaps file should exist"
    assert proposals_file.exists(), "Proposals file should exist"

    # Load data to verify
    import json
    with open(gaps_file, 'r') as f:
        gaps_data = json.load(f)

    with open(proposals_file, 'r') as f:
        proposals_data = json.load(f)

    assert len(gaps_data) >= 1, "Should have at least 1 saved gap"
    assert len(proposals_data) >= 1, "Should have at least 1 saved proposal"

    print("  ✓ Data persistence works correctly")
    return True


def test_eta_zeta_workflow():
    """Test complete Eta-Zeta improvement workflow."""
    print("Testing Eta-Zeta improvement workflow...")

    reset_improvement_engine()
    reset_message_broker()

    from core.agents import ZetaAgent

    eta = EtaAgent()
    zeta = ZetaAgent()

    # Simulate Eta detecting a need and orchestrating improvement
    improvement_report = eta.orchestrate_improvement(
        "Implement automatic code refactoring suggestions"
    )

    assert "Proposal" in improvement_report, "Should create proposal"
    assert "Zeta" in improvement_report, "Should delegate to Zeta"

    # Zeta should have received a message
    zeta_messages = zeta.check_messages()
    assert len(zeta_messages) > 0, "Zeta should have messages from Eta"

    eta_message = zeta_messages[0]
    assert eta_message.from_agent == "Eta", "Message should be from Eta"
    assert "proposal_id" in eta_message.context, "Should have proposal ID in context"
    assert eta_message.message_type.value == "delegation", "Should be delegation message"

    # Get the proposal ID from message
    proposal_id = eta_message.context['proposal_id']

    # Verify proposal exists in engine
    engine = get_improvement_engine()
    proposal = engine.improvement_proposals.get(proposal_id)
    assert proposal is not None, "Proposal should exist"
    assert proposal.status == ImprovementStatus.PLANNED, "Should be PLANNED"
    assert proposal.assigned_to == "Zeta", "Should be assigned to Zeta"

    # Simulate Zeta responding
    zeta.send_message_to(
        to_agent="Eta",
        content=f"Acknowledged. Starting work on {proposal_id}",
        message_type="RESPONSE",
        context={'proposal_id': proposal_id, 'status': 'acknowledged'}
    )

    # Eta should receive response
    eta_messages = eta.check_messages()
    assert len(eta_messages) > 0, "Eta should have response from Zeta"

    print("  ✓ Eta-Zeta improvement workflow works correctly")
    return True


def main():
    """Run all self-improvement tests."""
    print("=" * 60)
    print("B3PersonalAssistant Self-Improvement Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_engine_initialization,
        test_capability_gap_detection,
        test_improvement_proposal_creation,
        test_proposal_status_updates,
        test_get_capability_gaps,
        test_get_top_priorities,
        test_statistics,
        test_eta_integration,
        test_auto_proposal_from_gap,
        test_persistence,
        test_eta_zeta_workflow,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()

    if failed == 0:
        print("✓ ALL SELF-IMPROVEMENT TESTS PASSED!")
        print()
        print("Self-improvement features verified:")
        print("  ✓ Capability gap detection and tracking")
        print("  ✓ Improvement proposal creation and management")
        print("  ✓ Proposal status lifecycle (IDENTIFIED → PLANNED → IN_PROGRESS → COMPLETED)")
        print("  ✓ Priority-based proposal ranking")
        print("  ✓ Statistics and analytics")
        print("  ✓ Eta agent integration")
        print("  ✓ Auto-proposal from critical gaps")
        print("  ✓ Data persistence to disk")
        print("  ✓ Complete Eta-Zeta improvement workflow")

        # Clean up test data
        cleanup_test_data()
        return 0
    else:
        print(f"✗ {failed} test(s) failed")

        # Clean up test data
        cleanup_test_data()
        return 1


if __name__ == '__main__':
    sys.exit(main())
