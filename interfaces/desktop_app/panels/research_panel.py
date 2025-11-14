"""
Research Mode Panel

PDF viewing and citation management for research work.
"""

import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMessageBox, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from interfaces.desktop_app.widgets import PDFViewer


class ResearchPanel(QWidget):
    """
    Research mode workspace panel.

    Features:
    - PDF viewer
    - Citation extraction
    - Bibliography sidebar (optional)
    - Quick actions for research tasks
    """

    # Signals
    citation_extracted = pyqtSignal(dict)  # citation data
    note_created = pyqtSignal(str)  # note content
    summarize_requested = pyqtSignal(str)  # text to summarize

    def __init__(self, orchestrator=None, parent=None):
        super().__init__(parent)

        self.orchestrator = orchestrator
        self.current_file = None

        # Check for citation manager
        self.citation_manager = None
        if orchestrator and hasattr(orchestrator, 'agents'):
            gamma_agent = orchestrator.agents.get('gamma')
            if gamma_agent and hasattr(gamma_agent, 'citation_manager'):
                self.citation_manager = gamma_agent.citation_manager

        self._create_ui()

    def _create_ui(self):
        """Create the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Quick actions toolbar
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(8, 4, 8, 4)
        actions_layout.setSpacing(8)

        self.extract_citation_btn = QPushButton("📚 Extract Citation")
        self.extract_citation_btn.setProperty("primary", True)
        self.extract_citation_btn.clicked.connect(self._extract_citation)
        self.extract_citation_btn.setEnabled(False)
        actions_layout.addWidget(self.extract_citation_btn)

        self.create_note_btn = QPushButton("📝 Create Note")
        self.create_note_btn.clicked.connect(self._create_note)
        self.create_note_btn.setEnabled(False)
        actions_layout.addWidget(self.create_note_btn)

        self.summarize_btn = QPushButton("✨ Summarize Page")
        self.summarize_btn.clicked.connect(self._summarize_page)
        self.summarize_btn.setEnabled(False)
        actions_layout.addWidget(self.summarize_btn)

        self.search_related_btn = QPushButton("🔍 Search Related Papers")
        self.search_related_btn.clicked.connect(self._search_related)
        self.search_related_btn.setEnabled(False)
        actions_layout.addWidget(self.search_related_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # PDF viewer
        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.document_loaded.connect(self._on_document_loaded)
        layout.addWidget(self.pdf_viewer)

    def load_pdf(self, file_path: str) -> bool:
        """
        Load a PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            True if successful
        """
        success = self.pdf_viewer.load_pdf(file_path)
        if success:
            self.current_file = file_path
        return success

    def _on_document_loaded(self, file_path: str):
        """Handle document loaded."""
        self.current_file = file_path

        # Enable actions
        self.extract_citation_btn.setEnabled(True)
        self.create_note_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)
        self.search_related_btn.setEnabled(True)

    def _extract_citation(self):
        """Extract citation from PDF."""
        if not self.current_file:
            return

        if not self.citation_manager:
            QMessageBox.warning(
                self,
                "Citation Manager Not Available",
                "Citation manager is not initialized. Make sure Gamma agent is loaded."
            )
            return

        try:
            # Extract citation using citation manager
            citation = self.citation_manager.extract_from_pdf(Path(self.current_file))

            if citation:
                # Show citation info
                citation_text = f"""
                <h3>Citation Extracted</h3>
                <p><b>Title:</b> {citation.title}</p>
                <p><b>Authors:</b> {', '.join(citation.authors)}</p>
                <p><b>Year:</b> {citation.year or 'Unknown'}</p>
                <p><b>DOI:</b> {citation.doi or 'Not found'}</p>
                <p><b>Citation Key:</b> {citation.cite_key}</p>
                <hr>
                <h4>BibTeX:</h4>
                <pre>{citation.to_bibtex()}</pre>
                <hr>
                <h4>APA:</h4>
                <p>{citation.to_apa()}</p>
                """

                QMessageBox.information(
                    self,
                    "Citation Extracted",
                    citation_text
                )

                # Emit signal
                self.citation_extracted.emit({
                    'title': citation.title,
                    'authors': citation.authors,
                    'year': citation.year,
                    'doi': citation.doi,
                    'cite_key': citation.cite_key
                })
            else:
                QMessageBox.warning(
                    self,
                    "Citation Extraction Failed",
                    "Could not extract citation from PDF. Try manually adding citation information."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error extracting citation:\n{str(e)}"
            )

    def _create_note(self):
        """Create note from PDF."""
        if not self.current_file:
            return

        # Get current page text
        text = self.pdf_viewer.get_text()

        if text:
            # Get metadata
            metadata = self.pdf_viewer.get_metadata()
            title = metadata.get('title', Path(self.current_file).stem)

            # Create note content
            note_content = f"# Note: {title}\n\n"
            note_content += f"Source: {Path(self.current_file).name}\n"
            note_content += f"Page: {self.pdf_viewer.current_page + 1}\n\n"
            note_content += "## Content\n\n"
            note_content += text[:500] + "..." if len(text) > 500 else text

            # Emit signal
            self.note_created.emit(note_content)

            QMessageBox.information(
                self,
                "Note Created",
                "Note created from current page. Check Notes panel."
            )
        else:
            QMessageBox.warning(
                self,
                "No Text",
                "Could not extract text from current page."
            )

    def _summarize_page(self):
        """Request summary of current page."""
        if not self.current_file:
            return

        text = self.pdf_viewer.get_text()

        if text:
            # Emit signal for agent to summarize
            self.summarize_requested.emit(text)
        else:
            QMessageBox.warning(
                self,
                "No Text",
                "Could not extract text from current page."
            )

    def _search_related(self):
        """Search for related papers."""
        if not self.current_file:
            return

        # Get document metadata
        metadata = self.pdf_viewer.get_metadata()
        title = metadata.get('title', '')

        if title:
            # Use title as search query
            search_query = title
        else:
            # Get first few words from first page
            text = self.pdf_viewer.get_text()
            words = text.split()[:10]
            search_query = ' '.join(words)

        if search_query:
            QMessageBox.information(
                self,
                "Search Papers",
                f"Searching for papers related to:\n\n{search_query}\n\n"
                "This will be implemented with Beta agent integration."
            )
        else:
            QMessageBox.warning(
                self,
                "No Query",
                "Could not determine search query from PDF."
            )

    def get_current_file(self) -> Optional[str]:
        """Get currently loaded file path."""
        return self.current_file


class SimplePDFPanel(QWidget):
    """
    Simple PDF panel with just viewer and basic actions.
    Lighter weight version of ResearchPanel.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_file = None
        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # PDF viewer
        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.document_loaded.connect(self._on_document_loaded)
        layout.addWidget(self.pdf_viewer)

    def load_pdf(self, file_path: str) -> bool:
        """Load PDF."""
        success = self.pdf_viewer.load_pdf(file_path)
        if success:
            self.current_file = file_path
        return success

    def _on_document_loaded(self, file_path: str):
        """Handle document loaded."""
        self.current_file = file_path
