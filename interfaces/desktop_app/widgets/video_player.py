"""
Video Player Widget

Provides video playback with timeline navigation and editing controls.
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider,
    QLabel, QStyle, QSizePolicy
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QMouseEvent


class TimelineWidget(QWidget):
    """
    Timeline widget for video navigation and segment marking.

    Features:
    - Visual timeline with playhead
    - Segment markers
    - Click to seek
    - Drag to scrub
    """

    seek_requested = pyqtSignal(int)  # position in ms
    segment_added = pyqtSignal(int, int)  # start, end in ms

    def __init__(self, parent=None):
        super().__init__(parent)

        self.duration = 0  # in ms
        self.position = 0  # in ms
        self.segments: List[Tuple[int, int]] = []  # (start, end) in ms
        self.mark_start: Optional[int] = None  # for marking segments

        self.setMinimumHeight(60)
        self.setMouseTracking(True)

    def set_duration(self, duration_ms: int):
        """Set total duration."""
        self.duration = duration_ms
        self.update()

    def set_position(self, position_ms: int):
        """Update playhead position."""
        self.position = position_ms
        self.update()

    def add_segment(self, start_ms: int, end_ms: int):
        """Add a segment marker."""
        self.segments.append((start_ms, end_ms))
        self.update()

    def clear_segments(self):
        """Clear all segment markers."""
        self.segments.clear()
        self.update()

    def start_marking(self):
        """Start marking a segment at current position."""
        self.mark_start = self.position

    def finish_marking(self):
        """Finish marking segment at current position."""
        if self.mark_start is not None:
            start = min(self.mark_start, self.position)
            end = max(self.mark_start, self.position)
            self.add_segment(start, end)
            self.segment_added.emit(start, end)
            self.mark_start = None

    def paintEvent(self, event):
        """Draw timeline."""
        if self.duration == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background
        painter.fillRect(0, 0, width, height, QColor('#2D2D30'))

        # Timeline background
        timeline_y = height // 2 - 4
        timeline_height = 8
        painter.fillRect(0, timeline_y, width, timeline_height, QColor('#3E3E42'))

        # Draw segments
        for start_ms, end_ms in self.segments:
            if self.duration > 0:
                start_x = int(start_ms / self.duration * width)
                end_x = int(end_ms / self.duration * width)
                segment_width = max(end_x - start_x, 2)

                painter.fillRect(
                    start_x, timeline_y,
                    segment_width, timeline_height,
                    QColor('#007ACC')
                )

        # Draw marking in progress
        if self.mark_start is not None:
            start_x = int(self.mark_start / self.duration * width)
            end_x = int(self.position / self.duration * width)
            mark_x = min(start_x, end_x)
            mark_width = abs(end_x - start_x)

            painter.fillRect(
                mark_x, timeline_y,
                mark_width, timeline_height,
                QColor('#00FF00', 128)
            )

        # Draw playhead
        if self.duration > 0:
            playhead_x = int(self.position / self.duration * width)

            # Playhead line
            pen = QPen(QColor('#FFFFFF'))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(playhead_x, 0, playhead_x, height)

            # Playhead triangle
            painter.setBrush(QColor('#FFFFFF'))
            points = [
                (playhead_x - 5, 0),
                (playhead_x + 5, 0),
                (playhead_x, 10)
            ]
            from PyQt6.QtCore import QPointF
            painter.drawPolygon([QPointF(x, y) for x, y in points])

        # Time markers every 10 seconds
        painter.setPen(QColor('#808080'))
        for seconds in range(0, int(self.duration / 1000) + 1, 10):
            x = int((seconds * 1000) / self.duration * width)
            painter.drawLine(x, height - 15, x, height - 5)
            painter.drawText(x - 20, height - 18, 40, 15,
                           Qt.AlignmentFlag.AlignCenter,
                           f"{seconds}s")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click to seek."""
        if self.duration > 0:
            position_ms = int(event.position().x() / self.width() * self.duration)
            self.seek_requested.emit(position_ms)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse drag to scrub."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.duration > 0:
                position_ms = int(event.position().x() / self.width() * self.duration)
                self.seek_requested.emit(position_ms)


class VideoPlayer(QWidget):
    """
    Video player widget with full controls.

    Features:
    - Video playback with Qt multimedia
    - Timeline scrubbing
    - Segment marking
    - Playback controls
    - Volume control
    """

    # Signals
    video_loaded = pyqtSignal(str)
    playback_state_changed = pyqtSignal(bool)  # True = playing
    segment_marked = pyqtSignal(int, int)  # start_ms, end_ms
    position_changed = pyqtSignal(int)  # position in ms

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_file: Optional[str] = None
        self.is_marking_segment = False

        # Media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Connect signals
        self.media_player.positionChanged.connect(self._on_position_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.media_player.playbackStateChanged.connect(self._on_playback_state_changed)

        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Video display
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.video_widget)

        # Timeline
        self.timeline = TimelineWidget()
        self.timeline.seek_requested.connect(self._on_seek_requested)
        self.timeline.segment_added.connect(self._on_segment_added)
        layout.addWidget(self.timeline)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(8, 4, 8, 4)
        controls_layout.setSpacing(8)

        # Play/Pause button
        self.play_btn = QPushButton()
        self.play_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_btn)

        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        )
        self.stop_btn.setFixedSize(36, 36)
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)

        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(120)
        controls_layout.addWidget(self.time_label)

        controls_layout.addStretch()

        # Segment marking buttons
        self.mark_start_btn = QPushButton("[ Mark Start")
        self.mark_start_btn.setToolTip("Mark segment start point")
        self.mark_start_btn.clicked.connect(self._mark_start)
        controls_layout.addWidget(self.mark_start_btn)

        self.mark_end_btn = QPushButton("Mark End ]")
        self.mark_end_btn.setToolTip("Mark segment end point")
        self.mark_end_btn.clicked.connect(self._mark_end)
        self.mark_end_btn.setEnabled(False)
        controls_layout.addWidget(self.mark_end_btn)

        self.clear_segments_btn = QPushButton("Clear Segments")
        self.clear_segments_btn.clicked.connect(self._clear_segments)
        controls_layout.addWidget(self.clear_segments_btn)

        controls_layout.addSpacing(20)

        # Volume control
        volume_label = QLabel("Volume:")
        controls_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        controls_layout.addWidget(self.volume_slider)

        layout.addLayout(controls_layout)

    def load_video(self, file_path: str) -> bool:
        """
        Load a video file.

        Args:
            file_path: Path to video file

        Returns:
            True if successful
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False

            # Load video
            self.media_player.setSource(QUrl.fromLocalFile(str(path)))
            self.current_file = file_path

            # Clear segments
            self.timeline.clear_segments()

            self.video_loaded.emit(file_path)
            return True

        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def play(self):
        """Start playback."""
        self.media_player.play()

    def pause(self):
        """Pause playback."""
        self.media_player.pause()

    def stop(self):
        """Stop playback."""
        self.media_player.stop()

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def seek(self, position_ms: int):
        """Seek to position in milliseconds."""
        self.media_player.setPosition(position_ms)

    def get_position(self) -> int:
        """Get current position in milliseconds."""
        return self.media_player.position()

    def get_duration(self) -> int:
        """Get total duration in milliseconds."""
        return self.media_player.duration()

    def get_segments(self) -> List[Tuple[int, int]]:
        """Get all marked segments."""
        return self.timeline.segments.copy()

    def _on_position_changed(self, position_ms: int):
        """Handle position change."""
        self.timeline.set_position(position_ms)

        # Update time label
        current = self._format_time(position_ms)
        total = self._format_time(self.media_player.duration())
        self.time_label.setText(f"{current} / {total}")

        self.position_changed.emit(position_ms)

    def _on_duration_changed(self, duration_ms: int):
        """Handle duration change."""
        self.timeline.set_duration(duration_ms)

    def _on_playback_state_changed(self, state):
        """Handle playback state change."""
        is_playing = state == QMediaPlayer.PlaybackState.PlayingState

        # Update play button icon
        if is_playing:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

        self.playback_state_changed.emit(is_playing)

    def _on_seek_requested(self, position_ms: int):
        """Handle seek request from timeline."""
        self.seek(position_ms)

    def _on_segment_added(self, start_ms: int, end_ms: int):
        """Handle segment added from timeline."""
        self.segment_marked.emit(start_ms, end_ms)

    def _on_volume_changed(self, value: int):
        """Handle volume change."""
        self.audio_output.setVolume(value / 100.0)

    def _mark_start(self):
        """Mark segment start."""
        self.timeline.start_marking()
        self.is_marking_segment = True
        self.mark_start_btn.setEnabled(False)
        self.mark_end_btn.setEnabled(True)

    def _mark_end(self):
        """Mark segment end."""
        self.timeline.finish_marking()
        self.is_marking_segment = False
        self.mark_start_btn.setEnabled(True)
        self.mark_end_btn.setEnabled(False)

    def _clear_segments(self):
        """Clear all segments."""
        self.timeline.clear_segments()

    def _format_time(self, ms: int) -> str:
        """Format milliseconds as MM:SS."""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_current_file(self) -> Optional[str]:
        """Get currently loaded file path."""
        return self.current_file
