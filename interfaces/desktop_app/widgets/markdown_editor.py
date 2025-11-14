"""
Markdown Editor Widget

Syntax-highlighted Markdown editor with live preview.
"""

import re
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QTextBrowser, QSplitter, QLabel, QPushButton, QToolBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QTextCharFormat, QColor, QFont, QSyntaxHighlighter,
    QTextCursor
)


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Define formats
        self.formats = {}

        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#4A9EFF"))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.formats['header'] = header_format

        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        bold_format.setForeground(QColor("#CCCCCC"))
        self.formats['bold'] = bold_format

        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        italic_format.setForeground(QColor("#CCCCCC"))
        self.formats['italic'] = italic_format

        # Code
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#CE9178"))
        code_format.setFontFamily("Consolas, Monaco, monospace")
        self.formats['code'] = code_format

        # Link
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#4EC9B0"))
        link_format.setFontUnderline(True)
        self.formats['link'] = link_format

        # Citation
        citation_format = QTextCharFormat()
        citation_format.setForeground(QColor("#FFA500"))
        self.formats['citation'] = citation_format

        # Quote
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#858585"))
        quote_format.setFontItalic(True)
        self.formats['quote'] = quote_format

        # List
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#4A9EFF"))
        self.formats['list'] = list_format

    def highlightBlock(self, text):
        """Highlight a block of text."""
        # Headers
        if re.match(r'^#{1,6}\s', text):
            self.setFormat(0, len(text), self.formats['header'])
            return

        # Quote
        if text.startswith('>'):
            self.setFormat(0, len(text), self.formats['quote'])
            return

        # List
        if re.match(r'^\s*[-*+]\s', text) or re.match(r'^\s*\d+\.\s', text):
            match = re.match(r'^(\s*[-*+\d.]+\s)', text)
            if match:
                self.setFormat(0, len(match.group(1)), self.formats['list'])

        # Bold
        for match in re.finditer(r'\*\*(.+?)\*\*|__(.+?)__', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats['bold'])

        # Italic
        for match in re.finditer(r'\*(.+?)\*|_(.+?)_', text):
            # Skip if part of bold
            if text[max(0, match.start()-1):match.start()] != '*' and \
               text[match.end():min(len(text), match.end()+1)] != '*':
                self.setFormat(match.start(), match.end() - match.start(), self.formats['italic'])

        # Code
        for match in re.finditer(r'`([^`]+)`', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats['code'])

        # Links
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats['link'])

        # Citations
        for match in re.finditer(r'@[\w\d]+', text):
            self.setFormat(match.start(), match.end() - match.start(), self.formats['citation'])


class MarkdownEditor(QPlainTextEdit):
    """
    Markdown editor with syntax highlighting.

    Features:
    - Syntax highlighting
    - Auto-indentation
    - Tab support
    - Line numbers (optional)
    """

    text_changed_delayed = pyqtSignal()  # Emitted after typing stops

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set font
        font = QFont("Consolas, Monaco, Courier New, monospace", 11)
        self.setFont(font)

        # Set tab width to 4 spaces
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

        # Enable syntax highlighting
        self.highlighter = MarkdownHighlighter(self.document())

        # Delayed text changed signal (for live preview)
        self.change_timer = QTimer()
        self.change_timer.setInterval(500)  # 500ms delay
        self.change_timer.setSingleShot(True)
        self.change_timer.timeout.connect(self.text_changed_delayed.emit)
        self.textChanged.connect(self.change_timer.start)

    def insert_bold(self):
        """Insert bold formatting."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"**{text}**")
        else:
            cursor.insertText("****")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 2)
            self.setTextCursor(cursor)

    def insert_italic(self):
        """Insert italic formatting."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"*{text}*")
        else:
            cursor.insertText("**")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 1)
            self.setTextCursor(cursor)

    def insert_link(self):
        """Insert link."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"[{text}](url)")
        else:
            cursor.insertText("[text](url)")

    def insert_code(self):
        """Insert inline code."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"`{text}`")
        else:
            cursor.insertText("``")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 1)
            self.setTextCursor(cursor)

    def insert_heading(self, level: int = 1):
        """Insert heading."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText("#" * level + " ")

    def insert_citation(self, cite_key: str):
        """Insert citation reference."""
        cursor = self.textCursor()
        cursor.insertText(f"@{cite_key}")

    def get_word_count(self) -> int:
        """Get word count."""
        text = self.toPlainText()
        words = text.split()
        return len(words)

    def get_character_count(self) -> int:
        """Get character count."""
        return len(self.toPlainText())


class MarkdownPreview(QTextBrowser):
    """
    Markdown preview widget.

    Displays rendered Markdown HTML.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable links
        self.setOpenExternalLinks(True)

        # Set default content
        self.setHtml("<p style='color: #858585;'>Preview will appear here...</p>")

    def update_preview(self, markdown_text: str):
        """
        Update preview with rendered Markdown.

        Args:
            markdown_text: Markdown source text
        """
        try:
            # Try to use markdown library
            import markdown
            html = markdown.markdown(
                markdown_text,
                extensions=['extra', 'codehilite', 'tables', 'toc']
            )

            # Wrap in styled HTML
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #CCCCCC;
                        padding: 20px;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #4A9EFF;
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #3E3E42; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #3E3E42; padding-bottom: 0.3em; }}
                    h3 {{ font-size: 1.25em; }}
                    code {{
                        background-color: #2D2D2D;
                        color: #CE9178;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: Consolas, Monaco, monospace;
                    }}
                    pre {{
                        background-color: #2D2D2D;
                        padding: 16px;
                        border-radius: 6px;
                        overflow-x: auto;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    blockquote {{
                        border-left: 4px solid #4A9EFF;
                        margin: 0;
                        padding-left: 16px;
                        color: #858585;
                        font-style: italic;
                    }}
                    a {{
                        color: #4EC9B0;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                    }}
                    th, td {{
                        border: 1px solid #3E3E42;
                        padding: 8px 12px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #2D2D2D;
                        font-weight: 600;
                    }}
                    ul, ol {{
                        padding-left: 24px;
                    }}
                    li {{
                        margin: 4px 0;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """

            self.setHtml(styled_html)

        except ImportError:
            # Fallback if markdown library not available
            # Simple conversion
            html = self._simple_markdown_to_html(markdown_text)
            self.setHtml(html)

    def _simple_markdown_to_html(self, text: str) -> str:
        """Simple Markdown to HTML conversion (fallback)."""
        html = text

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Paragraphs
        html = '<p>' + html.replace('\n\n', '</p><p>') + '</p>'

        return f"<div style='color: #CCCCCC; padding: 20px;'>{html}</div>"


class MarkdownEditorWithPreview(QWidget):
    """
    Markdown editor with side-by-side live preview.

    Features:
    - Split view (editor | preview)
    - Toolbar with formatting buttons
    - Auto-updating preview
    - Word count display
    """

    text_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._create_ui()
        self._connect_signals()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Formatting buttons
        self.bold_btn = QPushButton("B")
        self.bold_btn.setToolTip("Bold (Ctrl+B)")
        self.bold_btn.setMaximumWidth(30)
        self.bold_btn.setStyleSheet("font-weight: bold;")
        self.bold_btn.clicked.connect(self._insert_bold)
        toolbar.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        self.italic_btn.setToolTip("Italic (Ctrl+I)")
        self.italic_btn.setMaximumWidth(30)
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.clicked.connect(self._insert_italic)
        toolbar.addWidget(self.italic_btn)

        self.code_btn = QPushButton("<>")
        self.code_btn.setToolTip("Code")
        self.code_btn.setMaximumWidth(30)
        self.code_btn.clicked.connect(self._insert_code)
        toolbar.addWidget(self.code_btn)

        self.link_btn = QPushButton("🔗")
        self.link_btn.setToolTip("Link")
        self.link_btn.setMaximumWidth(30)
        self.link_btn.clicked.connect(self._insert_link)
        toolbar.addWidget(self.link_btn)

        toolbar.addSeparator()

        self.h1_btn = QPushButton("H1")
        self.h1_btn.setToolTip("Heading 1")
        self.h1_btn.setMaximumWidth(35)
        self.h1_btn.clicked.connect(lambda: self._insert_heading(1))
        toolbar.addWidget(self.h1_btn)

        self.h2_btn = QPushButton("H2")
        self.h2_btn.setToolTip("Heading 2")
        self.h2_btn.setMaximumWidth(35)
        self.h2_btn.clicked.connect(lambda: self._insert_heading(2))
        toolbar.addWidget(self.h2_btn)

        self.h3_btn = QPushButton("H3")
        self.h3_btn.setToolTip("Heading 3")
        self.h3_btn.setMaximumWidth(35)
        self.h3_btn.clicked.connect(lambda: self._insert_heading(3))
        toolbar.addWidget(self.h3_btn)

        toolbar.addSeparator()

        # Word count
        self.word_count_label = QLabel("Words: 0 | Characters: 0")
        toolbar.addWidget(self.word_count_label)

        toolbar.addSeparator()

        # Preview toggle
        self.preview_toggle_btn = QPushButton("Hide Preview")
        self.preview_toggle_btn.clicked.connect(self._toggle_preview)
        toolbar.addWidget(self.preview_toggle_btn)

        layout.addWidget(toolbar)

        # Editor and preview (split view)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.editor = MarkdownEditor()
        self.splitter.addWidget(self.editor)

        self.preview = MarkdownPreview()
        self.splitter.addWidget(self.preview)

        # Set equal sizes
        self.splitter.setSizes([500, 500])

        layout.addWidget(self.splitter)

    def _connect_signals(self):
        """Connect signals."""
        self.editor.text_changed_delayed.connect(self._update_preview)
        self.editor.text_changed_delayed.connect(self._update_word_count)
        self.editor.textChanged.connect(self.text_changed.emit)

    def _insert_bold(self):
        """Insert bold."""
        self.editor.insert_bold()

    def _insert_italic(self):
        """Insert italic."""
        self.editor.insert_italic()

    def _insert_code(self):
        """Insert code."""
        self.editor.insert_code()

    def _insert_link(self):
        """Insert link."""
        self.editor.insert_link()

    def _insert_heading(self, level: int):
        """Insert heading."""
        self.editor.insert_heading(level)

    def _update_preview(self):
        """Update preview."""
        text = self.editor.toPlainText()
        self.preview.update_preview(text)

    def _update_word_count(self):
        """Update word count display."""
        words = self.editor.get_word_count()
        chars = self.editor.get_character_count()
        self.word_count_label.setText(f"Words: {words} | Characters: {chars}")

    def _toggle_preview(self):
        """Toggle preview visibility."""
        if self.preview.isVisible():
            self.preview.hide()
            self.preview_toggle_btn.setText("Show Preview")
        else:
            self.preview.show()
            self.preview_toggle_btn.setText("Hide Preview")
            self._update_preview()

    def get_text(self) -> str:
        """Get editor text."""
        return self.editor.toPlainText()

    def set_text(self, text: str):
        """Set editor text."""
        self.editor.setPlainText(text)
        self._update_preview()
        self._update_word_count()

    def insert_citation(self, cite_key: str):
        """Insert citation."""
        self.editor.insert_citation(cite_key)

    def get_word_count(self) -> int:
        """Get word count."""
        return self.editor.get_word_count()
