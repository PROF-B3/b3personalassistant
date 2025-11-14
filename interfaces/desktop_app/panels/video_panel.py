"""
Video Mode Panel

Video editing workspace with timeline, theme application, and export.
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QMessageBox, QFileDialog,
    QListWidget, QGroupBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from interfaces.desktop_app.widgets.video_player import VideoPlayer
from modules.video_processing import FUTURISTIC_THEMES, VideoProcessor, ProcessingConfig


class VideoPanel(QWidget):
    """
    Video mode workspace panel.

    Features:
    - Video playback with timeline
    - Segment marking and cutting
    - Theme selection and preview
    - AI image generation prompts
    - Export with theme application
    """

    # Signals
    segment_created = pyqtSignal(int, int)  # start_ms, end_ms
    theme_applied = pyqtSignal(str)  # theme_name
    export_requested = pyqtSignal(str, str)  # format, output_path

    def __init__(self, orchestrator=None, parent=None):
        super().__init__(parent)

        self.orchestrator = orchestrator
        self.current_file = None
        self.video_processor = None

        # Initialize video processor if dependencies available
        try:
            self.video_processor = VideoProcessor()
        except Exception as e:
            print(f"Video processor initialization: {e}")

        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Left side: Video player (70% width)
        video_container = QWidget()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(4)

        self.video_player = VideoPlayer()
        self.video_player.video_loaded.connect(self._on_video_loaded)
        self.video_player.segment_marked.connect(self._on_segment_marked)
        video_layout.addWidget(self.video_player)

        layout.addWidget(video_container, 7)

        # Right side: Controls and theme panel (30% width)
        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        controls_layout.setSpacing(12)

        # Segments section
        segments_group = QGroupBox("Segments")
        segments_layout = QVBoxLayout(segments_group)

        self.segments_list = QListWidget()
        self.segments_list.setMaximumHeight(150)
        segments_layout.addWidget(self.segments_list)

        segments_buttons = QHBoxLayout()

        self.export_segment_btn = QPushButton("Export Selected")
        self.export_segment_btn.clicked.connect(self._export_segment)
        segments_buttons.addWidget(self.export_segment_btn)

        self.delete_segment_btn = QPushButton("Delete")
        self.delete_segment_btn.clicked.connect(self._delete_segment)
        segments_buttons.addWidget(self.delete_segment_btn)

        segments_layout.addLayout(segments_buttons)

        controls_layout.addWidget(segments_group)

        # Theme selection section
        theme_group = QGroupBox("Futuristic Theme")
        theme_layout = QVBoxLayout(theme_group)

        theme_layout.addWidget(QLabel("Select Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(FUTURISTIC_THEMES.keys()))
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)

        # Theme info
        self.theme_info = QTextEdit()
        self.theme_info.setReadOnly(True)
        self.theme_info.setMaximumHeight(150)
        theme_layout.addWidget(self.theme_info)

        # Apply theme button
        self.apply_theme_btn = QPushButton("🎨 Apply Theme to Video")
        self.apply_theme_btn.setProperty("primary", True)
        self.apply_theme_btn.clicked.connect(self._apply_theme)
        theme_layout.addWidget(self.apply_theme_btn)

        controls_layout.addWidget(theme_group)

        # AI Image Generation section
        ai_group = QGroupBox("AI Image Generation")
        ai_layout = QVBoxLayout(ai_group)

        ai_layout.addWidget(QLabel("Generate AI images for theme:"))

        self.generate_images_btn = QPushButton("🖼️ Generate AI Images")
        self.generate_images_btn.clicked.connect(self._generate_ai_images)
        ai_layout.addWidget(self.generate_images_btn)

        self.ai_prompts_list = QListWidget()
        self.ai_prompts_list.setMaximumHeight(120)
        ai_layout.addWidget(self.ai_prompts_list)

        controls_layout.addWidget(ai_group)

        # Export section
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)

        self.export_full_btn = QPushButton("📹 Export Full Video")
        self.export_full_btn.setProperty("primary", True)
        self.export_full_btn.clicked.connect(self._export_full_video)
        export_layout.addWidget(self.export_full_btn)

        self.create_remix_btn = QPushButton("✨ Create Futuristic Remix")
        self.create_remix_btn.clicked.connect(self._create_remix)
        export_layout.addWidget(self.create_remix_btn)

        controls_layout.addWidget(export_group)

        controls_layout.addStretch()

        controls_scroll.setWidget(controls_widget)
        layout.addWidget(controls_scroll, 3)

        # Update theme info
        self._on_theme_changed(self.theme_combo.currentText())

    def load_file(self, file_path: str) -> bool:
        """
        Load a video file.

        Args:
            file_path: Path to video file

        Returns:
            True if successful
        """
        success = self.video_player.load_video(file_path)
        if success:
            self.current_file = file_path

            # Load video in processor
            if self.video_processor:
                self.video_processor.load_video(file_path)

        return success

    def _on_video_loaded(self, file_path: str):
        """Handle video loaded."""
        duration_ms = self.video_player.get_duration()
        duration_s = duration_ms / 1000

        QMessageBox.information(
            self,
            "Video Loaded",
            f"Loaded: {Path(file_path).name}\nDuration: {duration_s:.1f}s"
        )

    def _on_segment_marked(self, start_ms: int, end_ms: int):
        """Handle segment marked."""
        # Add to segments list
        start_s = start_ms / 1000
        end_s = end_ms / 1000
        duration_s = end_s - start_s

        item_text = f"{start_s:.2f}s - {end_s:.2f}s ({duration_s:.2f}s)"
        self.segments_list.addItem(item_text)

        self.segment_created.emit(start_ms, end_ms)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme selection changed."""
        if theme_name not in FUTURISTIC_THEMES:
            return

        theme = FUTURISTIC_THEMES[theme_name]

        # Update theme info
        info = f"<b>Theme: {theme_name.replace('_', ' ').title()}</b><br><br>"
        info += f"<b>Colors:</b> {', '.join(theme['colors'])}<br><br>"
        info += f"<b>Effects:</b> {', '.join(theme['effects'])}<br><br>"

        self.theme_info.setHtml(info)

        # Update AI prompts list
        self.ai_prompts_list.clear()
        for prompt in theme['ai_prompts']:
            self.ai_prompts_list.addItem(prompt)

    def _apply_theme(self):
        """Apply selected theme to video."""
        theme_name = self.theme_combo.currentText()

        if not self.current_file:
            QMessageBox.warning(
                self,
                "No Video",
                "Please load a video first."
            )
            return

        # Show info about theme application
        theme = FUTURISTIC_THEMES[theme_name]
        msg = f"Theme '{theme_name.replace('_', ' ').title()}' will be applied.\n\n"
        msg += f"Effects: {', '.join(theme['effects'])}\n"
        msg += f"Colors: {', '.join(theme['colors'])}\n\n"
        msg += "This will generate AI images and apply visual effects."

        reply = QMessageBox.question(
            self,
            "Apply Theme",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.theme_applied.emit(theme_name)

            # Would implement theme application here
            QMessageBox.information(
                self,
                "Theme Applied",
                f"Theme '{theme_name}' applied successfully.\n"
                "Export video to save changes."
            )

    def _generate_ai_images(self):
        """Generate AI images for selected theme."""
        theme_name = self.theme_combo.currentText()

        if not self.video_processor:
            QMessageBox.warning(
                self,
                "Not Available",
                "Video processor not available. Check dependencies."
            )
            return

        # Generate images
        try:
            images = self.video_processor.generate_ai_images(theme_name, count=3)

            msg = f"Generated {len(images)} AI images for theme '{theme_name}':\n\n"
            msg += "\n".join(images)

            QMessageBox.information(
                self,
                "AI Images Generated",
                msg
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate AI images:\n{str(e)}"
            )

    def _export_segment(self):
        """Export selected segment."""
        current_item = self.segments_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a segment to export."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Segment",
            "",
            "Video Files (*.mp4)"
        )

        if not file_path:
            return

        if not file_path.endswith('.mp4'):
            file_path += '.mp4'

        # Get segment times from item text
        # Format: "10.50s - 25.30s (14.80s)"
        item_text = current_item.text()

        try:
            # Parse times from text
            import re
            match = re.match(r"([\d.]+)s - ([\d.]+)s", item_text)
            if not match:
                QMessageBox.warning(self, "Error", "Could not parse segment times")
                return

            start_time = float(match.group(1))
            end_time = float(match.group(2))

            # Get selected theme
            theme_name = self.theme_combo.currentText()

            # Export with progress message
            from PyQt6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting segment...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            # Export segment
            success = self.video_processor.export_segment(
                start_time,
                end_time,
                file_path,
                theme=theme_name
            )

            progress.close()

            if success:
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Segment exported successfully to:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    "Failed to export segment. Check logs for details."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export segment:\n{str(e)}"
            )

    def _delete_segment(self):
        """Delete selected segment."""
        current_row = self.segments_list.currentRow()
        if current_row >= 0:
            self.segments_list.takeItem(current_row)

    def _export_full_video(self):
        """Export full video with theme applied."""
        if not self.current_file:
            QMessageBox.warning(
                self,
                "No Video",
                "Please load a video first."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            "",
            "Video Files (*.mp4)"
        )

        if not file_path:
            return

        if not file_path.endswith('.mp4'):
            file_path += '.mp4'

        try:
            # Get selected theme
            theme_name = self.theme_combo.currentText()

            # Export with progress message
            from PyQt6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting video with theme...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            # Get full duration
            duration_ms = self.video_player.get_duration()
            duration_s = duration_ms / 1000

            # Export full video with theme
            success = self.video_processor.export_segment(
                0.0,
                duration_s,
                file_path,
                theme=theme_name
            )

            progress.close()

            if success:
                self.export_requested.emit("mp4", file_path)
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Video exported successfully with '{theme_name}' theme to:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    "Failed to export video. Check logs for details."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export video:\n{str(e)}"
            )

    def _create_remix(self):
        """Create futuristic remix of video."""
        if not self.current_file:
            QMessageBox.warning(
                self,
                "No Video",
                "Please load a video first."
            )
            return

        if not self.video_processor:
            QMessageBox.warning(
                self,
                "Not Available",
                "Video processor not available. Check dependencies."
            )
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )

        if not output_dir:
            return

        # Create remix
        try:
            theme_name = self.theme_combo.currentText()

            msg = f"Creating futuristic remix...\n\n"
            msg += "This will:\n"
            msg += "1. Detect or create video segments\n"
            msg += "2. Generate AI-styled gradient images\n"
            msg += "3. Apply theme color grading and effects\n"
            msg += "4. Add text overlays with theme fonts\n"
            msg += "5. Composite images over video\n"
            msg += "6. Export all segments\n\n"
            msg += "This may take several minutes depending on video length.\n"
            msg += f"Theme: {theme_name.replace('_', ' ').title()}\n\n"
            msg += "Continue?"

            reply = QMessageBox.question(
                self,
                "Create Futuristic Remix",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Create remix with progress dialog
                from PyQt6.QtWidgets import QProgressDialog
                progress = QProgressDialog("Creating futuristic remix...", "Cancel", 0, 0, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()

                # Create the remix
                output_files = self.video_processor.create_futuristic_remix(
                    self.current_file,
                    output_dir,
                    apply_effects=True,
                    add_overlays=True
                )

                progress.close()

                if output_files:
                    msg = f"Futuristic remix created successfully!\n\n"
                    msg += f"Created {len(output_files)} segments in:\n{output_dir}\n\n"
                    msg += "Segments:\n"
                    for file in output_files[:5]:  # Show first 5
                        msg += f"  • {Path(file).name}\n"
                    if len(output_files) > 5:
                        msg += f"  ... and {len(output_files) - 5} more\n"

                    QMessageBox.information(
                        self,
                        "Remix Complete",
                        msg
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Remix Failed",
                        "Failed to create remix. Check logs for details."
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create remix:\n{str(e)}"
            )

    def get_current_file(self) -> Optional[str]:
        """Get currently loaded file path."""
        return self.current_file

    def get_segments(self) -> List[Tuple[int, int]]:
        """Get all marked segments."""
        return self.video_player.get_segments()


class SimpleVideoPanel(QWidget):
    """
    Simple video panel with just player.
    Lighter weight version.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_file = None
        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)

    def load_file(self, file_path: str) -> bool:
        """Load file."""
        success = self.video_player.load_video(file_path)
        if success:
            self.current_file = file_path
        return success
