"""
Database Utilities for B3PersonalAssistant

Provides database connection management with context managers,
connection pooling simulation, and common database operations.
"""

import sqlite3
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator
from contextlib import contextmanager
from dataclasses import dataclass

from core.constants import DATABASE_DIR

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    path: Path
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: Optional[str] = None


class DatabaseManager:
    """
    Database manager with connection pooling and context managers.

    Provides thread-safe database access with automatic connection
    management and error handling.

    Example:
        >>> db = DatabaseManager("databases/conversations.db")
        >>> with db.connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM conversations")
        ...     results = cursor.fetchall()
    """

    _instances: Dict[str, 'DatabaseManager'] = {}
    _lock = threading.Lock()

    def __new__(cls, db_path: str):
        """Singleton pattern per database path."""
        with cls._lock:
            if db_path not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[db_path] = instance
            return cls._instances[db_path]

    def __init__(self, db_path: str):
        """
        Initialize database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        if hasattr(self, '_initialized'):
            return

        self.db_path = Path(db_path)
        self.config = DatabaseConfig(path=self.db_path)
        self._local = threading.local()
        self._initialized = True

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"DatabaseManager initialized for {db_path}")

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection

        Example:
            >>> with db.connection() as conn:
            ...     conn.execute("INSERT INTO table VALUES (?)", (value,))
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=self.config.timeout,
                check_same_thread=self.config.check_same_thread,
                isolation_level=self.config.isolation_level
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for database cursor.

        Yields:
            sqlite3.Cursor: Database cursor

        Example:
            >>> with db.cursor() as cursor:
            ...     cursor.execute("SELECT * FROM table")
            ...     rows = cursor.fetchall()
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows
        """
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of rows affected
        """
        with self.cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script.

        Args:
            script: SQL script string
        """
        with self.connection() as conn:
            conn.executescript(script)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return len(result) > 0

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about table columns.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        with self.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            return [
                {
                    'id': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': bool(col[3]),
                    'default': col[4],
                    'pk': bool(col[5])
                }
                for col in columns
            ]

    def vacuum(self) -> None:
        """Optimize database by running VACUUM."""
        with self.connection() as conn:
            conn.execute("VACUUM")
        logger.info(f"Vacuumed database: {self.db_path}")

    def backup(self, backup_path: str) -> None:
        """
        Create a backup of the database.

        Args:
            backup_path: Path for the backup file
        """
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with self.connection() as source:
            backup_conn = sqlite3.connect(str(backup_path))
            try:
                source.backup(backup_conn)
                logger.info(f"Database backed up to: {backup_path}")
            finally:
                backup_conn.close()


def get_database(db_name: str) -> DatabaseManager:
    """
    Get a database manager instance.

    Args:
        db_name: Name of the database (e.g., 'conversations', 'tasks')

    Returns:
        DatabaseManager instance
    """
    db_path = DATABASE_DIR / f"{db_name}.db"
    return DatabaseManager(str(db_path))


# Convenience functions for common databases
def get_conversations_db() -> DatabaseManager:
    """Get the conversations database manager."""
    return get_database("conversations")


def get_tasks_db() -> DatabaseManager:
    """Get the tasks database manager."""
    return get_database("tasks")


# Migration support
class MigrationManager:
    """
    Manages database schema migrations.

    Example:
        >>> migrator = MigrationManager(db)
        >>> migrator.add_migration("001_initial", create_tables_sql)
        >>> migrator.run_migrations()
    """

    def __init__(self, db: DatabaseManager):
        """
        Initialize migration manager.

        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        with self.db.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration names."""
        results = self.db.execute("SELECT name FROM _migrations ORDER BY id")
        return [row['name'] for row in results]

    def apply_migration(self, name: str, sql: str) -> bool:
        """
        Apply a single migration.

        Args:
            name: Migration name
            sql: SQL to execute

        Returns:
            True if migration was applied, False if already applied
        """
        applied = self.get_applied_migrations()
        if name in applied:
            logger.debug(f"Migration {name} already applied")
            return False

        try:
            self.db.execute_script(sql)
            self.db.execute(
                "INSERT INTO _migrations (name) VALUES (?)",
                (name,)
            )
            logger.info(f"Applied migration: {name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Migration {name} failed: {e}")
            raise


if __name__ == "__main__":
    # Test database utilities
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, "test.db")
        db = DatabaseManager(test_db_path)

        # Create a test table
        with db.connection() as conn:
            conn.execute("""
                CREATE TABLE test (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value REAL
                )
            """)

        # Insert data
        db.execute("INSERT INTO test (name, value) VALUES (?, ?)", ("test1", 1.5))
        db.execute("INSERT INTO test (name, value) VALUES (?, ?)", ("test2", 2.5))

        # Query data
        results = db.execute("SELECT * FROM test")
        print(f"Found {len(results)} rows")

        # Check table exists
        print(f"Table 'test' exists: {db.table_exists('test')}")
        print(f"Table 'fake' exists: {db.table_exists('fake')}")

        # Get table info
        info = db.get_table_info("test")
        print(f"Table columns: {[col['name'] for col in info]}")

        print("Database utilities test passed!")
