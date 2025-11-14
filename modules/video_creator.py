"""
Video Creator Module

Create videos from prompts using assets (videos, images, texts).
Supports 1-20 minute video generation with AI assistance.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class VideoAsset:
    """Represents an asset for video creation."""
    type: str  # 'video', 'image', 'text', 'audio'
    path: Optional[str] = None
    content: Optional[str] = None  # For text assets
    duration: Optional[float] = None  # Duration to display
    position: str = 'center'  # Position for overlays
    effects: List[str] = field(default_factory=list)

@dataclass
class VideoScript:
    """Represents a video script/storyboard."""
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    total_duration: float = 0.0
    theme: str = 'neon_cyberpunk'
    background_music: Optional[str] = None

class VideoCreator:
    """
    Create videos from prompts and assets.

    Features:
    - Parse natural language prompts
    - Assemble videos from multiple assets
    - Add text overlays and transitions
    - Support 1-20 minute duration
    - Theme-based styling
    """

    def __init__(self):
        """Initialize video creator."""
        self.logger = logging.getLogger("video_creator")
        self.assets_dir = Path("assets")
        self.output_dir = Path("created_videos")

        # Create directories
        self.assets_dir.mkdir(exist_ok=True)
        (self.assets_dir / "videos").mkdir(exist_ok=True)
        (self.assets_dir / "images").mkdir(exist_ok=True)
        (self.assets_dir / "audio").mkdir(exist_ok=True)
        (self.assets_dir / "texts").mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Check dependencies
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required libraries are available."""
        self.dependencies = {
            'moviepy': False,
            'pillow': False,
            'numpy': False
        }

        try:
            import moviepy.editor as mp
            self.dependencies['moviepy'] = True
        except ImportError:
            pass

        try:
            from PIL import Image
            self.dependencies['pillow'] = True
        except ImportError:
            pass

        try:
            import numpy as np
            self.dependencies['numpy'] = True
        except ImportError:
            pass

    def parse_prompt(self, prompt: str, target_duration: int = 60) -> VideoScript:
        """
        Parse a natural language prompt into a video script.

        Args:
            prompt: Natural language description of desired video
            target_duration: Target duration in seconds (60-1200 for 1-20 mins)

        Returns:
            VideoScript object
        """
        script = VideoScript()
        script.total_duration = min(max(target_duration, 60), 1200)  # 1-20 minutes

        # Simple keyword-based parsing (can be enhanced with AI)
        prompt_lower = prompt.lower()

        # Detect theme from keywords
        if 'cyberpunk' in prompt_lower or 'neon' in prompt_lower:
            script.theme = 'neon_cyberpunk'
        elif 'nature' in prompt_lower or 'eco' in prompt_lower or 'green' in prompt_lower:
            script.theme = 'green_solarpunk'
        elif 'space' in prompt_lower or 'cosmic' in prompt_lower or 'galaxy' in prompt_lower:
            script.theme = 'cosmic_voyage'
        elif 'ai' in prompt_lower or 'neural' in prompt_lower or 'digital' in prompt_lower:
            script.theme = 'ai_consciousness'
        elif 'bio' in prompt_lower or 'evolution' in prompt_lower or 'dna' in prompt_lower:
            script.theme = 'bio_evolution'

        self.logger.info(f"Detected theme: {script.theme}")
        self.logger.info(f"Target duration: {script.total_duration}s ({script.total_duration/60:.1f} minutes)")

        return script

    def add_asset(self, asset: VideoAsset) -> bool:
        """
        Add an asset to the asset library.

        Args:
            asset: VideoAsset object

        Returns:
            True if successful
        """
        try:
            if asset.type == 'video' and asset.path:
                target_dir = self.assets_dir / "videos"
                target_path = target_dir / Path(asset.path).name

                if not Path(asset.path).exists():
                    self.logger.error(f"Video file not found: {asset.path}")
                    return False

                # Copy if not already in assets
                if not target_path.exists():
                    import shutil
                    shutil.copy(asset.path, target_path)

                self.logger.info(f"Added video asset: {target_path}")
                return True

            elif asset.type == 'image' and asset.path:
                target_dir = self.assets_dir / "images"
                target_path = target_dir / Path(asset.path).name

                if not Path(asset.path).exists():
                    self.logger.error(f"Image file not found: {asset.path}")
                    return False

                if not target_path.exists():
                    import shutil
                    shutil.copy(asset.path, target_path)

                self.logger.info(f"Added image asset: {target_path}")
                return True

            elif asset.type == 'audio' and asset.path:
                target_dir = self.assets_dir / "audio"
                target_path = target_dir / Path(asset.path).name

                if not Path(asset.path).exists():
                    self.logger.error(f"Audio file not found: {asset.path}")
                    return False

                if not target_path.exists():
                    import shutil
                    shutil.copy(asset.path, target_path)

                self.logger.info(f"Added audio asset: {target_path}")
                return True

            elif asset.type == 'text' and asset.content:
                # Save text content
                target_dir = self.assets_dir / "texts"
                target_path = target_dir / f"text_{hash(asset.content)}.txt"

                with open(target_path, 'w') as f:
                    f.write(asset.content)

                self.logger.info(f"Added text asset: {target_path}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to add asset: {e}")
            return False

    def list_assets(self, asset_type: Optional[str] = None) -> List[str]:
        """
        List available assets.

        Args:
            asset_type: Filter by type ('video', 'image', 'audio', 'text')

        Returns:
            List of asset paths
        """
        assets = []

        if asset_type is None or asset_type == 'video':
            video_dir = self.assets_dir / "videos"
            if video_dir.exists():
                assets.extend([str(p) for p in video_dir.glob("*.*")])

        if asset_type is None or asset_type == 'image':
            image_dir = self.assets_dir / "images"
            if image_dir.exists():
                assets.extend([str(p) for p in image_dir.glob("*.*")])

        if asset_type is None or asset_type == 'audio':
            audio_dir = self.assets_dir / "audio"
            if audio_dir.exists():
                assets.extend([str(p) for p in audio_dir.glob("*.*")])

        if asset_type is None or asset_type == 'text':
            text_dir = self.assets_dir / "texts"
            if text_dir.exists():
                assets.extend([str(p) for p in text_dir.glob("*.txt")])

        return assets

    def create_video_from_prompt(self, prompt: str,
                                 video_assets: List[str] = None,
                                 image_assets: List[str] = None,
                                 text_overlays: List[str] = None,
                                 target_duration: int = 60,
                                 output_path: Optional[str] = None) -> Optional[str]:
        """
        Create a video from a prompt and assets.

        Args:
            prompt: Natural language description
            video_assets: List of video file paths to use
            image_assets: List of image file paths to use
            text_overlays: List of text strings to overlay
            target_duration: Target duration in seconds (60-1200)
            output_path: Optional custom output path

        Returns:
            Path to created video, or None if failed
        """
        try:
            if not self.dependencies['moviepy']:
                self.logger.error("MoviePy not available")
                return None

            import moviepy.editor as mp
            from modules.video_processing import FUTURISTIC_THEMES

            # Parse prompt
            script = self.parse_prompt(prompt, target_duration)

            # Get theme data
            if script.theme in FUTURISTIC_THEMES:
                theme_data = FUTURISTIC_THEMES[script.theme]
            else:
                theme_data = FUTURISTIC_THEMES['neon_cyberpunk']

            clips = []
            current_time = 0.0

            # Add video clips
            if video_assets:
                for video_path in video_assets:
                    if not os.path.exists(video_path):
                        self.logger.warning(f"Video not found: {video_path}")
                        continue

                    video_clip = mp.VideoFileClip(video_path)

                    # Limit duration to fit target
                    remaining_time = script.total_duration - current_time
                    if remaining_time <= 0:
                        break

                    if video_clip.duration > remaining_time:
                        video_clip = video_clip.subclip(0, remaining_time)

                    # Set start time
                    video_clip = video_clip.set_start(current_time)
                    clips.append(video_clip)
                    current_time += video_clip.duration

            # Fill remaining time with images
            if image_assets and current_time < script.total_duration:
                remaining_time = script.total_duration - current_time
                time_per_image = remaining_time / len(image_assets)
                time_per_image = max(3.0, min(time_per_image, 10.0))  # 3-10 seconds per image

                for img_path in image_assets:
                    if not os.path.exists(img_path):
                        self.logger.warning(f"Image not found: {img_path}")
                        continue

                    if current_time >= script.total_duration:
                        break

                    img_clip = mp.ImageClip(img_path)
                    img_clip = img_clip.set_duration(time_per_image)
                    img_clip = img_clip.set_start(current_time)

                    # Add zoom effect to images
                    img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)

                    clips.append(img_clip)
                    current_time += time_per_image

            if not clips:
                self.logger.error("No valid video or image assets provided")
                return None

            # Composite all clips
            final_clip = mp.CompositeVideoClip(clips, size=(1920, 1080))

            # Add text overlays
            if text_overlays:
                text_clips = []
                overlay_duration = final_clip.duration / len(text_overlays)

                for i, text in enumerate(text_overlays):
                    # Create text clip
                    from modules.video_processing import VideoProcessor
                    processor = VideoProcessor()

                    txt_clip = processor.create_text_overlay(
                        text,
                        duration=overlay_duration,
                        theme=script.theme,
                        position='bottom',
                        font_size=50
                    )

                    if txt_clip:
                        txt_clip = txt_clip.set_start(i * overlay_duration)
                        text_clips.append(txt_clip)

                if text_clips:
                    final_clip = mp.CompositeVideoClip([final_clip] + text_clips)

            # Apply theme color grading
            from modules.video_processing import VideoProcessor
            processor = VideoProcessor()
            final_clip = processor.apply_theme_effects(final_clip, script.theme)

            # Set output path
            if output_path is None:
                output_path = str(self.output_dir / f"created_video_{script.theme}.mp4")

            # Export
            self.logger.info(f"Creating video: {output_path}")
            self.logger.info(f"Duration: {final_clip.duration:.1f}s")
            self.logger.info(f"Theme: {script.theme}")

            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium'
            )

            # Cleanup
            for clip in clips:
                clip.close()
            final_clip.close()

            self.logger.info(f"Video created successfully: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to create video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_slideshow(self, images: List[str],
                        duration_per_image: float = 5.0,
                        transition: str = 'fade',
                        theme: str = 'neon_cyberpunk',
                        text_overlays: Optional[List[str]] = None,
                        background_music: Optional[str] = None,
                        output_path: Optional[str] = None) -> Optional[str]:
        """
        Create a slideshow video from images.

        Args:
            images: List of image paths
            duration_per_image: Duration for each image in seconds
            transition: Transition type ('fade', 'slide', 'zoom')
            theme: Theme to apply
            text_overlays: Optional text for each image
            background_music: Optional background music path
            output_path: Optional output path

        Returns:
            Path to created video
        """
        try:
            if not self.dependencies['moviepy']:
                self.logger.error("MoviePy not available")
                return None

            import moviepy.editor as mp

            clips = []

            for i, img_path in enumerate(images):
                if not os.path.exists(img_path):
                    self.logger.warning(f"Image not found: {img_path}")
                    continue

                # Load image
                img_clip = mp.ImageClip(img_path)
                img_clip = img_clip.set_duration(duration_per_image)

                # Add effect based on transition type
                if transition == 'zoom':
                    # Zoom in effect
                    img_clip = img_clip.resize(lambda t: 1 + 0.1 * (t / duration_per_image))
                elif transition == 'slide':
                    # Slide in from right
                    w, h = img_clip.size
                    img_clip = img_clip.set_position(lambda t: (w * (1 - t/duration_per_image), 0))

                # Add text overlay if provided
                if text_overlays and i < len(text_overlays):
                    from modules.video_processing import VideoProcessor
                    processor = VideoProcessor()

                    txt_clip = processor.create_text_overlay(
                        text_overlays[i],
                        duration=duration_per_image,
                        theme=theme,
                        position='bottom'
                    )

                    if txt_clip:
                        img_clip = mp.CompositeVideoClip([img_clip, txt_clip])

                clips.append(img_clip)

            if not clips:
                self.logger.error("No valid images provided")
                return None

            # Concatenate clips
            if transition == 'fade':
                # Add crossfade between clips
                final_clip = mp.concatenate_videoclips(clips, method="compose")
            else:
                final_clip = mp.concatenate_videoclips(clips)

            # Apply theme
            from modules.video_processing import VideoProcessor
            processor = VideoProcessor()
            final_clip = processor.apply_theme_effects(final_clip, theme)

            # Add background music
            if background_music and os.path.exists(background_music):
                final_clip = processor.add_background_music(final_clip, background_music, volume=0.3)

            # Set output path
            if output_path is None:
                output_path = str(self.output_dir / f"slideshow_{theme}.mp4")

            # Export
            self.logger.info(f"Creating slideshow: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30
            )

            # Cleanup
            for clip in clips:
                clip.close()
            final_clip.close()

            self.logger.info(f"Slideshow created: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to create slideshow: {e}")
            import traceback
            traceback.print_exc()
            return None
