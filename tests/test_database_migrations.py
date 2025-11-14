"""
Unit tests for database migration system.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from core.database_migrations import Migration, MigrationManager
from core.exceptions import DatabaseException


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def migration_manager(temp_db):
    """Create a migration manager with temporary database."""
    return MigrationManager(temp_db)


class TestMigrationManager:
    """Test suite for MigrationManager."""

    def test_initialization(self, migration_manager, temp_db):
        """Test that migration manager initializes correctly."""
        assert migration_manager.db_path == Path(temp_db)
        assert migration_manager.migrations == []

        # Check migration table exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='schema_migrations'
            """)
            assert cursor.fetchone() is not None

    def test_get_current_version_empty(self, migration_manager):
        """Test getting current version when no migrations applied."""
        assert migration_manager.get_current_version() == 0

    def test_register_migration(self, migration_manager):
        """Test registering a migration."""
        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")

        migration = Migration(
            version=1,
            name="test_migration",
            description="Test migration",
            up=up
        )

        migration_manager.register_migration(migration)
        assert len(migration_manager.migrations) == 1
        assert migration_manager.migrations[0].version == 1

    def test_register_duplicate_version(self, migration_manager):
        """Test that registering duplicate version raises error."""
        def up(conn):
            pass

        migration1 = Migration(version=1, name="test1", description="", up=up)
        migration2 = Migration(version=1, name="test2", description="", up=up)

        migration_manager.register_migration(migration1)

        with pytest.raises(ValueError, match="already registered"):
            migration_manager.register_migration(migration2)

    def test_migrate_up(self, migration_manager, temp_db):
        """Test applying migrations."""
        def up_v1(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

        def up_v2(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT)")

        migration_manager.register_migration(Migration(
            version=1,
            name="create_users",
            description="Create users table",
            up=up_v1
        ))

        migration_manager.register_migration(Migration(
            version=2,
            name="create_posts",
            description="Create posts table",
            up=up_v2
        ))

        # Apply migrations
        result = migration_manager.migrate_up()
        assert result is True
        assert migration_manager.get_current_version() == 2

        # Check tables exist
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
                AND name IN ('users', 'posts')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            assert 'users' in tables
            assert 'posts' in tables

    def test_migrate_up_to_target(self, migration_manager):
        """Test migrating to specific version."""
        def up(conn):
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE test_{conn} (id INTEGER)")

        for i in range(1, 4):
            migration_manager.register_migration(Migration(
                version=i,
                name=f"migration_{i}",
                description="",
                up=up
            ))

        # Migrate only to version 2
        migration_manager.migrate_up(target_version=2)
        assert migration_manager.get_current_version() == 2

    def test_migrate_down(self, migration_manager, temp_db):
        """Test rolling back migrations."""
        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")

        def down(conn):
            cursor = conn.cursor()
            cursor.execute("DROP TABLE test_table")

        migration = Migration(
            version=1,
            name="test_migration",
            description="",
            up=up,
            down=down
        )

        migration_manager.register_migration(migration)
        migration_manager.migrate_up()

        assert migration_manager.get_current_version() == 1

        # Rollback
        migration_manager.migrate_down(target_version=0)
        assert migration_manager.get_current_version() == 0

        # Check table doesn't exist
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='test_table'
            """)
            assert cursor.fetchone() is None

    def test_migrate_down_without_down_function(self, migration_manager):
        """Test that rollback fails without down function."""
        def up(conn):
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")

        migration = Migration(
            version=1,
            name="test_migration",
            description="",
            up=up
            # No down function
        )

        migration_manager.register_migration(migration)
        migration_manager.migrate_up()

        with pytest.raises(ValueError, match="no down migration"):
            migration_manager.migrate_down(target_version=0)

    def test_get_pending_migrations(self, migration_manager):
        """Test getting list of pending migrations."""
        def up(conn):
            pass

        migration_manager.register_migration(Migration(
            version=1, name="m1", description="", up=up
        ))
        migration_manager.register_migration(Migration(
            version=2, name="m2", description="", up=up
        ))

        pending = migration_manager.get_pending_migrations()
        assert len(pending) == 2

        migration_manager.migrate_up(target_version=1)

        pending = migration_manager.get_pending_migrations()
        assert len(pending) == 1
        assert pending[0].version == 2

    def test_get_migration_history(self, migration_manager):
        """Test getting migration history."""
        def up(conn):
            pass

        migration_manager.register_migration(Migration(
            version=1, name="test_migration", description="Test desc", up=up
        ))

        migration_manager.migrate_up()

        history = migration_manager.get_migration_history()
        assert len(history) == 1
        assert history[0]['version'] == 1
        assert history[0]['name'] == "test_migration"
        assert 'applied_at' in history[0]
        assert 'execution_time_ms' in history[0]

    def test_migration_ordering(self, migration_manager):
        """Test that migrations are applied in version order."""
        def up(conn):
            pass

        # Register out of order
        migration_manager.register_migration(Migration(version=3, name="m3", description="", up=up))
        migration_manager.register_migration(Migration(version=1, name="m1", description="", up=up))
        migration_manager.register_migration(Migration(version=2, name="m2", description="", up=up))

        # Should be sorted by version
        assert migration_manager.migrations[0].version == 1
        assert migration_manager.migrations[1].version == 2
        assert migration_manager.migrations[2].version == 3

    def test_migration_failure_handling(self, migration_manager):
        """Test that migration failures are properly handled."""
        def up_failing(conn):
            raise Exception("Migration failed intentionally")

        migration = Migration(
            version=1,
            name="failing_migration",
            description="",
            up=up_failing
        )

        migration_manager.register_migration(migration)

        with pytest.raises(Exception, match="failed intentionally"):
            migration_manager.migrate_up()

        # Version should remain 0
        assert migration_manager.get_current_version() == 0


@pytest.mark.integration
class TestMigrationIntegration:
    """Integration tests for migrations with real database operations."""

    def test_complex_migration_workflow(self, temp_db):
        """Test a complex migration workflow."""
        manager = MigrationManager(temp_db)

        # Define migrations
        def create_users(conn):
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT
                )
            """)

        def drop_users(conn):
            cursor = conn.cursor()
            cursor.execute("DROP TABLE users")

        def add_created_at(conn):
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

        def remove_created_at(conn):
            # SQLite doesn't support DROP COLUMN directly
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT
                )
            """)
            cursor.execute("INSERT INTO users_new SELECT id, username, email FROM users")
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")

        manager.register_migration(Migration(
            version=1, name="create_users", description="", up=create_users, down=drop_users
        ))
        manager.register_migration(Migration(
            version=2, name="add_created_at", description="", up=add_created_at, down=remove_created_at
        ))

        # Apply all migrations
        manager.migrate_up()
        assert manager.get_current_version() == 2

        # Rollback to version 1
        manager.migrate_down(1)
        assert manager.get_current_version() == 1

        # Reapply
        manager.migrate_up()
        assert manager.get_current_version() == 2
