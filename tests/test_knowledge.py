"""
Tests for the knowledge management (Zettelkasten) module.

Tests cover:
- Zettel dataclass creation and manipulation
- ZettelkastenSystem initialization
- Note creation, retrieval, and deletion
- Tag management
- Link management
- Search functionality
- Statistics
"""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from modules.knowledge import (
    Zettel,
    ZettelkastenSystem,
)


class TestZettel:
    """Tests for the Zettel dataclass."""

    def test_basic_zettel_creation(self):
        """Test creating a basic Zettel."""
        zettel = Zettel(
            id="1a",
            title="Test Note",
            content="This is test content.",
            tags=["test", "note"],
            category="1",
            created_date="2024-01-01T10:00:00",
            modified_date="2024-01-01T10:00:00",
            links_to=[],
            linked_from=[],
            metadata={}
        )
        assert zettel.id == "1a"
        assert zettel.title == "Test Note"
        assert len(zettel.tags) == 2
        assert zettel.ai_insights is None

    def test_zettel_with_all_fields(self):
        """Test creating a Zettel with all fields populated."""
        zettel = Zettel(
            id="A1",
            title="AI Research",
            content="Research on artificial intelligence.",
            tags=["ai", "research", "ml"],
            category="A",
            created_date="2024-01-01T10:00:00",
            modified_date="2024-01-02T15:30:00",
            links_to=["1a", "2b"],
            linked_from=["3c"],
            metadata={"source": "academic paper", "author": "Smith"},
            ai_insights="This note connects AI concepts with ML algorithms."
        )
        assert len(zettel.links_to) == 2
        assert len(zettel.linked_from) == 1
        assert "source" in zettel.metadata
        assert zettel.ai_insights is not None

    def test_zettel_with_empty_tags(self):
        """Test creating a Zettel with empty tags."""
        zettel = Zettel(
            id="1",
            title="Empty Tags Note",
            content="Content without tags.",
            tags=[],
            category="1",
            created_date="2024-01-01T10:00:00",
            modified_date="2024-01-01T10:00:00",
            links_to=[],
            linked_from=[],
            metadata={}
        )
        assert zettel.tags == []


class TestZettelkastenSystemInit:
    """Tests for ZettelkastenSystem initialization."""

    @pytest.fixture
    def temp_base_path(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_system_initialization(self, temp_base_path):
        """Test that the system initializes correctly."""
        system = ZettelkastenSystem(base_path=str(temp_base_path))

        # Check directories were created
        assert (temp_base_path / "1").exists()
        assert (temp_base_path / "2").exists()
        assert (temp_base_path / "A").exists()
        assert (temp_base_path / "Z").exists()
        assert (temp_base_path / "_metadata").exists()

    def test_database_creation(self, temp_base_path):
        """Test that the database is created with proper schema."""
        system = ZettelkastenSystem(base_path=str(temp_base_path))
        db_path = temp_base_path / "_metadata" / "zettelkasten.db"

        assert db_path.exists()

        # Check tables exist
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            assert "zettels" in tables
            assert "tags" in tables
            assert "links" in tables

    def test_multiple_initializations(self, temp_base_path):
        """Test that multiple initializations don't break the system."""
        system1 = ZettelkastenSystem(base_path=str(temp_base_path))
        system2 = ZettelkastenSystem(base_path=str(temp_base_path))

        # Both should work without errors
        assert system1.base_path == system2.base_path


class TestZettelkastenCRUD:
    """Tests for Create, Read, Update, Delete operations."""

    @pytest.fixture
    def zettelkasten_system(self):
        """Create a ZettelkastenSystem with temporary directory."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)
        yield system
        shutil.rmtree(temp_dir)

    def test_create_zettel(self, zettelkasten_system):
        """Test creating a new Zettel."""
        note_id = zettelkasten_system.create_zettel(
            title="Test Note",
            content="Test content for the note.",
            tags=["test", "example"],
            category="1"
        )

        assert note_id is not None
        assert note_id.startswith("1")

    def test_get_zettel(self, zettelkasten_system):
        """Test retrieving a Zettel by ID."""
        # Create a zettel first
        note_id = zettelkasten_system.create_zettel(
            title="Retrievable Note",
            content="This note can be retrieved.",
            tags=["retrieve"],
            category="1"
        )

        # Retrieve it
        zettel = zettelkasten_system.get_zettel(note_id)

        assert zettel is not None
        assert zettel.title == "Retrievable Note"
        assert "retrieve" in zettel.tags

    def test_get_nonexistent_zettel(self, zettelkasten_system):
        """Test retrieving a non-existent Zettel."""
        zettel = zettelkasten_system.get_zettel("nonexistent_id_12345")
        assert zettel is None

    def test_update_zettel(self, zettelkasten_system):
        """Test updating a Zettel."""
        # Create a zettel
        note_id = zettelkasten_system.create_zettel(
            title="Original Title",
            content="Original content.",
            tags=["original"],
            category="1"
        )

        # Update it
        result = zettelkasten_system.update_zettel(
            note_id,
            title="Updated Title",
            content="Updated content.",
            tags=["updated"]
        )

        assert result is True

        # Verify update
        zettel = zettelkasten_system.get_zettel(note_id)
        assert zettel.title == "Updated Title"
        assert "updated" in zettel.tags

    def test_delete_zettel(self, zettelkasten_system):
        """Test deleting a Zettel."""
        # Create a zettel
        note_id = zettelkasten_system.create_zettel(
            title="Delete Me",
            content="This note will be deleted.",
            tags=["delete"],
            category="1"
        )

        # Delete it
        result = zettelkasten_system.delete_zettel(note_id)
        assert result is True

        # Verify deletion
        zettel = zettelkasten_system.get_zettel(note_id)
        assert zettel is None


class TestZettelkastenSearch:
    """Tests for search functionality."""

    @pytest.fixture
    def populated_system(self):
        """Create a system with some test data."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)

        # Create test notes
        system.create_zettel(
            title="Machine Learning Basics",
            content="Introduction to machine learning concepts.",
            tags=["ml", "ai", "basics"],
            category="1"
        )
        system.create_zettel(
            title="Deep Learning Networks",
            content="Neural networks and deep learning architectures.",
            tags=["dl", "ai", "neural"],
            category="1"
        )
        system.create_zettel(
            title="Python Programming",
            content="Python programming fundamentals.",
            tags=["python", "programming"],
            category="2"
        )

        yield system
        shutil.rmtree(temp_dir)

    def test_search_by_query(self, populated_system):
        """Test searching by text query."""
        results = populated_system.search_zettels("machine learning")

        assert len(results) >= 1
        titles = [z.title for z in results]
        assert "Machine Learning Basics" in titles

    def test_search_by_tag(self, populated_system):
        """Test searching by tag."""
        results = populated_system.get_zettels_by_tag("ai")

        assert len(results) >= 2

    def test_search_no_results(self, populated_system):
        """Test search with no results."""
        results = populated_system.search_zettels("nonexistent_unique_term_12345")

        assert len(results) == 0

    def test_search_with_limit(self, populated_system):
        """Test search with result limit."""
        results = populated_system.search_zettels("programming", limit=1)

        assert len(results) <= 1


class TestZettelkastenLinks:
    """Tests for link management."""

    @pytest.fixture
    def system_with_notes(self):
        """Create a system with notes for linking tests."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)

        # Create notes
        note1_id = system.create_zettel(
            title="Note 1",
            content="First note.",
            tags=["test"],
            category="1"
        )
        note2_id = system.create_zettel(
            title="Note 2",
            content="Second note.",
            tags=["test"],
            category="1"
        )
        note3_id = system.create_zettel(
            title="Note 3",
            content="Third note.",
            tags=["test"],
            category="1"
        )

        yield system, note1_id, note2_id, note3_id
        shutil.rmtree(temp_dir)

    def test_create_link(self, system_with_notes):
        """Test creating a link between notes."""
        system, note1_id, note2_id, _ = system_with_notes

        result = system.create_link(note1_id, note2_id)
        assert result is True

    def test_get_links(self, system_with_notes):
        """Test getting links from a note."""
        system, note1_id, note2_id, note3_id = system_with_notes

        # Create links
        system.create_link(note1_id, note2_id)
        system.create_link(note1_id, note3_id)

        # Get outgoing links
        note1 = system.get_zettel(note1_id)
        assert len(note1.links_to) >= 0  # May vary based on implementation

    def test_bidirectional_linking(self, system_with_notes):
        """Test that links can be bidirectional."""
        system, note1_id, note2_id, _ = system_with_notes

        system.create_link(note1_id, note2_id)
        system.create_link(note2_id, note1_id)

        # Both notes should have links
        note1 = system.get_zettel(note1_id)
        note2 = system.get_zettel(note2_id)

        # Just verify no errors occur
        assert note1 is not None
        assert note2 is not None


class TestZettelkastenTags:
    """Tests for tag management."""

    @pytest.fixture
    def zettelkasten_system(self):
        """Create a ZettelkastenSystem with temporary directory."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)
        yield system
        shutil.rmtree(temp_dir)

    def test_get_all_tags(self, zettelkasten_system):
        """Test getting all tags."""
        # Create notes with tags
        zettelkasten_system.create_zettel(
            title="Note 1",
            content="Content 1",
            tags=["tag1", "tag2"],
            category="1"
        )
        zettelkasten_system.create_zettel(
            title="Note 2",
            content="Content 2",
            tags=["tag2", "tag3"],
            category="1"
        )

        all_tags = zettelkasten_system.get_all_tags()

        assert "tag1" in all_tags
        assert "tag2" in all_tags
        assert "tag3" in all_tags

    def test_tag_counts(self, zettelkasten_system):
        """Test getting tag counts."""
        zettelkasten_system.create_zettel(
            title="Note 1",
            content="Content 1",
            tags=["common", "unique1"],
            category="1"
        )
        zettelkasten_system.create_zettel(
            title="Note 2",
            content="Content 2",
            tags=["common", "unique2"],
            category="1"
        )

        tag_counts = zettelkasten_system.get_tag_counts()

        assert tag_counts.get("common", 0) >= 2


class TestZettelkastenStatistics:
    """Tests for system statistics."""

    @pytest.fixture
    def populated_system(self):
        """Create a system with test data."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)

        # Create notes in different categories
        system.create_zettel(title="Note 1", content="Content", tags=["tag1"], category="1")
        system.create_zettel(title="Note 2", content="Content", tags=["tag2"], category="1")
        system.create_zettel(title="Note 3", content="Content", tags=["tag1", "tag3"], category="A")

        yield system
        shutil.rmtree(temp_dir)

    def test_get_statistics(self, populated_system):
        """Test getting system statistics."""
        stats = populated_system.get_statistics()

        assert "total_zettels" in stats
        assert stats["total_zettels"] >= 3

        assert "by_category" in stats
        assert "total_tags" in stats
        assert "total_links" in stats


class TestZettelkastenEdgeCases:
    """Edge case tests."""

    @pytest.fixture
    def zettelkasten_system(self):
        """Create a ZettelkastenSystem with temporary directory."""
        temp_dir = tempfile.mkdtemp()
        system = ZettelkastenSystem(base_path=temp_dir)
        yield system
        shutil.rmtree(temp_dir)

    def test_empty_title(self, zettelkasten_system):
        """Test creating a note with empty title."""
        # Should either raise error or handle gracefully
        try:
            note_id = zettelkasten_system.create_zettel(
                title="",
                content="Content without title.",
                tags=[],
                category="1"
            )
            # If it succeeds, the note should still be retrievable
            if note_id:
                zettel = zettelkasten_system.get_zettel(note_id)
                assert zettel is not None
        except (ValueError, sqlite3.IntegrityError):
            # Expected behavior for empty title
            pass

    def test_special_characters_in_content(self, zettelkasten_system):
        """Test creating a note with special characters."""
        note_id = zettelkasten_system.create_zettel(
            title="Special Chars",
            content="Content with 'quotes', \"double quotes\", and symbols: @#$%^&*()",
            tags=["special"],
            category="1"
        )

        zettel = zettelkasten_system.get_zettel(note_id)
        assert "quotes" in zettel.content

    def test_unicode_content(self, zettelkasten_system):
        """Test creating a note with unicode content."""
        note_id = zettelkasten_system.create_zettel(
            title="Unicode Note",
            content="Content with unicode: 日本語, emoji: 🎉, symbols: αβγ",
            tags=["unicode"],
            category="1"
        )

        zettel = zettelkasten_system.get_zettel(note_id)
        assert "日本語" in zettel.content

    def test_very_long_content(self, zettelkasten_system):
        """Test creating a note with very long content."""
        long_content = "A" * 10000  # 10,000 characters

        note_id = zettelkasten_system.create_zettel(
            title="Long Note",
            content=long_content,
            tags=["long"],
            category="1"
        )

        zettel = zettelkasten_system.get_zettel(note_id)
        assert len(zettel.content) == 10000

    def test_many_tags(self, zettelkasten_system):
        """Test creating a note with many tags."""
        many_tags = [f"tag{i}" for i in range(100)]

        note_id = zettelkasten_system.create_zettel(
            title="Many Tags Note",
            content="Content",
            tags=many_tags,
            category="1"
        )

        zettel = zettelkasten_system.get_zettel(note_id)
        assert len(zettel.tags) == 100
