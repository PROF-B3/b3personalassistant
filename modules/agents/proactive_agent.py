"""
Proactive Agent for B3PersonalAssistant

Learns from user behavior patterns and proactively suggests actions,
information, and optimizations before being asked.
"""

import logging
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
import re

from core.constants import DB_DIR
from core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """A learned behavior pattern."""
    pattern_type: str  # "time_based", "sequence", "context", "frequency"
    description: str
    confidence: float  # 0-1
    frequency: int
    last_seen: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Suggestion:
    """A proactive suggestion."""
    suggestion_type: str  # "task", "info", "optimization", "reminder"
    title: str
    description: str
    confidence: float
    priority: int  # 1-5
    action: Optional[str] = None  # Suggested action to take
    metadata: Optional[Dict[str, Any]] = None


class ProactiveAgent:
    """
    Learns user patterns and makes proactive suggestions.

    Features:
    - Time-based patterns (what you do at certain times)
    - Sequence patterns (action sequences)
    - Context patterns (what you do in certain contexts)
    - Frequency analysis (common tasks/topics)
    - Anomaly detection (unusual behavior)
    - Smart reminders based on context
    - Predictive task suggestions

    Example:
        >>> agent = ProactiveAgent()
        >>> agent.record_action("checked email", context="morning")
        >>> agent.record_action("reviewed tasks", context="morning")
        >>>
        >>> # Later...
        >>> suggestions = agent.get_suggestions()
        >>> for suggestion in suggestions:
        ...     print(f"{suggestion.title}: {suggestion.description}")
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize proactive agent.

        Args:
            db_path: Path to patterns database
        """
        if db_path is None:
            db_path = f"{DB_DIR}/patterns.db"

        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self):
        """Create patterns database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # User actions log
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS action_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT NOT NULL,
                        context TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        day_of_week INTEGER,
                        hour_of_day INTEGER
                    )
                """)

                # Learned patterns
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        pattern_key TEXT UNIQUE NOT NULL,
                        description TEXT,
                        confidence REAL DEFAULT 0.5,
                        frequency INTEGER DEFAULT 1,
                        first_seen TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        metadata TEXT
                    )
                """)

                # Suggestions history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS suggestions_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        suggestion_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        confidence REAL,
                        shown_at TEXT NOT NULL,
                        accepted BOOLEAN,
                        feedback TEXT
                    )
                """)

                # User preferences learned from feedback
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learned_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        preference_key TEXT UNIQUE NOT NULL,
                        preference_value TEXT NOT NULL,
                        confidence REAL DEFAULT 0.5,
                        updated_at TEXT NOT NULL
                    )
                """)

                # Indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_action_timestamp
                    ON action_log(timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_action_context
                    ON action_log(context)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_action_hour
                    ON action_log(hour_of_day)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pattern_type
                    ON patterns(pattern_type)
                """)

                conn.commit()
                logger.info("Patterns database initialized")

        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to initialize patterns database: {e}") from e

    def record_action(
        self,
        action: str,
        context: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Record a user action for pattern learning.

        Args:
            action: Action description (e.g., "checked email", "created task")
            context: Context (e.g., "morning", "work", "after_meeting")
            metadata: Optional metadata dictionary

        Returns:
            True if recorded successfully

        Example:
            >>> agent.record_action(
            ...     action="reviewed project tasks",
            ...     context="work",
            ...     metadata={"project": "Website Redesign", "duration": 300}
            ... )
        """
        try:
            now = datetime.now()
            timestamp = now.isoformat()
            day_of_week = now.weekday()  # 0=Monday, 6=Sunday
            hour_of_day = now.hour

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO action_log
                    (action, context, timestamp, metadata, day_of_week, hour_of_day)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    action,
                    context,
                    timestamp,
                    json.dumps(metadata) if metadata else None,
                    day_of_week,
                    hour_of_day
                ))
                conn.commit()

            # Trigger pattern learning asynchronously (simplified)
            self._update_patterns(action, context, day_of_week, hour_of_day)

            logger.debug(f"Recorded action: {action} (context: {context})")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to record action: {e}")
            return False

    def _update_patterns(
        self,
        action: str,
        context: Optional[str],
        day_of_week: int,
        hour_of_day: int
    ):
        """Update patterns based on new action."""
        try:
            now = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Time-based pattern
                time_key = f"time:{action}:{hour_of_day}"
                cursor.execute("""
                    INSERT INTO patterns
                    (pattern_type, pattern_key, description, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(pattern_key) DO UPDATE SET
                        frequency = frequency + 1,
                        last_seen = excluded.last_seen,
                        confidence = MIN(1.0, (frequency + 1) * 0.1)
                """, (
                    "time_based",
                    time_key,
                    f"User typically {action} around {hour_of_day}:00",
                    now,
                    now
                ))

                # Context-based pattern
                if context:
                    context_key = f"context:{action}:{context}"
                    cursor.execute("""
                        INSERT INTO patterns
                        (pattern_type, pattern_key, description, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(pattern_key) DO UPDATE SET
                            frequency = frequency + 1,
                            last_seen = excluded.last_seen,
                            confidence = MIN(1.0, (frequency + 1) * 0.1)
                    """, (
                        "context",
                        context_key,
                        f"User {action} in {context} context",
                        now,
                        now
                    ))

                # Day-of-week pattern
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_key = f"day:{action}:{day_of_week}"
                cursor.execute("""
                    INSERT INTO patterns
                    (pattern_type, pattern_key, description, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(pattern_key) DO UPDATE SET
                        frequency = frequency + 1,
                        last_seen = excluded.last_seen,
                        confidence = MIN(1.0, (frequency + 1) * 0.1)
                """, (
                    "day_based",
                    day_key,
                    f"User {action} on {day_names[day_of_week]}s",
                    now,
                    now
                ))

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Failed to update patterns: {e}")

    def get_suggestions(
        self,
        current_context: Optional[str] = None,
        limit: int = 5
    ) -> List[Suggestion]:
        """
        Get proactive suggestions based on learned patterns.

        Args:
            current_context: Current user context
            limit: Maximum number of suggestions

        Returns:
            List of suggestions ordered by priority and confidence

        Example:
            >>> suggestions = agent.get_suggestions(current_context="morning")
            >>> for s in suggestions:
            ...     print(f"{s.title} (confidence: {s.confidence:.0%})")
        """
        suggestions = []
        now = datetime.now()
        hour_of_day = now.hour
        day_of_week = now.weekday()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Time-based suggestions
                cursor.execute("""
                    SELECT pattern_key, description, confidence, frequency
                    FROM patterns
                    WHERE pattern_type = 'time_based'
                    AND pattern_key LIKE ?
                    AND confidence > 0.5
                    ORDER BY confidence DESC, frequency DESC
                    LIMIT 3
                """, (f"time:%:{hour_of_day}",))

                for row in cursor.fetchall():
                    pattern_key, description, confidence, frequency = row
                    action = pattern_key.split(":")[1]

                    suggestions.append(Suggestion(
                        suggestion_type="reminder",
                        title=f"Time for {action}?",
                        description=f"Based on your routine, you usually {action} around this time",
                        confidence=confidence,
                        priority=3,
                        action=action,
                        metadata={"frequency": frequency, "basis": "time_pattern"}
                    ))

                # Context-based suggestions
                if current_context:
                    cursor.execute("""
                        SELECT pattern_key, description, confidence, frequency
                        FROM patterns
                        WHERE pattern_type = 'context'
                        AND pattern_key LIKE ?
                        AND confidence > 0.4
                        ORDER BY confidence DESC, frequency DESC
                        LIMIT 3
                    """, (f"context:%:{current_context}",))

                    for row in cursor.fetchall():
                        pattern_key, description, confidence, frequency = row
                        action = pattern_key.split(":")[1]

                        suggestions.append(Suggestion(
                            suggestion_type="task",
                            title=f"Consider: {action}",
                            description=f"You often {action} when in {current_context} mode",
                            confidence=confidence,
                            priority=4,
                            action=action,
                            metadata={"frequency": frequency, "basis": "context_pattern"}
                        ))

                # Frequency-based suggestions (common tasks)
                cursor.execute("""
                    SELECT action, COUNT(*) as count
                    FROM action_log
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY action
                    ORDER BY count DESC
                    LIMIT 3
                """)

                for row in cursor.fetchall():
                    action, count = row
                    if count >= 3:  # At least 3 times in past week
                        suggestions.append(Suggestion(
                            suggestion_type="info",
                            title=f"Frequent action: {action}",
                            description=f"You've done this {count} times this week. Consider automating it?",
                            confidence=0.7,
                            priority=2,
                            metadata={"frequency": count, "basis": "frequency"}
                        ))

                # Missing pattern detection (things you used to do but haven't recently)
                cursor.execute("""
                    SELECT pattern_key, description, confidence
                    FROM patterns
                    WHERE last_seen < datetime('now', '-7 days')
                    AND frequency >= 5
                    AND confidence > 0.6
                    LIMIT 2
                """)

                for row in cursor.fetchall():
                    pattern_key, description, confidence = row
                    action = pattern_key.split(":")[1]

                    suggestions.append(Suggestion(
                        suggestion_type="reminder",
                        title=f"Haven't {action} lately",
                        description=f"You usually {action}, but haven't done it in over a week",
                        confidence=confidence,
                        priority=3,
                        action=action,
                        metadata={"basis": "missing_pattern"}
                    ))

            # Sort by priority and confidence
            suggestions.sort(key=lambda s: (s.priority, s.confidence), reverse=True)

            return suggestions[:limit]

        except sqlite3.Error as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

    def record_feedback(
        self,
        suggestion_title: str,
        accepted: bool,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Record user feedback on suggestions.

        Args:
            suggestion_title: Title of the suggestion
            accepted: Whether user accepted the suggestion
            feedback: Optional feedback text

        Returns:
            True if recorded successfully

        Example:
            >>> agent.record_feedback("Time for checked email?", accepted=True)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE suggestions_history
                    SET accepted = ?, feedback = ?
                    WHERE title = ?
                    ORDER BY shown_at DESC
                    LIMIT 1
                """, (accepted, feedback, suggestion_title))
                conn.commit()

            # Adjust patterns based on feedback
            if not accepted:
                # Reduce confidence for rejected suggestions
                # (Simplified - in production, this would be more sophisticated)
                logger.info(f"User rejected suggestion: {suggestion_title}")

            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def get_learned_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.3
    ) -> List[Pattern]:
        """
        Get all learned patterns.

        Args:
            pattern_type: Filter by pattern type
            min_confidence: Minimum confidence threshold

        Returns:
            List of learned patterns
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = """
                    SELECT pattern_type, description, confidence, frequency, last_seen, metadata
                    FROM patterns
                    WHERE confidence >= ?
                """
                params = [min_confidence]

                if pattern_type:
                    query += " AND pattern_type = ?"
                    params.append(pattern_type)

                query += " ORDER BY confidence DESC, frequency DESC"

                cursor.execute(query, params)

                patterns = []
                for row in cursor.fetchall():
                    patterns.append(Pattern(
                        pattern_type=row[0],
                        description=row[1],
                        confidence=row[2],
                        frequency=row[3],
                        last_seen=row[4],
                        metadata=json.loads(row[5]) if row[5] else None
                    ))

                return patterns

        except sqlite3.Error as e:
            logger.error(f"Failed to get patterns: {e}")
            return []

    def analyze_productivity(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze productivity patterns over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with productivity insights
        """
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total actions
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM action_log
                    WHERE timestamp > ?
                """, (cutoff,))
                total_actions = cursor.fetchone()[0]

                # Actions by hour
                cursor.execute("""
                    SELECT hour_of_day, COUNT(*) as count
                    FROM action_log
                    WHERE timestamp > ?
                    GROUP BY hour_of_day
                    ORDER BY count DESC
                """, (cutoff,))
                peak_hours = dict(cursor.fetchall())

                # Actions by day
                cursor.execute("""
                    SELECT day_of_week, COUNT(*) as count
                    FROM action_log
                    WHERE timestamp > ?
                    GROUP BY day_of_week
                    ORDER BY count DESC
                """, (cutoff,))
                busy_days = dict(cursor.fetchall())

                # Most common actions
                cursor.execute("""
                    SELECT action, COUNT(*) as count
                    FROM action_log
                    WHERE timestamp > ?
                    GROUP BY action
                    ORDER BY count DESC
                    LIMIT 10
                """, (cutoff,))
                common_actions = dict(cursor.fetchall())

                # Context distribution
                cursor.execute("""
                    SELECT context, COUNT(*) as count
                    FROM action_log
                    WHERE timestamp > ? AND context IS NOT NULL
                    GROUP BY context
                    ORDER BY count DESC
                """, (cutoff,))
                context_distribution = dict(cursor.fetchall())

                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                most_productive_day = day_names[max(busy_days.items(), key=lambda x: x[1])[0]] if busy_days else "N/A"
                peak_hour = max(peak_hours.items(), key=lambda x: x[1])[0] if peak_hours else 0

                return {
                    "period_days": days,
                    "total_actions": total_actions,
                    "avg_actions_per_day": round(total_actions / days, 1),
                    "most_productive_day": most_productive_day,
                    "peak_productivity_hour": f"{peak_hour}:00",
                    "common_actions": common_actions,
                    "context_distribution": context_distribution,
                    "hourly_distribution": peak_hours,
                    "daily_distribution": busy_days
                }

        except sqlite3.Error as e:
            logger.error(f"Failed to analyze productivity: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = ProactiveAgent()

    # Simulate some actions
    print("Recording sample actions...")
    agent.record_action("checked email", context="morning")
    agent.record_action("reviewed tasks", context="morning")
    agent.record_action("wrote code", context="work")
    agent.record_action("attended meeting", context="work")

    # Get suggestions
    print("\nProactive Suggestions:")
    suggestions = agent.get_suggestions(current_context="morning")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. [{suggestion.suggestion_type}] {suggestion.title}")
        print(f"   {suggestion.description}")
        print(f"   Confidence: {suggestion.confidence:.0%}\n")

    # Analyze productivity
    print("Productivity Analysis:")
    analysis = agent.analyze_productivity(days=7)
    print(json.dumps(analysis, indent=2))

    # Show learned patterns
    print("\nLearned Patterns:")
    patterns = agent.get_learned_patterns(min_confidence=0.3)
    for pattern in patterns[:5]:
        print(f"- [{pattern.pattern_type}] {pattern.description}")
        print(f"  Confidence: {pattern.confidence:.0%}, Frequency: {pattern.frequency}")
