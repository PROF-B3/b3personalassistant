"""
PDF Viewer Widget

View and navigate PDF documents with PyMuPDF.
"""

import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QSlider, QSpinBox, QToolBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QPixmap, QPainter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class PDFViewer(QWidget):
    """
    PDF viewer widget using PyMuPDF.

    Features:
    - View PDF pages
    - Navigate pages (prev/next, jump to page)
    - Zoom in/out
    - Scroll through document
    - Extract text and metadata
    """

    # Signals
    page_changed = pyqtSignal(int)  # current page number
    document_loaded = pyqtSignal(str)  # file path
    text_selected = pyqtSignal(str)  # selected text

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.file_path = None

        # Check if PyMuPDF is available
        self.pymupdf_available = self._check_pymupdf()

        self._create_ui()

    def _check_pymupdf(self) -> bool:
        """Check if PyMuPDF (fitz) is available."""
        try:
            import fitz
            return True
        except ImportError:
            return False

    def _create_ui(self):
        """Create the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Navigation buttons
        self.prev_button = QPushButton("← Prev")
        self.prev_button.clicked.connect(self._prev_page)
        toolbar.addWidget(self.prev_button)

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self._next_page)
        toolbar.addWidget(self.next_button)

        toolbar.addSeparator()

        # Page selector
        toolbar.addWidget(QLabel("Page:"))
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.valueChanged.connect(self._jump_to_page)
        self.page_spinbox.setMaximumWidth(80)
        toolbar.addWidget(self.page_spinbox)

        self.page_label = QLabel("/ 0")
        toolbar.addWidget(self.page_label)

        toolbar.addSeparator()

        # Zoom controls
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.clicked.connect(self._zoom_out)
        self.zoom_out_button.setMaximumWidth(30)
        toolbar.addWidget(self.zoom_out_button)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)  # 50%
        self.zoom_slider.setMaximum(200)  # 200%
        self.zoom_slider.setValue(100)  # 100%
        self.zoom_slider.setMaximumWidth(150)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self.zoom_slider)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(self._zoom_in)
        self.zoom_in_button.setMaximumWidth(30)
        toolbar.addWidget(self.zoom_in_button)

        self.zoom_label = QLabel("100%")
        toolbar.addWidget(self.zoom_label)

        layout.addWidget(toolbar)

        # PDF display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        if not self.pymupdf_available:
            self.pdf_label.setText(
                "PyMuPDF not installed\n\n"
                "Install with: pip install PyMuPDF\n\n"
                "This will enable PDF viewing."
            )
            self.pdf_label.setStyleSheet("color: #858585; font-size: 14px; padding: 40px;")

        self.scroll_area.setWidget(self.pdf_label)
        layout.addWidget(self.scroll_area)

        # Disable controls initially
        self._set_controls_enabled(False)

    def load_pdf(self, file_path: str) -> bool:
        """
        Load a PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            True if successful, False otherwise
        """
        if not self.pymupdf_available:
            return False

        try:
            import fitz

            # Open PDF
            self.pdf_document = fitz.open(file_path)
            self.file_path = file_path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0

            # Update UI
            self.page_spinbox.setMaximum(self.total_pages)
            self.page_spinbox.setValue(1)
            self.page_label.setText(f"/ {self.total_pages}")

            # Enable controls
            self._set_controls_enabled(True)

            # Render first page
            self._render_page()

            # Emit signal
            self.document_loaded.emit(file_path)

            return True

        except Exception as e:
            self.pdf_label.setText(f"Error loading PDF:\n{str(e)}")
            return False

    def _render_page(self):
        """Render the current PDF page."""
        if not self.pdf_document or self.current_page >= self.total_pages:
            return

        try:
            import fitz

            # Get page
            page = self.pdf_document[self.current_page]

            # Calculate zoom matrix
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)

            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert to QImage
            img = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888
            )

            # Display
            pixmap = QPixmap.fromImage(img)
            self.pdf_label.setPixmap(pixmap)
            self.pdf_label.resize(pixmap.size())

            # Update page indicator
            self.page_spinbox.blockSignals(True)
            self.page_spinbox.setValue(self.current_page + 1)
            self.page_spinbox.blockSignals(False)

            # Emit signal
            self.page_changed.emit(self.current_page)

        except Exception as e:
            self.pdf_label.setText(f"Error rendering page:\n{str(e)}")

    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_page()

    def _jump_to_page(self, page_num: int):
        """Jump to specific page (1-indexed)."""
        page_index = page_num - 1
        if 0 <= page_index < self.total_pages:
            self.current_page = page_index
            self._render_page()

    def _zoom_in(self):
        """Zoom in."""
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(min(current + 10, 200))

    def _zoom_out(self):
        """Zoom out."""
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(max(current - 10, 50))

    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_level = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self._render_page()

    def _set_controls_enabled(self, enabled: bool):
        """Enable/disable navigation controls."""
        self.prev_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.page_spinbox.setEnabled(enabled)
        self.zoom_slider.setEnabled(enabled)
        self.zoom_in_button.setEnabled(enabled)
        self.zoom_out_button.setEnabled(enabled)

    def get_text(self, page_num: Optional[int] = None) -> str:
        """
        Get text from page.

        Args:
            page_num: Page number (0-indexed), or current page if None

        Returns:
            Extracted text
        """
        if not self.pdf_document:
            return ""

        try:
            page_index = page_num if page_num is not None else self.current_page
            if 0 <= page_index < self.total_pages:
                page = self.pdf_document[page_index]
                return page.get_text()
        except Exception:
            pass

        return ""

    def get_all_text(self) -> str:
        """Get text from all pages."""
        if not self.pdf_document:
            return ""

        try:
            text_parts = []
            for page_num in range(self.total_pages):
                page = self.pdf_document[page_num]
                text_parts.append(page.get_text())
            return "\n\n".join(text_parts)
        except Exception:
            return ""

    def get_metadata(self) -> dict:
        """Get PDF metadata."""
        if not self.pdf_document:
            return {}

        try:
            return self.pdf_document.metadata
        except Exception:
            return {}

    def search_text(self, query: str, case_sensitive: bool = False) -> list:
        """
        Search for text in PDF.

        Args:
            query: Search query
            case_sensitive: Case sensitive search

        Returns:
            List of (page_num, rectangles) tuples
        """
        if not self.pdf_document:
            return []

        results = []
        try:
            for page_num in range(self.total_pages):
                page = self.pdf_document[page_num]
                rects = page.search_for(query)
                if rects:
                    results.append((page_num, rects))
        except Exception:
            pass

        return results

    def close_document(self):
        """Close the current PDF document."""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
            self.current_page = 0
            self.total_pages = 0
            self.file_path = None

            self.pdf_label.clear()
            self.pdf_label.setText("No PDF loaded")
            self._set_controls_enabled(False)


class PDFViewerWithInfo(QWidget):
    """
    PDF viewer with info panel showing metadata and quick actions.
    """

    # Signals
    extract_citation_clicked = pyqtSignal()
    create_note_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pdf_viewer = PDFViewer()
        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Quick actions bar
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(8, 4, 8, 4)

        self.extract_citation_btn = QPushButton("📚 Extract Citation")
        self.extract_citation_btn.clicked.connect(self.extract_citation_clicked.emit)
        actions_layout.addWidget(self.extract_citation_btn)

        self.create_note_btn = QPushButton("📝 Create Note")
        self.create_note_btn.clicked.connect(self.create_note_clicked.emit)
        actions_layout.addWidget(self.create_note_btn)

        self.summarize_btn = QPushButton("✨ Summarize")
        actions_layout.addWidget(self.summarize_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # PDF viewer
        layout.addWidget(self.pdf_viewer)

    def load_pdf(self, file_path: str) -> bool:
        """Load PDF."""
        return self.pdf_viewer.load_pdf(file_path)

    def get_metadata(self) -> dict:
        """Get PDF metadata."""
        return self.pdf_viewer.get_metadata()

    def get_text(self) -> str:
        """Get current page text."""
        return self.pdf_viewer.get_text()

    def get_all_text(self) -> str:
        """Get all text."""
        return self.pdf_viewer.get_all_text()
