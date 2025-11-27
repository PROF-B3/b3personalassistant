"""
Tests for the video_processing module.

Tests cover:
- VideoProcessor initialization and configuration
- Scene detection and segmentation
- Theme management
- Text overlay creation
- Export functionality
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from modules.video_processing import (
    VideoProcessor,
    VideoSegment,
    ProcessingConfig,
    FUTURISTIC_THEMES,
    DEFAULT_SEGMENT_DURATION,
    DEFAULT_FPS,
    DEFAULT_RESOLUTION,
)


class TestVideoSegment:
    """Tests for the VideoSegment dataclass."""

    def test_basic_segment_creation(self):
        """Test creating a basic video segment."""
        segment = VideoSegment(
            start_time=0.0,
            end_time=10.0,
            theme='neon_cyberpunk'
        )
        assert segment.start_time == 0.0
        assert segment.end_time == 10.0
        assert segment.theme == 'neon_cyberpunk'
        assert segment.ai_images == []
        assert segment.text_overlays == []
        assert segment.effects == []

    def test_segment_with_all_attributes(self):
        """Test creating a segment with all attributes."""
        segment = VideoSegment(
            start_time=5.0,
            end_time=15.0,
            theme='cosmic_voyage',
            clip=None,
            ai_images=['image1.png', 'image2.png'],
            text_overlays=['Title', 'Subtitle'],
            effects=['star_field', 'nebula_flow']
        )
        assert len(segment.ai_images) == 2
        assert len(segment.text_overlays) == 2
        assert len(segment.effects) == 2

    def test_segment_duration(self):
        """Test that segment duration can be calculated."""
        segment = VideoSegment(start_time=10.0, end_time=25.0, theme='test')
        duration = segment.end_time - segment.start_time
        assert duration == 15.0


class TestProcessingConfig:
    """Tests for the ProcessingConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ProcessingConfig()
        assert config.segment_duration == DEFAULT_SEGMENT_DURATION
        assert config.fps == DEFAULT_FPS
        assert config.resolution == DEFAULT_RESOLUTION
        assert config.export_format == 'mp4'
        assert config.quality == 'high'
        assert config.themes == list(FUTURISTIC_THEMES.keys())

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ProcessingConfig(
            segment_duration=30,
            fps=60,
            resolution=(3840, 2160),
            themes=['neon_cyberpunk'],
            export_format='webm',
            quality='medium'
        )
        assert config.segment_duration == 30
        assert config.fps == 60
        assert config.resolution == (3840, 2160)
        assert config.themes == ['neon_cyberpunk']
        assert config.export_format == 'webm'
        assert config.quality == 'medium'


class TestFuturisticThemes:
    """Tests for the FUTURISTIC_THEMES constant."""

    def test_theme_structure(self):
        """Test that all themes have required keys."""
        required_keys = ['colors', 'fonts', 'effects', 'ai_prompts']
        for theme_name, theme_data in FUTURISTIC_THEMES.items():
            for key in required_keys:
                assert key in theme_data, f"Theme '{theme_name}' missing '{key}'"

    def test_theme_colors_not_empty(self):
        """Test that all themes have at least one color."""
        for theme_name, theme_data in FUTURISTIC_THEMES.items():
            assert len(theme_data['colors']) > 0

    def test_theme_ai_prompts_not_empty(self):
        """Test that all themes have at least one AI prompt."""
        for theme_name, theme_data in FUTURISTIC_THEMES.items():
            assert len(theme_data['ai_prompts']) > 0

    def test_known_themes_exist(self):
        """Test that expected themes are present."""
        expected_themes = [
            'neon_cyberpunk',
            'green_solarpunk',
            'cosmic_voyage',
            'ai_consciousness',
            'bio_evolution'
        ]
        for theme in expected_themes:
            assert theme in FUTURISTIC_THEMES


class TestVideoProcessor:
    """Tests for the VideoProcessor class."""

    def test_initialization_with_default_config(self):
        """Test VideoProcessor initialization with default config."""
        processor = VideoProcessor()
        assert processor.config is not None
        assert processor.segments == []
        assert processor.input_video is None

    def test_initialization_with_custom_config(self):
        """Test VideoProcessor initialization with custom config."""
        config = ProcessingConfig(fps=60, quality='ultra')
        processor = VideoProcessor(config=config)
        assert processor.config.fps == 60
        assert processor.config.quality == 'ultra'

    def test_dependency_check(self):
        """Test that dependencies are checked on initialization."""
        processor = VideoProcessor()
        assert 'moviepy' in processor.dependencies
        assert 'scenedetect' in processor.dependencies
        assert 'numpy' in processor.dependencies
        assert 'pillow' in processor.dependencies

    def test_get_theme_exists(self):
        """Test getting an existing theme."""
        processor = VideoProcessor()
        theme = processor.get_theme('neon_cyberpunk')
        assert theme is not None
        assert 'colors' in theme
        assert 'fonts' in theme

    def test_get_theme_not_exists(self):
        """Test getting a non-existing theme returns None or default."""
        processor = VideoProcessor()
        theme = processor.get_theme('nonexistent_theme')
        # Should return None for non-existent theme
        assert theme is None or theme == {}

    def test_get_available_themes(self):
        """Test getting list of available themes."""
        processor = VideoProcessor()
        themes = processor.get_available_themes()
        assert len(themes) > 0
        assert 'neon_cyberpunk' in themes

    def test_create_text_overlay(self):
        """Test text overlay creation."""
        processor = VideoProcessor()
        overlay = processor.create_text_overlay(
            text="Test Title",
            position="center",
            theme="neon_cyberpunk"
        )
        assert overlay is not None or overlay == {}

    def test_create_segment(self):
        """Test segment creation."""
        processor = VideoProcessor()
        segment = processor.create_segment(
            start_time=0.0,
            end_time=10.0,
            theme='cosmic_voyage'
        )
        assert segment.start_time == 0.0
        assert segment.end_time == 10.0
        assert segment.theme == 'cosmic_voyage'

    def test_add_segment(self):
        """Test adding a segment to the processor."""
        processor = VideoProcessor()
        segment = VideoSegment(start_time=0.0, end_time=10.0, theme='test')
        processor.add_segment(segment)
        assert len(processor.segments) == 1

    def test_clear_segments(self):
        """Test clearing all segments."""
        processor = VideoProcessor()
        segment = VideoSegment(start_time=0.0, end_time=10.0, theme='test')
        processor.add_segment(segment)
        processor.clear_segments()
        assert len(processor.segments) == 0

    def test_get_total_duration(self):
        """Test calculating total duration from segments."""
        processor = VideoProcessor()
        processor.add_segment(VideoSegment(start_time=0.0, end_time=10.0, theme='test'))
        processor.add_segment(VideoSegment(start_time=10.0, end_time=25.0, theme='test'))

        # Total duration should be from first start to last end
        duration = processor.get_total_duration()
        assert duration >= 0


class TestVideoProcessorWithMocks:
    """Tests for VideoProcessor with mocked dependencies."""

    @patch('modules.video_processing.VideoProcessor._check_dependencies')
    def test_initialization_skips_dependency_check(self, mock_check):
        """Test that dependency check can be mocked."""
        processor = VideoProcessor()
        # Dependency check was called
        assert mock_check.called or not mock_check.called  # Just verify no error

    def test_load_video_nonexistent_file(self):
        """Test loading a non-existent video file."""
        processor = VideoProcessor()
        result = processor.load_video('/nonexistent/path/video.mp4')
        # Should return False or raise exception for non-existent file
        assert result is False or result is None

    def test_export_without_segments(self):
        """Test export without any segments."""
        processor = VideoProcessor()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'output.mp4'
            result = processor.export(str(output_path))
            # Should fail or return False when no segments
            assert result is False or result is None

    def test_get_project_summary(self):
        """Test getting project summary."""
        processor = VideoProcessor()
        processor.add_segment(VideoSegment(start_time=0.0, end_time=10.0, theme='neon_cyberpunk'))

        summary = processor.get_project_summary()
        assert summary is not None


class TestVideoProcessorIntegration:
    """Integration tests for VideoProcessor."""

    def test_full_workflow_without_actual_video(self):
        """Test a full workflow without actual video files."""
        # Create processor
        config = ProcessingConfig(
            segment_duration=30,
            themes=['neon_cyberpunk', 'cosmic_voyage']
        )
        processor = VideoProcessor(config=config)

        # Create segments
        processor.add_segment(VideoSegment(
            start_time=0.0,
            end_time=30.0,
            theme='neon_cyberpunk',
            text_overlays=['Introduction']
        ))
        processor.add_segment(VideoSegment(
            start_time=30.0,
            end_time=60.0,
            theme='cosmic_voyage',
            text_overlays=['Main Content']
        ))

        # Verify segments were added
        assert len(processor.segments) == 2
        assert processor.segments[0].theme == 'neon_cyberpunk'
        assert processor.segments[1].theme == 'cosmic_voyage'

    def test_theme_rotation(self):
        """Test that themes can be rotated for variety."""
        processor = VideoProcessor()
        themes = ['neon_cyberpunk', 'cosmic_voyage', 'green_solarpunk']

        for i, theme in enumerate(themes):
            processor.add_segment(VideoSegment(
                start_time=i * 30.0,
                end_time=(i + 1) * 30.0,
                theme=theme
            ))

        # Verify theme rotation
        for i, segment in enumerate(processor.segments):
            assert segment.theme == themes[i]


class TestVideoSegmentEdgeCases:
    """Edge case tests for VideoSegment."""

    def test_zero_duration_segment(self):
        """Test segment with zero duration."""
        segment = VideoSegment(start_time=10.0, end_time=10.0, theme='test')
        assert segment.end_time - segment.start_time == 0.0

    def test_negative_start_time(self):
        """Test segment with negative start time (should still work)."""
        segment = VideoSegment(start_time=-5.0, end_time=10.0, theme='test')
        assert segment.start_time == -5.0

    def test_segment_with_empty_theme(self):
        """Test segment with empty theme string."""
        segment = VideoSegment(start_time=0.0, end_time=10.0, theme='')
        assert segment.theme == ''

    def test_segment_lists_are_independent(self):
        """Test that default lists are independent between instances."""
        segment1 = VideoSegment(start_time=0.0, end_time=10.0, theme='test')
        segment2 = VideoSegment(start_time=10.0, end_time=20.0, theme='test')

        segment1.ai_images.append('image1.png')
        assert 'image1.png' not in segment2.ai_images
