"""
Code Generation Tracking and Changelog System for B3PersonalAssistant.

Tracks all code generation by Zeta, maintains changelogs, enables rollback,
and generates documentation for troubleshooting.
"""

import logging
import hashlib
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Type of code change."""
    CREATE = "create"          # New file/module created
    MODIFY = "modify"          # Existing file modified
    DELETE = "delete"          # File deleted
    REFACTOR = "refactor"      # Code refactored
    FIX = "fix"                # Bug fix
    FEATURE = "feature"        # New feature added
    OPTIMIZATION = "optimization"  # Performance improvement


class ChangeStatus(Enum):
    """Status of a code change."""
    PROPOSED = "proposed"      # Change proposed but not applied
    APPLIED = "applied"        # Change successfully applied
    TESTED = "tested"          # Change tested and verified
    ROLLED_BACK = "rolled_back"  # Change was rolled back
    FAILED = "failed"          # Change failed to apply


@dataclass
class FileSnapshot:
    """Snapshot of a file at a point in time."""
    file_path: str
    content: str
    checksum: str
    timestamp: float
    size_bytes: int

    @classmethod
    def from_file(cls, file_path: Path) -> 'FileSnapshot':
        """Create snapshot from a file."""
        content = file_path.read_text() if file_path.exists() else ""
        checksum = hashlib.sha256(content.encode()).hexdigest()
        size_bytes = len(content.encode())

        return cls(
            file_path=str(file_path),
            content=content,
            checksum=checksum,
            timestamp=datetime.now().timestamp(),
            size_bytes=size_bytes
        )


@dataclass
class CodeChange:
    """Represents a single code change."""
    change_id: str
    change_type: ChangeType
    file_path: str
    description: str
    generated_by: str  # "Zeta" or agent name
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    status: ChangeStatus = ChangeStatus.PROPOSED

    # Code tracking
    before_snapshot: Optional[FileSnapshot] = None
    after_snapshot: Optional[FileSnapshot] = None
    diff_summary: Optional[str] = None

    # Metadata
    related_proposal_id: Optional[str] = None
    improvement_request: Optional[str] = None
    tests_generated: List[str] = field(default_factory=list)
    documentation: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    # Testing results
    tests_passed: Optional[bool] = None
    test_output: Optional[str] = None

    # Rollback tracking
    rolled_back_at: Optional[float] = None
    rollback_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'change_id': self.change_id,
            'change_type': self.change_type.value,
            'file_path': self.file_path,
            'description': self.description,
            'generated_by': self.generated_by,
            'timestamp': self.timestamp,
            'status': self.status.value,
            'before_snapshot': {
                'file_path': self.before_snapshot.file_path,
                'checksum': self.before_snapshot.checksum,
                'timestamp': self.before_snapshot.timestamp,
                'size_bytes': self.before_snapshot.size_bytes
            } if self.before_snapshot else None,
            'after_snapshot': {
                'file_path': self.after_snapshot.file_path,
                'checksum': self.after_snapshot.checksum,
                'timestamp': self.after_snapshot.timestamp,
                'size_bytes': self.after_snapshot.size_bytes
            } if self.after_snapshot else None,
            'diff_summary': self.diff_summary,
            'related_proposal_id': self.related_proposal_id,
            'improvement_request': self.improvement_request,
            'tests_generated': self.tests_generated,
            'documentation': self.documentation,
            'dependencies': self.dependencies,
            'tests_passed': self.tests_passed,
            'test_output': self.test_output,
            'rolled_back_at': self.rolled_back_at,
            'rollback_reason': self.rollback_reason
        }


@dataclass
class ChangelogEntry:
    """Entry in the system changelog."""
    entry_id: str
    timestamp: float
    title: str
    description: str
    changes: List[str]  # List of change IDs
    generated_by: str
    version: str  # Semantic version or timestamp-based version
    related_proposal_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp,
            'title': self.title,
            'description': self.description,
            'changes': self.changes,
            'generated_by': self.generated_by,
            'version': self.version,
            'related_proposal_id': self.related_proposal_id
        }


class CodeGenerationTracker:
    """
    Tracks all code generation and modifications.

    Provides:
    - Complete change history
    - Rollback capability
    - Documentation generation
    - Troubleshooting support
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize code generation tracker.

        Args:
            storage_path: Path to store tracking data
        """
        self.logger = logging.getLogger("code_tracker")
        self.storage_path = storage_path or Path("databases/code_generation")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage directories
        self.snapshots_dir = self.storage_path / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

        # Data structures
        self.code_changes: Dict[str, CodeChange] = {}
        self.changelog_entries: Dict[str, ChangelogEntry] = {}
        self.change_counter = 0
        self.changelog_counter = 0

        # Load existing data
        self._load_data()

        self.logger.info("Code generation tracker initialized")

    def track_code_generation(
        self,
        file_path: Path,
        description: str,
        change_type: ChangeType = ChangeType.CREATE,
        generated_by: str = "Zeta",
        improvement_request: Optional[str] = None,
        related_proposal_id: Optional[str] = None,
        documentation: Optional[str] = None
    ) -> str:
        """
        Track a code generation event.

        Args:
            file_path: Path to the generated/modified file
            description: Description of the change
            change_type: Type of change
            generated_by: Agent that generated the code
            improvement_request: Original improvement request
            related_proposal_id: Related improvement proposal ID
            documentation: Auto-generated documentation

        Returns:
            Change ID
        """
        self.change_counter += 1
        change_id = f"change_{self.change_counter}_{int(datetime.now().timestamp())}"

        # Create before snapshot if file exists
        before_snapshot = None
        if file_path.exists():
            before_snapshot = FileSnapshot.from_file(file_path)
            # Save snapshot content
            self._save_snapshot(change_id, "before", before_snapshot)

        change = CodeChange(
            change_id=change_id,
            change_type=change_type,
            file_path=str(file_path),
            description=description,
            generated_by=generated_by,
            before_snapshot=before_snapshot,
            related_proposal_id=related_proposal_id,
            improvement_request=improvement_request,
            documentation=documentation
        )

        self.code_changes[change_id] = change

        self.logger.info(
            f"Tracking code generation: {change_id} - {change_type.value} - {file_path}"
        )

        self._save_data()
        return change_id

    def finalize_change(
        self,
        change_id: str,
        status: ChangeStatus = ChangeStatus.APPLIED,
        tests_generated: Optional[List[str]] = None,
        tests_passed: Optional[bool] = None,
        test_output: Optional[str] = None
    ):
        """
        Finalize a code change after generation/testing.

        Args:
            change_id: Change ID
            status: New status
            tests_generated: List of generated test files
            tests_passed: Whether tests passed
            test_output: Test execution output
        """
        if change_id not in self.code_changes:
            self.logger.warning(f"Change {change_id} not found")
            return

        change = self.code_changes[change_id]
        file_path = Path(change.file_path)

        # Create after snapshot
        if file_path.exists():
            after_snapshot = FileSnapshot.from_file(file_path)
            change.after_snapshot = after_snapshot
            self._save_snapshot(change_id, "after", after_snapshot)

            # Generate diff summary
            if change.before_snapshot:
                change.diff_summary = self._generate_diff_summary(
                    change.before_snapshot,
                    after_snapshot
                )

        change.status = status

        if tests_generated:
            change.tests_generated = tests_generated

        if tests_passed is not None:
            change.tests_passed = tests_passed
            change.test_output = test_output

            if tests_passed:
                change.status = ChangeStatus.TESTED

        self.logger.info(f"Finalized change {change_id}: {status.value}")
        self._save_data()

    def rollback_change(self, change_id: str, reason: str):
        """
        Rollback a code change to its previous state.

        Args:
            change_id: Change ID to rollback
            reason: Reason for rollback
        """
        if change_id not in self.code_changes:
            self.logger.error(f"Change {change_id} not found for rollback")
            return

        change = self.code_changes[change_id]

        if not change.before_snapshot:
            self.logger.error(f"No before snapshot for {change_id}, cannot rollback")
            return

        # Restore file from before snapshot
        file_path = Path(change.file_path)

        try:
            if change.before_snapshot.content:
                # Restore previous content
                file_path.write_text(change.before_snapshot.content)
                self.logger.info(f"Restored {file_path} to previous state")
            else:
                # File didn't exist before, delete it
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"Deleted {file_path} (didn't exist before)")

            # Update change record
            change.status = ChangeStatus.ROLLED_BACK
            change.rolled_back_at = datetime.now().timestamp()
            change.rollback_reason = reason

            self.logger.info(f"Rolled back change {change_id}: {reason}")
            self._save_data()

        except Exception as e:
            self.logger.error(f"Failed to rollback {change_id}: {e}")
            change.status = ChangeStatus.FAILED
            self._save_data()

    def create_changelog_entry(
        self,
        title: str,
        description: str,
        change_ids: List[str],
        generated_by: str = "Zeta",
        version: Optional[str] = None,
        related_proposal_id: Optional[str] = None
    ) -> str:
        """
        Create a changelog entry grouping related changes.

        Args:
            title: Entry title
            description: Detailed description
            change_ids: List of change IDs in this entry
            generated_by: Agent that generated changes
            version: Version identifier
            related_proposal_id: Related improvement proposal

        Returns:
            Entry ID
        """
        self.changelog_counter += 1
        entry_id = f"changelog_{self.changelog_counter}_{int(datetime.now().timestamp())}"

        # Auto-generate version if not provided
        if not version:
            version = f"v{datetime.now().strftime('%Y.%m.%d.%H%M')}"

        entry = ChangelogEntry(
            entry_id=entry_id,
            timestamp=datetime.now().timestamp(),
            title=title,
            description=description,
            changes=change_ids,
            generated_by=generated_by,
            version=version,
            related_proposal_id=related_proposal_id
        )

        self.changelog_entries[entry_id] = entry

        self.logger.info(f"Created changelog entry: {entry_id} - {title} ({version})")
        self._save_data()

        return entry_id

    def generate_changelog_markdown(self, limit: int = 50) -> str:
        """
        Generate changelog in Markdown format.

        Args:
            limit: Maximum number of entries to include

        Returns:
            Markdown changelog
        """
        # Sort entries by timestamp (newest first)
        sorted_entries = sorted(
            self.changelog_entries.values(),
            key=lambda e: e.timestamp,
            reverse=True
        )[:limit]

        markdown = "# B3PersonalAssistant Code Generation Changelog\n\n"
        markdown += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        markdown += "---\n\n"

        for entry in sorted_entries:
            # Entry header
            timestamp_str = datetime.fromtimestamp(entry.timestamp).strftime('%Y-%m-%d %H:%M')
            markdown += f"## {entry.version} - {entry.title}\n"
            markdown += f"**Date:** {timestamp_str} | **Generated by:** {entry.generated_by}\n\n"

            # Description
            markdown += f"{entry.description}\n\n"

            # Changes
            markdown += "**Changes:**\n"
            for change_id in entry.changes:
                if change_id in self.code_changes:
                    change = self.code_changes[change_id]
                    file_name = Path(change.file_path).name
                    status_icon = "✅" if change.status == ChangeStatus.TESTED else "🔧"
                    markdown += f"- {status_icon} `{file_name}` - {change.description}\n"

                    if change.tests_passed is not None:
                        test_status = "✅ Tests passed" if change.tests_passed else "❌ Tests failed"
                        markdown += f"  - {test_status}\n"

            markdown += "\n"

            # Related proposal
            if entry.related_proposal_id:
                markdown += f"*Related to improvement proposal: {entry.related_proposal_id}*\n\n"

            markdown += "---\n\n"

        return markdown

    def get_change_history(
        self,
        file_path: Optional[str] = None,
        limit: int = 20
    ) -> List[CodeChange]:
        """
        Get change history, optionally filtered by file.

        Args:
            file_path: Optional file path to filter by
            limit: Maximum number of changes to return

        Returns:
            List of code changes
        """
        changes = list(self.code_changes.values())

        if file_path:
            changes = [c for c in changes if c.file_path == file_path]

        # Sort by timestamp (newest first)
        changes = sorted(changes, key=lambda c: c.timestamp, reverse=True)

        return changes[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get code generation statistics."""
        return {
            'total_changes': len(self.code_changes),
            'changes_by_type': {
                change_type.value: len([
                    c for c in self.code_changes.values()
                    if c.change_type == change_type
                ])
                for change_type in ChangeType
            },
            'changes_by_status': {
                status.value: len([
                    c for c in self.code_changes.values()
                    if c.status == status
                ])
                for status in ChangeStatus
            },
            'total_changelog_entries': len(self.changelog_entries),
            'tests_passed_rate': self._calculate_test_pass_rate(),
            'rollback_count': len([
                c for c in self.code_changes.values()
                if c.status == ChangeStatus.ROLLED_BACK
            ])
        }

    def _calculate_test_pass_rate(self) -> float:
        """Calculate test pass rate."""
        tested_changes = [c for c in self.code_changes.values() if c.tests_passed is not None]
        if not tested_changes:
            return 0.0

        passed = len([c for c in tested_changes if c.tests_passed])
        return (passed / len(tested_changes)) * 100

    def _generate_diff_summary(
        self,
        before: FileSnapshot,
        after: FileSnapshot
    ) -> str:
        """Generate a summary of changes between two snapshots."""
        before_lines = before.content.splitlines()
        after_lines = after.content.splitlines()

        added = len(after_lines) - len(before_lines)

        summary = f"Lines: {len(before_lines)} → {len(after_lines)}"
        if added > 0:
            summary += f" (+{added})"
        elif added < 0:
            summary += f" ({added})"

        summary += f" | Size: {before.size_bytes} → {after.size_bytes} bytes"

        return summary

    def _save_snapshot(self, change_id: str, snapshot_type: str, snapshot: FileSnapshot):
        """Save snapshot content to disk."""
        snapshot_dir = self.snapshots_dir / change_id
        snapshot_dir.mkdir(exist_ok=True)

        snapshot_file = snapshot_dir / f"{snapshot_type}.txt"
        snapshot_file.write_text(snapshot.content)

        # Save snapshot metadata
        metadata_file = snapshot_dir / f"{snapshot_type}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump({
                'file_path': snapshot.file_path,
                'checksum': snapshot.checksum,
                'timestamp': snapshot.timestamp,
                'size_bytes': snapshot.size_bytes
            }, f, indent=2)

    def _save_data(self):
        """Save tracking data to disk."""
        try:
            # Save code changes
            changes_file = self.storage_path / "code_changes.json"
            with open(changes_file, 'w') as f:
                changes_data = {
                    change_id: change.to_dict()
                    for change_id, change in self.code_changes.items()
                }
                json.dump(changes_data, f, indent=2)

            # Save changelog entries
            changelog_file = self.storage_path / "changelog_entries.json"
            with open(changelog_file, 'w') as f:
                changelog_data = {
                    entry_id: entry.to_dict()
                    for entry_id, entry in self.changelog_entries.items()
                }
                json.dump(changelog_data, f, indent=2)

            # Generate and save markdown changelog
            markdown_file = self.storage_path / "CHANGELOG.md"
            markdown_file.write_text(self.generate_changelog_markdown())

        except Exception as e:
            self.logger.error(f"Failed to save tracking data: {e}")

    def _load_data(self):
        """Load tracking data from disk."""
        try:
            # Load code changes
            changes_file = self.storage_path / "code_changes.json"
            if changes_file.exists():
                with open(changes_file, 'r') as f:
                    changes_data = json.load(f)
                    for change_id, data in changes_data.items():
                        # Convert enums
                        data['change_type'] = ChangeType(data['change_type'])
                        data['status'] = ChangeStatus(data['status'])

                        # Convert snapshots
                        if data.get('before_snapshot'):
                            snap_data = data['before_snapshot']
                            data['before_snapshot'] = FileSnapshot(
                                file_path=snap_data['file_path'],
                                content="",  # Not stored in JSON
                                checksum=snap_data['checksum'],
                                timestamp=snap_data['timestamp'],
                                size_bytes=snap_data['size_bytes']
                            )

                        if data.get('after_snapshot'):
                            snap_data = data['after_snapshot']
                            data['after_snapshot'] = FileSnapshot(
                                file_path=snap_data['file_path'],
                                content="",  # Not stored in JSON
                                checksum=snap_data['checksum'],
                                timestamp=snap_data['timestamp'],
                                size_bytes=snap_data['size_bytes']
                            )

                        self.code_changes[change_id] = CodeChange(**data)

                self.logger.info(f"Loaded {len(self.code_changes)} code changes")

            # Load changelog entries
            changelog_file = self.storage_path / "changelog_entries.json"
            if changelog_file.exists():
                with open(changelog_file, 'r') as f:
                    changelog_data = json.load(f)
                    for entry_id, data in changelog_data.items():
                        self.changelog_entries[entry_id] = ChangelogEntry(**data)

                self.logger.info(f"Loaded {len(self.changelog_entries)} changelog entries")

        except Exception as e:
            self.logger.error(f"Failed to load tracking data: {e}")


# Global tracker instance
_global_tracker: Optional[CodeGenerationTracker] = None


def get_code_tracker() -> CodeGenerationTracker:
    """Get or create the global code generation tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CodeGenerationTracker()
    return _global_tracker


def reset_code_tracker():
    """Reset the global tracker (useful for testing)."""
    global _global_tracker
    _global_tracker = CodeGenerationTracker()
