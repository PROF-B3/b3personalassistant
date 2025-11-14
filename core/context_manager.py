"""
Context Manager for B3PersonalAssistant

Maintains conversation context, user preferences, and working memory across sessions.
Enables the assistant to "remember" previous interactions and provide coherent,
context-aware responses.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from core.constants import DB_DIR
from core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context that can be stored."""
    CONVERSATION = "conversation"
    WORK = "work"
    PERSONAL = "personal"
    PROJECT = "project"
    RESEARCH = "research"
    CUSTOM = "custom"


class ContextPriority(Enum):
    """Priority levels for context items."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextItem:
    """A single context item with metadata."""
    id: Optional[int] = None
    context_type: str = ContextType.CONVERSATION.value
    key: str = ""
    value: str = ""
    priority: int = ContextPriority.MEDIUM.value
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            k: v for k, v in asdict(self).items()
            if v is not None
        }


class ContextManager:
    """
    Manages conversation context and working memory.

    Features:
    - Short-term memory (current conversation)
    - Long-term memory (preferences, important facts)
    - Context switching (work vs personal vs projects)
    - Automatic context detection
    - Time-based context retrieval
    - Context compression and summarization

    Example:
        >>> context = ContextManager()
        >>> context.set("current_task", "Writing email to client")
        >>> context.set("user_preference_tone", "professional", priority=ContextPriority.HIGH)
        >>>
        >>> # Later...
        >>> task = context.get("current_task")
        >>> tone = context.get("user_preference_tone")
        >>>
        >>> # Get all relevant context for AI
        >>> relevant_context = context.get_relevant_context(limit=10)
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize context manager.

        Args:
            db_path: Path to database file (defaults to databases/context.db)
        """
        if db_path is None:
            db_path = f"{DB_DIR}/context.db"

        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

        # In-memory cache for fast access
        self._cache: Dict[str, ContextItem] = {}
        self._load_cache()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Context items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        context_type TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        priority INTEGER DEFAULT 2,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        expires_at TEXT,
                        metadata TEXT,
                        UNIQUE(context_type, key)
                    )
                """)

                # Context history (for conversation replay)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        context_type TEXT NOT NULL,
                        action TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)

                # Indexes for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_context_type
                    ON context_items(context_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_context_priority
                    ON context_items(priority)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_context_expires
                    ON context_items(expires_at)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_history_session
                    ON context_history(session_id)
                """)

                conn.commit()
                logger.info("Context database initialized successfully")

        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to initialize context database: {e}") from e

    def _load_cache(self):
        """Load high-priority items into memory cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, context_type, key, value, priority,
                           created_at, updated_at, expires_at, metadata
                    FROM context_items
                    WHERE priority >= ? AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY priority DESC, updated_at DESC
                    LIMIT 100
                """, (ContextPriority.MEDIUM.value, datetime.now().isoformat()))

                for row in cursor.fetchall():
                    item = ContextItem(
                        id=row[0],
                        context_type=row[1],
                        key=row[2],
                        value=row[3],
                        priority=row[4],
                        created_at=row[5],
                        updated_at=row[6],
                        expires_at=row[7],
                        metadata=json.loads(row[8]) if row[8] else None
                    )
                    self._cache[f"{row[1]}:{row[2]}"] = item

                logger.debug(f"Loaded {len(self._cache)} items into context cache")

        except sqlite3.Error as e:
            logger.error(f"Failed to load context cache: {e}")

    def set(
        self,
        key: str,
        value: Any,
        context_type: ContextType = ContextType.CONVERSATION,
        priority: ContextPriority = ContextPriority.MEDIUM,
        expires_in: Optional[timedelta] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Store a context item.

        Args:
            key: Context key (e.g., "current_task", "user_preference_tone")
            value: Context value (will be JSON-serialized if not string)
            context_type: Type of context
            priority: Priority level
            expires_in: Optional expiration time
            metadata: Optional metadata dictionary
            session_id: Optional session ID for history tracking

        Returns:
            True if successful

        Example:
            >>> context.set("current_project", "Website Redesign",
            ...             priority=ContextPriority.HIGH,
            ...             expires_in=timedelta(hours=8))
        """
        try:
            # Serialize value if not string
            if not isinstance(value, str):
                value = json.dumps(value)

            now = datetime.now().isoformat()
            expires_at = None
            if expires_in:
                expires_at = (datetime.now() + expires_in).isoformat()

            metadata_json = json.dumps(metadata) if metadata else None

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert or update
                cursor.execute("""
                    INSERT INTO context_items
                    (context_type, key, value, priority, created_at, updated_at, expires_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(context_type, key) DO UPDATE SET
                        value = excluded.value,
                        priority = excluded.priority,
                        updated_at = excluded.updated_at,
                        expires_at = excluded.expires_at,
                        metadata = excluded.metadata
                """, (
                    context_type.value, key, value, priority.value,
                    now, now, expires_at, metadata_json
                ))

                # Add to history if session_id provided
                if session_id:
                    cursor.execute("""
                        INSERT INTO context_history
                        (session_id, context_type, action, key, value, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (session_id, context_type.value, "set", key, value, now))

                conn.commit()

            # Update cache
            cache_key = f"{context_type.value}:{key}"
            self._cache[cache_key] = ContextItem(
                context_type=context_type.value,
                key=key,
                value=value,
                priority=priority.value,
                created_at=now,
                updated_at=now,
                expires_at=expires_at,
                metadata=metadata
            )

            logger.debug(f"Set context: {cache_key} = {value[:50]}...")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to set context {key}: {e}")
            raise DatabaseException(f"Failed to set context: {e}") from e

    def get(
        self,
        key: str,
        context_type: ContextType = ContextType.CONVERSATION,
        default: Any = None
    ) -> Optional[Any]:
        """
        Retrieve a context item.

        Args:
            key: Context key
            context_type: Type of context
            default: Default value if not found

        Returns:
            Context value or default

        Example:
            >>> task = context.get("current_task", default="No active task")
        """
        cache_key = f"{context_type.value}:{key}"

        # Check cache first
        if cache_key in self._cache:
            item = self._cache[cache_key]

            # Check expiration
            if item.expires_at:
                if datetime.fromisoformat(item.expires_at) < datetime.now():
                    self.delete(key, context_type)
                    return default

            # Try to deserialize JSON
            try:
                return json.loads(item.value)
            except (json.JSONDecodeError, TypeError):
                return item.value

        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value, expires_at
                    FROM context_items
                    WHERE context_type = ? AND key = ?
                """, (context_type.value, key))

                row = cursor.fetchone()
                if row:
                    value, expires_at = row

                    # Check expiration
                    if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                        self.delete(key, context_type)
                        return default

                    # Try to deserialize
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value

        except sqlite3.Error as e:
            logger.error(f"Failed to get context {key}: {e}")

        return default

    def get_relevant_context(
        self,
        context_types: Optional[List[ContextType]] = None,
        min_priority: ContextPriority = ContextPriority.LOW,
        limit: int = 20
    ) -> List[ContextItem]:
        """
        Get relevant context items for AI processing.

        Args:
            context_types: Filter by context types (None = all)
            min_priority: Minimum priority level
            limit: Maximum number of items

        Returns:
            List of context items, ordered by priority and recency

        Example:
            >>> # Get recent work-related context
            >>> work_context = context.get_relevant_context(
            ...     context_types=[ContextType.WORK, ContextType.PROJECT],
            ...     min_priority=ContextPriority.MEDIUM,
            ...     limit=10
            ... )
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build query
                query = """
                    SELECT id, context_type, key, value, priority,
                           created_at, updated_at, expires_at, metadata
                    FROM context_items
                    WHERE priority >= ? AND (expires_at IS NULL OR expires_at > ?)
                """
                params = [min_priority.value, datetime.now().isoformat()]

                if context_types:
                    placeholders = ",".join("?" * len(context_types))
                    query += f" AND context_type IN ({placeholders})"
                    params.extend([ct.value for ct in context_types])

                query += " ORDER BY priority DESC, updated_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)

                items = []
                for row in cursor.fetchall():
                    items.append(ContextItem(
                        id=row[0],
                        context_type=row[1],
                        key=row[2],
                        value=row[3],
                        priority=row[4],
                        created_at=row[5],
                        updated_at=row[6],
                        expires_at=row[7],
                        metadata=json.loads(row[8]) if row[8] else None
                    ))

                return items

        except sqlite3.Error as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []

    def delete(self, key: str, context_type: ContextType = ContextType.CONVERSATION) -> bool:
        """Delete a context item."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM context_items
                    WHERE context_type = ? AND key = ?
                """, (context_type.value, key))
                conn.commit()

            # Remove from cache
            cache_key = f"{context_type.value}:{key}"
            self._cache.pop(cache_key, None)

            logger.debug(f"Deleted context: {cache_key}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to delete context {key}: {e}")
            return False

    def clear(self, context_type: Optional[ContextType] = None) -> bool:
        """
        Clear context items.

        Args:
            context_type: Clear specific type, or all if None

        Example:
            >>> context.clear(ContextType.CONVERSATION)  # Clear conversation only
            >>> context.clear()  # Clear everything
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if context_type:
                    cursor.execute("DELETE FROM context_items WHERE context_type = ?",
                                   (context_type.value,))
                else:
                    cursor.execute("DELETE FROM context_items")

                conn.commit()

            # Clear cache
            if context_type:
                self._cache = {
                    k: v for k, v in self._cache.items()
                    if not k.startswith(f"{context_type.value}:")
                }
            else:
                self._cache.clear()

            logger.info(f"Cleared context: {context_type.value if context_type else 'all'}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to clear context: {e}")
            return False

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of current context state.

        Returns:
            Dictionary with context statistics and highlights
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count by type
                cursor.execute("""
                    SELECT context_type, COUNT(*), AVG(priority)
                    FROM context_items
                    WHERE expires_at IS NULL OR expires_at > ?
                    GROUP BY context_type
                """, (datetime.now().isoformat(),))

                type_counts = {row[0]: {"count": row[1], "avg_priority": row[2]}
                               for row in cursor.fetchall()}

                # Recent items
                cursor.execute("""
                    SELECT key, value, priority, updated_at
                    FROM context_items
                    WHERE expires_at IS NULL OR expires_at > ?
                    ORDER BY updated_at DESC
                    LIMIT 5
                """, (datetime.now().isoformat(),))

                recent = [
                    {"key": row[0], "value": row[1][:100], "priority": row[2], "updated": row[3]}
                    for row in cursor.fetchall()
                ]

                return {
                    "total_items": sum(data["count"] for data in type_counts.values()),
                    "by_type": type_counts,
                    "recent_updates": recent,
                    "cache_size": len(self._cache),
                }

        except sqlite3.Error as e:
            logger.error(f"Failed to get context summary: {e}")
            return {"error": str(e)}

    def format_for_ai(self, limit: int = 10) -> str:
        """
        Format context for AI prompt inclusion.

        Returns:
            Formatted string suitable for AI context window

        Example output:
            Current Context:
            - [WORK] current_project: Website Redesign
            - [PERSONAL] user_preference_tone: professional
            - [CONVERSATION] last_topic: email automation
        """
        items = self.get_relevant_context(limit=limit)

        if not items:
            return "No active context."

        lines = ["Current Context:"]
        for item in items:
            value = item.value[:100] + "..." if len(item.value) > 100 else item.value
            lines.append(f"- [{item.context_type.upper()}] {item.key}: {value}")

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize context manager
    context = ContextManager()

    # Set some context
    context.set("current_task", "Writing documentation")
    context.set("user_name", "Alice", priority=ContextPriority.HIGH)
    context.set("project_deadline", "2024-12-31", context_type=ContextType.WORK)
    context.set("temporary_note", "Check email", expires_in=timedelta(hours=1))

    # Retrieve context
    task = context.get("current_task")
    print(f"Current task: {task}")

    # Get relevant context for AI
    print("\n" + context.format_for_ai())

    # Get summary
    print("\nContext Summary:")
    print(json.dumps(context.get_context_summary(), indent=2))
