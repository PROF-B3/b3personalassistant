"""
Automated tests for the onboarding system.
"""

import unittest
import tempfile
from pathlib import Path
import shutil
from modules.onboarding import OnboardingManager, UserPreferences, get_all_tutorials, get_tutorial
from modules.sample_data import SampleDataGenerator, generate_sample_data_for_onboarding


class TestOnboardingSystem(unittest.TestCase):
    """Test suite for onboarding system."""

    def setUp(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".b3assistant"
        self.manager = OnboardingManager(self.config_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_first_run_detection(self):
        """Test first run detection."""
        self.assertTrue(self.manager.is_first_run(), "Should be first run initially")
        self.manager.mark_first_run_complete()
        self.assertFalse(self.manager.is_first_run(), "Should not be first run after marking complete")

    def test_first_run_file_creation(self):
        """Test that first run file is created."""
        self.manager.mark_first_run_complete()
        self.assertTrue(self.manager.first_run_file.exists(), "First run file should exist")

    def test_preferences_default_values(self):
        """Test default preference values."""
        prefs = self.manager.preferences
        self.assertEqual(prefs.name, "User")
        self.assertEqual(prefs.theme, "dark")
        self.assertEqual(prefs.default_citation_style, "APA")
        self.assertEqual(prefs.default_video_theme, "neon_cyberpunk")
        self.assertTrue(prefs.auto_save)
        self.assertTrue(prefs.show_tooltips)

    def test_preferences_persistence(self):
        """Test preference saving and loading."""
        self.manager.preferences.name = "Test User"
        self.manager.preferences.default_citation_style = "MLA"
        self.manager.preferences.theme = "light"
        self.manager.save_preferences()

        # Create new manager to test loading
        manager2 = OnboardingManager(self.config_dir)
        self.assertEqual(manager2.preferences.name, "Test User")
        self.assertEqual(manager2.preferences.default_citation_style, "MLA")
        self.assertEqual(manager2.preferences.theme, "light")

    def test_preferences_to_dict(self):
        """Test preferences conversion to dictionary."""
        self.manager.preferences.name = "Test User"
        prefs_dict = self.manager.preferences.to_dict()

        self.assertIsInstance(prefs_dict, dict)
        self.assertEqual(prefs_dict['name'], "Test User")
        self.assertIn('theme', prefs_dict)
        self.assertIn('default_citation_style', prefs_dict)

    def test_tutorial_tracking(self):
        """Test tutorial completion tracking."""
        tutorial_id = 'basic_navigation'

        self.assertFalse(
            self.manager.is_tutorial_completed(tutorial_id),
            "Tutorial should not be completed initially"
        )

        self.manager.mark_tutorial_complete(tutorial_id)
        self.assertTrue(
            self.manager.is_tutorial_completed(tutorial_id),
            "Tutorial should be marked as completed"
        )

        # Check it's in completed list
        self.assertIn(tutorial_id, self.manager.preferences.completed_tutorials)

    def test_tutorial_progress_percentage(self):
        """Test tutorial completion percentage calculation."""
        # Initially 0%
        self.assertEqual(self.manager.get_completion_percentage(), 0)

        # Complete one tutorial (7 total, so ~14%)
        self.manager.mark_tutorial_complete('basic_navigation')
        progress = self.manager.get_completion_percentage()
        self.assertGreater(progress, 0)
        self.assertLessEqual(progress, 100)
        self.assertAlmostEqual(progress, 14.3, places=0)

        # Complete all tutorials (100%)
        for tutorial_id in get_all_tutorials().keys():
            self.manager.mark_tutorial_complete(tutorial_id)
        self.assertEqual(self.manager.get_completion_percentage(), 100)

    def test_workspace_creation(self):
        """Test workspace directory creation."""
        self.manager.preferences.workspace_path = str(Path(self.temp_dir) / "workspace")
        workspace_str = self.manager.create_default_workspace()
        workspace = Path(workspace_str)

        self.assertTrue(workspace.exists(), "Workspace directory should exist")
        self.assertTrue((workspace / "Papers").exists())
        self.assertTrue((workspace / "Notes").exists())
        self.assertTrue((workspace / "Documents").exists())
        self.assertTrue((workspace / "Videos").exists())
        self.assertTrue((workspace / "Projects").exists())
        self.assertTrue((workspace / "Assets").exists())
        self.assertTrue((workspace / "Exports").exists())

        # Check asset subdirectories
        self.assertTrue((workspace / "Assets" / "videos").exists())
        self.assertTrue((workspace / "Assets" / "images").exists())
        self.assertTrue((workspace / "Assets" / "audio").exists())

    def test_default_workspace_creation(self):
        """Test creating workspace with default path."""
        # Set workspace path
        self.manager.preferences.workspace_path = str(Path(self.temp_dir) / "default_workspace")
        workspace_str = self.manager.create_default_workspace()
        workspace = Path(workspace_str)

        self.assertTrue(workspace.exists())
        # Note: create_default_workspace always uses ~/B3Workspace, not preferences.workspace_path
        self.assertEqual(workspace.name, "B3Workspace")

    def test_all_tutorials_loaded(self):
        """Test that all 7 tutorials are available."""
        tutorials = get_all_tutorials()
        self.assertEqual(len(tutorials), 7, "Should have exactly 7 tutorials")

        # Check specific tutorials exist
        expected_ids = [
            'basic_navigation',
            'research_mode',
            'writing_mode',
            'video_mode',
            'agent_chat',
            'citation_management',
            'video_editing'
        ]

        for tutorial_id in expected_ids:
            self.assertIn(tutorial_id, tutorials, f"Tutorial '{tutorial_id}' should exist")

    def test_tutorial_structure(self):
        """Test that tutorials have required fields."""
        tutorials = get_all_tutorials()

        for tutorial_id, tutorial in tutorials.items():
            self.assertIn('id', tutorial)
            self.assertIn('title', tutorial)
            self.assertIn('description', tutorial)
            self.assertIn('duration', tutorial)
            self.assertIn('steps', tutorial)

            # Each tutorial should have multiple steps
            self.assertGreater(len(tutorial['steps']), 0)

            # Check step structure
            for step in tutorial['steps']:
                self.assertIn('title', step)
                self.assertIn('content', step)
                self.assertIn('action', step)

    def test_get_tutorial(self):
        """Test getting individual tutorial."""
        tutorial = get_tutorial('basic_navigation')
        self.assertIsNotNone(tutorial)
        self.assertEqual(tutorial['id'], 'basic_navigation')

        # Test non-existent tutorial
        invalid = get_tutorial('nonexistent_tutorial')
        self.assertIsNone(invalid)

    def test_next_tutorial_suggestion(self):
        """Test next tutorial suggestion."""
        # Initially should suggest first tutorial
        next_tut = self.manager.get_next_tutorial()
        self.assertIsNotNone(next_tut, "Should suggest a tutorial when none completed")

        # Complete first tutorial
        first_tutorial = list(get_all_tutorials().keys())[0]
        self.manager.mark_tutorial_complete(first_tutorial)

        # Should suggest next tutorial
        next_tut = self.manager.get_next_tutorial()
        self.assertIsNotNone(next_tut, "Should suggest next tutorial")
        self.assertNotEqual(next_tut, first_tutorial, "Should not suggest completed tutorial")

        # Complete all tutorials
        for tutorial_id in get_all_tutorials().keys():
            self.manager.mark_tutorial_complete(tutorial_id)

        # Should return None when all complete
        next_tut = self.manager.get_next_tutorial()
        self.assertIsNone(next_tut, "Should return None when all tutorials complete")

    def test_uncompleted_tutorials(self):
        """Test getting list of uncompleted tutorials."""
        uncompleted = self.manager.get_uncompleted_tutorials()
        self.assertEqual(len(uncompleted), 7, "All tutorials should be uncompleted initially")

        # Complete one
        self.manager.mark_tutorial_complete('basic_navigation')
        uncompleted = self.manager.get_uncompleted_tutorials()
        self.assertEqual(len(uncompleted), 6, "Should have 6 uncompleted tutorials")
        self.assertNotIn('basic_navigation', uncompleted)

    def test_preferences_reset(self):
        """Test preferences reset."""
        self.manager.preferences.name = "Test User"
        self.manager.preferences.default_citation_style = "MLA"
        self.manager.save_preferences()

        self.manager.reset_onboarding()

        # Reload and verify
        manager2 = OnboardingManager(self.config_dir)
        self.assertEqual(manager2.preferences.name, "User")
        self.assertEqual(manager2.preferences.default_citation_style, "APA")


class TestSampleDataGeneration(unittest.TestCase):
    """Test suite for sample data generation."""

    def setUp(self):
        """Create temporary workspace."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / "workspace"
        self.workspace.mkdir()
        self.generator = SampleDataGenerator(self.workspace)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_quickstart_generation(self):
        """Test quick start guide generation."""
        quickstart_path = self.generator.generate_quickstart_guide(self.workspace)

        self.assertTrue(Path(quickstart_path).exists(), "Quick start file should exist")

        # Check content
        with open(quickstart_path, 'r') as f:
            content = f.read()
            self.assertIn("Quick Start Guide", content)
            self.assertIn("Research Mode", content)
            self.assertIn("Video Mode", content)
            self.assertIn("Writing Mode", content)

    def test_sample_markdown_generation(self):
        """Test sample Markdown generation."""
        research_dir = self.workspace / "Research"
        research_dir.mkdir()

        sample_path = self.generator.generate_sample_markdown(research_dir)

        self.assertTrue(Path(sample_path).exists(), "Sample Markdown should exist")

        with open(sample_path, 'r') as f:
            content = f.read()
            self.assertIn("# ", content)  # Should have headings
            self.assertIn("##", content)

    def test_sample_notes_generation(self):
        """Test sample notes generation."""
        notes_dir = self.workspace / "Notes"
        notes_dir.mkdir()

        notes_path = self.generator.generate_sample_notes(notes_dir)

        self.assertTrue(Path(notes_path).exists(), "Sample notes should exist")

        with open(notes_path, 'r') as f:
            content = f.read()
            self.assertIn("tags:", content)  # Zettelkasten metadata
            self.assertIn("links:", content)

    def test_asset_directory_creation(self):
        """Test video asset directory creation."""
        self.generator.create_sample_video_assets(self.workspace)

        assets_dir = self.workspace / "Assets"
        self.assertTrue(assets_dir.exists())
        self.assertTrue((assets_dir / "videos").exists())
        self.assertTrue((assets_dir / "images").exists())
        self.assertTrue((assets_dir / "audio").exists())
        self.assertTrue((assets_dir / "texts").exists())

        # Check README files
        self.assertTrue((assets_dir / "videos" / "README.md").exists())

    def test_generate_all_samples(self):
        """Test generating all sample data at once."""
        result = self.generator.generate_all_samples()

        self.assertIsInstance(result, dict)
        self.assertIn('quickstart', result)
        self.assertIn('sample_markdown', result)
        self.assertIn('sample_notes', result)

        # Verify all files exist
        for file_path in result.values():
            if file_path:  # Some might be None
                self.assertTrue(Path(file_path).exists())

    def test_convenience_function(self):
        """Test convenience function for sample data generation."""
        # Use the convenience function
        result = generate_sample_data_for_onboarding(self.workspace)

        self.assertIsInstance(result, dict)
        self.assertTrue(len(result) > 0)


class TestUserPreferences(unittest.TestCase):
    """Test UserPreferences dataclass."""

    def test_preferences_creation(self):
        """Test creating UserPreferences."""
        prefs = UserPreferences()

        self.assertEqual(prefs.name, "User")
        self.assertEqual(prefs.theme, "dark")
        self.assertEqual(prefs.default_citation_style, "APA")

    def test_preferences_with_values(self):
        """Test creating preferences with custom values."""
        prefs = UserPreferences(
            name="Test User",
            theme="light",
            default_citation_style="MLA",
            default_video_theme="matrix",
            auto_save=False
        )

        self.assertEqual(prefs.name, "Test User")
        self.assertEqual(prefs.theme, "light")
        self.assertEqual(prefs.default_citation_style, "MLA")
        self.assertFalse(prefs.auto_save)

    def test_preferences_to_dict(self):
        """Test converting preferences to dictionary."""
        prefs = UserPreferences(name="Test User")
        prefs_dict = prefs.to_dict()

        self.assertIsInstance(prefs_dict, dict)
        self.assertEqual(prefs_dict['name'], "Test User")
        self.assertIn('completed_tutorials', prefs_dict)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
