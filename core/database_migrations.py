"""
Database Migration System for B3PersonalAssistant

Provides a simple migration system for managing database schema changes
across different versions of the application.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Callable, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Represents a single database migration."""
    version: int
    name: str
    description: str
    up: Callable[[sqlite3.Connection], None]
    down: Optional[Callable[[sqlite3.Connection], None]] = None


class MigrationManager:
    """
    Manages database migrations with versioning and rollback support.

    Features:
    - Version tracking
    - Incremental migrations
    - Rollback support
    - Migration history
    """

    def __init__(self, db_path: str):
        """
        Initialize migration manager.

        Args:
            db_path: Path to the database file
        """
        self.db_path = Path(db_path)
        self.migrations: List[Migration] = []
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """Create the migration tracking table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version INTEGER UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        applied_at TEXT NOT NULL,
                        execution_time_ms INTEGER
                    )
                """)
                conn.commit()
                logger.info(f"Migration table ensured for {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to create migration table: {e}")
            raise

    def register_migration(self, migration: Migration):
        """
        Register a migration.

        Args:
            migration: Migration to register

        Raises:
            ValueError: If migration with same version already exists
        """
        # Check for duplicate version
        if any(m.version == migration.version for m in self.migrations):
            raise ValueError(f"Migration version {migration.version} already registered")

        self.migrations.append(migration)
        # Keep migrations sorted by version
        self.migrations.sort(key=lambda m: m.version)
        logger.debug(f"Registered migration v{migration.version}: {migration.name}")

    def get_current_version(self) -> int:
        """
        Get the current database schema version.

        Returns:
            Current schema version, or 0 if no migrations applied
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MAX(version) FROM schema_migrations
                """)
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except sqlite3.Error as e:
            logger.error(f"Failed to get current version: {e}")
            return 0

    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of migrations that haven't been applied yet.

        Returns:
            List of pending migrations in order
        """
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]

    def migrate_up(self, target_version: Optional[int] = None) -> bool:
        """
        Apply pending migrations up to target version.

        Args:
            target_version: Target version to migrate to (None = latest)

        Returns:
            True if all migrations succeeded

        Raises:
            Exception: If migration fails
        """
        pending = self.get_pending_migrations()

        if target_version is not None:
            pending = [m for m in pending if m.version <= target_version]

        if not pending:
            logger.info("No pending migrations")
            return True

        logger.info(f"Applying {len(pending)} migration(s)")

        for migration in pending:
            start_time = datetime.now()

            try:
                logger.info(f"Applying migration v{migration.version}: {migration.name}")

                with sqlite3.connect(self.db_path) as conn:
                    # Execute migration
                    migration.up(conn)

                    # Record migration
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO schema_migrations
                        (version, name, description, applied_at, execution_time_ms)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        migration.version,
                        migration.name,
                        migration.description,
                        datetime.now().isoformat(),
                        execution_time
                    ))
                    conn.commit()

                logger.info(f"Successfully applied migration v{migration.version} ({execution_time}ms)")

            except Exception as e:
                logger.error(f"Failed to apply migration v{migration.version}: {e}")
                raise

        final_version = self.get_current_version()
        logger.info(f"Migration complete. Current version: {final_version}")
        return True

    def migrate_down(self, target_version: int) -> bool:
        """
        Rollback migrations down to target version.

        Args:
            target_version: Target version to rollback to

        Returns:
            True if rollback succeeded

        Raises:
            Exception: If rollback fails
        """
        current_version = self.get_current_version()

        if target_version >= current_version:
            logger.warning(f"Target version {target_version} >= current version {current_version}")
            return True

        # Get migrations to rollback (in reverse order)
        migrations_to_rollback = [
            m for m in reversed(self.migrations)
            if target_version < m.version <= current_version
        ]

        logger.info(f"Rolling back {len(migrations_to_rollback)} migration(s)")

        for migration in migrations_to_rollback:
            if migration.down is None:
                logger.error(f"Migration v{migration.version} has no down migration")
                raise ValueError(f"Cannot rollback migration v{migration.version} - no down migration defined")

            try:
                logger.info(f"Rolling back migration v{migration.version}: {migration.name}")

                with sqlite3.connect(self.db_path) as conn:
                    # Execute rollback
                    migration.down(conn)

                    # Remove migration record
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM schema_migrations WHERE version = ?
                    """, (migration.version,))
                    conn.commit()

                logger.info(f"Successfully rolled back migration v{migration.version}")

            except Exception as e:
                logger.error(f"Failed to rollback migration v{migration.version}: {e}")
                raise

        final_version = self.get_current_version()
        logger.info(f"Rollback complete. Current version: {final_version}")
        return True

    def get_migration_history(self) -> List[Dict]:
        """
        Get history of applied migrations.

        Returns:
            List of applied migrations with metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT version, name, description, applied_at, execution_time_ms
                    FROM schema_migrations
                    ORDER BY version DESC
                """)

                history = []
                for row in cursor.fetchall():
                    history.append({
                        'version': row[0],
                        'name': row[1],
                        'description': row[2],
                        'applied_at': row[3],
                        'execution_time_ms': row[4]
                    })

                return history

        except sqlite3.Error as e:
            logger.error(f"Failed to get migration history: {e}")
            return []


# Example migrations for existing databases
def create_example_migrations(db_path: str) -> MigrationManager:
    """
    Create migration manager with example migrations.

    This demonstrates how to define migrations for your database.
    """
    manager = MigrationManager(db_path)

    # Example: Add index to improve query performance
    def migration_001_up(conn: sqlite3.Connection):
        """Add performance indexes."""
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_example ON some_table(column_name)")

    def migration_001_down(conn: sqlite3.Connection):
        """Remove performance indexes."""
        cursor = conn.cursor()
        cursor.execute("DROP INDEX IF EXISTS idx_example")

    manager.register_migration(Migration(
        version=1,
        name="add_performance_indexes",
        description="Add indexes to improve query performance",
        up=migration_001_up,
        down=migration_001_down
    ))

    return manager


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create migration manager
    manager = MigrationManager("databases/test.db")

    # Define a simple migration
    def migration_1_up(conn):
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

    def migration_1_down(conn):
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_table")

    # Register migration
    manager.register_migration(Migration(
        version=1,
        name="create_test_table",
        description="Create initial test table",
        up=migration_1_up,
        down=migration_1_down
    ))

    # Apply migrations
    print(f"Current version: {manager.get_current_version()}")
    print(f"Pending migrations: {len(manager.get_pending_migrations())}")

    manager.migrate_up()

    print(f"Current version after migration: {manager.get_current_version()}")
    print("\nMigration history:")
    for entry in manager.get_migration_history():
        print(f"  v{entry['version']}: {entry['name']} ({entry['execution_time_ms']}ms)")
