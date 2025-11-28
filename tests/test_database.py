"""
Tests for the database utilities module.

Tests cover:
- DatabaseManager initialization
- Connection context managers
- CRUD operations
- Migration support
"""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path

from core.database import (
    DatabaseManager,
    DatabaseConfig,
    MigrationManager,
    get_database,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DatabaseConfig(path=Path("/tmp/test.db"))
        assert config.timeout == 30.0
        assert config.check_same_thread is False
        assert config.isolation_level is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = DatabaseConfig(
            path=Path("/tmp/test.db"),
            timeout=60.0,
            check_same_thread=True,
            isolation_level="IMMEDIATE"
        )
        assert config.timeout == 60.0
        assert config.check_same_thread is True
        assert config.isolation_level == "IMMEDIATE"


class TestDatabaseManager:
    """Tests for DatabaseManager class."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)

    def test_initialization(self, temp_db_path):
        """Test database manager initialization."""
        db = DatabaseManager(temp_db_path)
        assert db.db_path == Path(temp_db_path)
        assert db.db_path.parent.exists()

    def test_connection_context_manager(self, temp_db_path):
        """Test connection context manager."""
        db = DatabaseManager(temp_db_path)

        with db.connection() as conn:
            assert conn is not None
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

        # Verify table was created
        with db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "test" in tables

    def test_cursor_context_manager(self, temp_db_path):
        """Test cursor context manager."""
        db = DatabaseManager(temp_db_path)

        # Create table first
        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")

        # Use cursor context manager
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO test VALUES (1, 'test')")

        # Verify insert
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM test")
            rows = cursor.fetchall()
            assert len(rows) == 1

    def test_execute_method(self, temp_db_path):
        """Test execute helper method."""
        db = DatabaseManager(temp_db_path)

        # Create table
        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'a')")
            conn.execute("INSERT INTO test VALUES (2, 'b')")

        # Query using execute
        results = db.execute("SELECT * FROM test WHERE id = ?", (1,))
        assert len(results) == 1
        assert results[0]['value'] == 'a'

    def test_execute_many(self, temp_db_path):
        """Test execute_many method."""
        db = DatabaseManager(temp_db_path)

        # Create table
        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")

        # Insert multiple rows
        data = [(1, 'a'), (2, 'b'), (3, 'c')]
        count = db.execute_many("INSERT INTO test VALUES (?, ?)", data)

        # Verify inserts
        results = db.execute("SELECT * FROM test")
        assert len(results) == 3

    def test_table_exists(self, temp_db_path):
        """Test table_exists method."""
        db = DatabaseManager(temp_db_path)

        assert not db.table_exists("test")

        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")

        assert db.table_exists("test")
        assert not db.table_exists("nonexistent")

    def test_get_table_info(self, temp_db_path):
        """Test get_table_info method."""
        db = DatabaseManager(temp_db_path)

        with db.connection() as conn:
            conn.execute("""
                CREATE TABLE test (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value REAL DEFAULT 0.0
                )
            """)

        info = db.get_table_info("test")

        assert len(info) == 3
        column_names = [col['name'] for col in info]
        assert 'id' in column_names
        assert 'name' in column_names
        assert 'value' in column_names

    def test_singleton_pattern(self, temp_db_path):
        """Test that same path returns same instance."""
        db1 = DatabaseManager(temp_db_path)
        db2 = DatabaseManager(temp_db_path)
        assert db1 is db2

    def test_error_handling(self, temp_db_path):
        """Test error handling and rollback."""
        db = DatabaseManager(temp_db_path)

        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test VALUES (1)")

        # Try to insert duplicate primary key
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO test VALUES (1)")

        # Original data should still be there
        results = db.execute("SELECT * FROM test")
        assert len(results) == 1

    def test_backup(self, temp_db_path):
        """Test database backup."""
        db = DatabaseManager(temp_db_path)

        with db.connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, data TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'test data')")

        # Create backup
        backup_path = temp_db_path + ".backup"
        db.backup(backup_path)

        # Verify backup
        backup_db = DatabaseManager(backup_path)
        results = backup_db.execute("SELECT * FROM test")
        assert len(results) == 1
        assert results[0]['data'] == 'test data'


class TestMigrationManager:
    """Tests for MigrationManager class."""

    @pytest.fixture
    def db_with_migrator(self):
        """Create a database with migration manager."""
        temp_dir = tempfile.mkdtemp()
        db_path = str(Path(temp_dir) / "test.db")
        db = DatabaseManager(db_path)
        migrator = MigrationManager(db)
        yield db, migrator
        shutil.rmtree(temp_dir)

    def test_migrations_table_created(self, db_with_migrator):
        """Test that migrations table is created."""
        db, migrator = db_with_migrator
        assert db.table_exists("_migrations")

    def test_get_applied_migrations_empty(self, db_with_migrator):
        """Test getting applied migrations when none exist."""
        db, migrator = db_with_migrator
        applied = migrator.get_applied_migrations()
        assert applied == []

    def test_apply_migration(self, db_with_migrator):
        """Test applying a migration."""
        db, migrator = db_with_migrator

        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
        result = migrator.apply_migration("001_create_users", sql)

        assert result is True
        assert db.table_exists("users")
        assert "001_create_users" in migrator.get_applied_migrations()

    def test_migration_not_reapplied(self, db_with_migrator):
        """Test that migrations are not reapplied."""
        db, migrator = db_with_migrator

        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY)"
        migrator.apply_migration("001_create_users", sql)

        # Try to apply again
        result = migrator.apply_migration("001_create_users", sql)
        assert result is False

    def test_multiple_migrations(self, db_with_migrator):
        """Test applying multiple migrations in order."""
        db, migrator = db_with_migrator

        migrations = [
            ("001_users", "CREATE TABLE users (id INTEGER PRIMARY KEY)"),
            ("002_posts", "CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER)"),
            ("003_comments", "CREATE TABLE comments (id INTEGER PRIMARY KEY, post_id INTEGER)"),
        ]

        for name, sql in migrations:
            migrator.apply_migration(name, sql)

        applied = migrator.get_applied_migrations()
        assert len(applied) == 3
        assert applied == ["001_users", "002_posts", "003_comments"]


class TestDatabaseHelpers:
    """Tests for database helper functions."""

    def test_get_database(self):
        """Test get_database helper."""
        temp_dir = tempfile.mkdtemp()
        try:
            import core.constants
            original_db_dir = core.constants.DATABASE_DIR
            core.constants.DATABASE_DIR = Path(temp_dir)

            db = get_database("test")
            assert db is not None
            assert "test.db" in str(db.db_path)
        finally:
            core.constants.DATABASE_DIR = original_db_dir
            shutil.rmtree(temp_dir)
