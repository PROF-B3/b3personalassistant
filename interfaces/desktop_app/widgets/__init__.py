"""Desktop app widgets"""

from .pdf_viewer import PDFViewer
from .markdown_editor import MarkdownEditor, MarkdownPreview, MarkdownEditorWithPreview

# Video player is optional (requires PyQt6-Multimedia, not available for Python 3.13)
try:
    from .video_player import VideoPlayer, TimelineWidget
    __all__ = ['PDFViewer', 'MarkdownEditor', 'MarkdownPreview', 'MarkdownEditorWithPreview', 'VideoPlayer', 'TimelineWidget']
except ImportError:
    __all__ = ['PDFViewer', 'MarkdownEditor', 'MarkdownPreview', 'MarkdownEditorWithPreview']
