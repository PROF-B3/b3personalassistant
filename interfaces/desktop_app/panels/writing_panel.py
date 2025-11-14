"""
Writing Mode Panel

Markdown editor with live preview and export for writing work.
"""

import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import pyqtSignal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from interfaces.desktop_app.widgets.markdown_editor import MarkdownEditorWithPreview


class WritingPanel(QWidget):
    """
    Writing mode workspace panel.

    Features:
    - Markdown editor with live preview
    - Citation insertion
    - Export to Word/LaTeX
    - Writing assistance from AI
    - Word count tracking
    """

    # Signals
    citation_insert_requested = pyqtSignal()
    export_requested = pyqtSignal(str, str)  # format, content
    writing_help_requested = pyqtSignal(str)  # text to improve

    def __init__(self, orchestrator=None, parent=None):
        super().__init__(parent)

        self.orchestrator = orchestrator
        self.current_file = None
        self.is_modified = False

        # Check for document exporter
        self.doc_exporter = None
        if orchestrator and hasattr(orchestrator, 'agents'):
            epsilon_agent = orchestrator.agents.get('epsilon')
            if epsilon_agent and hasattr(epsilon_agent, 'doc_exporter'):
                self.doc_exporter = epsilon_agent.doc_exporter

        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Quick actions toolbar
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(8, 4, 8, 4)
        actions_layout.setSpacing(8)

        self.insert_citation_btn = QPushButton("[@] Insert Citation")
        self.insert_citation_btn.setToolTip("Insert citation from bibliography (Ctrl+@)")
        self.insert_citation_btn.clicked.connect(self._insert_citation)
        actions_layout.addWidget(self.insert_citation_btn)

        self.improve_text_btn = QPushButton("✨ Improve Writing")
        self.improve_text_btn.setToolTip("Get AI suggestions to improve selected text")
        self.improve_text_btn.clicked.connect(self._improve_writing)
        actions_layout.addWidget(self.improve_text_btn)

        self.generate_bib_btn = QPushButton("📚 Generate Bibliography")
        self.generate_bib_btn.setToolTip("Generate bibliography section")
        self.generate_bib_btn.clicked.connect(self._generate_bibliography)
        actions_layout.addWidget(self.generate_bib_btn)

        self.export_word_btn = QPushButton("📄 Export to Word")
        self.export_word_btn.setProperty("primary", True)
        self.export_word_btn.clicked.connect(lambda: self._export("word"))
        actions_layout.addWidget(self.export_word_btn)

        self.export_latex_btn = QPushButton("📝 Export to LaTeX")
        self.export_latex_btn.clicked.connect(lambda: self._export("latex"))
        actions_layout.addWidget(self.export_latex_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # Markdown editor with preview
        self.editor = MarkdownEditorWithPreview()
        self.editor.text_changed.connect(self._on_text_changed)
        layout.addWidget(self.editor)

    def load_file(self, file_path: str) -> bool:
        """
        Load a Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.editor.set_text(content)
            self.current_file = file_path
            self.is_modified = False

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Could not load file:\n{str(e)}"
            )
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save current content to file.

        Args:
            file_path: Path to save to (uses current_file if None)

        Returns:
            True if successful
        """
        if file_path is None:
            file_path = self.current_file

        if not file_path:
            return False

        try:
            content = self.editor.get_text()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_path
            self.is_modified = False

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving File",
                f"Could not save file:\n{str(e)}"
            )
            return False

    def _on_text_changed(self):
        """Handle text changed."""
        self.is_modified = True

    def _insert_citation(self):
        """Insert citation."""
        # Get citation key from user
        cite_key, ok = QInputDialog.getText(
            self,
            "Insert Citation",
            "Enter citation key (e.g., Smith2023):"
        )

        if ok and cite_key:
            self.editor.insert_citation(cite_key)

        # Emit signal for more advanced citation browser
        self.citation_insert_requested.emit()

    def _improve_writing(self):
        """Request writing improvement from AI."""
        # Get selected text or current paragraph
        cursor = self.editor.editor.textCursor()

        if cursor.hasSelection():
            text = cursor.selectedText()
        else:
            # Get current block
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            text = cursor.selectedText()

        if text:
            self.writing_help_requested.emit(text)
        else:
            QMessageBox.information(
                self,
                "Improve Writing",
                "Select text to improve, or place cursor in a paragraph."
            )

    def _generate_bibliography(self):
        """Generate bibliography section."""
        if not self.orchestrator:
            QMessageBox.warning(
                self,
                "Not Available",
                "Bibliography generation requires Gamma agent."
            )
            return

        # Get Gamma agent
        gamma_agent = self.orchestrator.agents.get('gamma')
        if not gamma_agent or not hasattr(gamma_agent, 'citation_manager'):
            QMessageBox.warning(
                self,
                "Not Available",
                "Citation manager not available."
            )
            return

        try:
            # Generate bibliography
            citation_manager = gamma_agent.citation_manager
            bibliography = citation_manager.generate_bibliography(style='apa')

            if bibliography:
                # Insert at end of document
                current_text = self.editor.get_text()
                new_text = current_text + "\n\n## References\n\n" + bibliography
                self.editor.set_text(new_text)

                QMessageBox.information(
                    self,
                    "Bibliography Generated",
                    "Bibliography has been added to the end of your document."
                )
            else:
                QMessageBox.information(
                    self,
                    "No Citations",
                    "No citations found in bibliography. Extract citations from PDFs first."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not generate bibliography:\n{str(e)}"
            )

    def _export(self, format_type: str):
        """
        Export document.

        Args:
            format_type: 'word' or 'latex'
        """
        if not self.doc_exporter:
            QMessageBox.warning(
                self,
                "Export Not Available",
                "Document exporter is not available. Make sure Epsilon agent is loaded."
            )
            return

        # Get output file path
        if format_type == "word":
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export to Word",
                "",
                "Word Documents (*.docx)"
            )
            if not file_path:
                return

            if not file_path.endswith('.docx'):
                file_path += '.docx'

        else:  # latex
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export to LaTeX",
                "",
                "LaTeX Files (*.tex)"
            )
            if not file_path:
                return

            if not file_path.endswith('.tex'):
                file_path += '.tex'

        try:
            content = self.editor.get_text()

            # Get title and author
            title, ok1 = QInputDialog.getText(
                self,
                "Document Title",
                "Enter document title:"
            )

            author, ok2 = QInputDialog.getText(
                self,
                "Document Author",
                "Enter author name:"
            )

            if format_type == "word":
                # Export to Word
                self.doc_exporter.export_to_word(
                    content,
                    Path(file_path),
                    title=title if ok1 else None,
                    author=author if ok2 else None
                )
            else:
                # Export to LaTeX
                self.doc_exporter.export_to_latex(
                    content,
                    Path(file_path),
                    template='article',
                    title=title if ok1 else None,
                    author=author if ok2 else None
                )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Document exported to:\n{file_path}"
            )

            # Emit signal
            self.export_requested.emit(format_type, file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not export document:\n{str(e)}"
            )

    def get_current_file(self) -> Optional[str]:
        """Get currently loaded file path."""
        return self.current_file

    def get_word_count(self) -> int:
        """Get word count."""
        return self.editor.get_word_count()

    def is_document_modified(self) -> bool:
        """Check if document has unsaved changes."""
        return self.is_modified


class SimpleWritingPanel(QWidget):
    """
    Simple writing panel with just editor.
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

        self.editor = MarkdownEditorWithPreview()
        layout.addWidget(self.editor)

    def load_file(self, file_path: str) -> bool:
        """Load file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.editor.set_text(content)
            self.current_file = file_path
            return True

        except Exception:
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save file."""
        if file_path is None:
            file_path = self.current_file

        if not file_path:
            return False

        try:
            content = self.editor.get_text()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_path
            return True

        except Exception:
            return False
