"""
File Tree Panel

Browse project files with drag-and-drop import.
"""

import os
from pathlib import Path
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView,
    QLineEdit, QLabel, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QDir, QModelIndex, pyqtSignal
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFileSystemModel


class FileTreePanel(QWidget):
    """
    File tree panel for browsing project files.

    Features:
    - Tree view of project directory
    - Search/filter files
    - Drag-and-drop import
    - Context menu (open, rename, delete)
    - File type icons
    """

    # Signals
    file_selected = pyqtSignal(str)  # file path
    file_opened = pyqtSignal(str)    # double-click
    files_imported = pyqtSignal(list)  # drag-and-drop

    def __init__(self, root_path: Optional[str] = None, parent=None):
        super().__init__(parent)

        self.root_path = root_path or os.getcwd()

        # Enable drag-and-drop
        self.setAcceptDrops(True)

        self._create_ui()
        self._setup_model()

    def _create_ui(self):
        """Create the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QLabel("Files")
        header.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(header)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")
        self.search_box.textChanged.connect(self._filter_files)
        layout.addWidget(self.search_box)

        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)

        # Connect signals
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree_view)

    def _setup_model(self):
        """Setup the file system model."""
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root_path)

        # Set filters
        self.model.setFilter(
            QDir.Filter.AllDirs |
            QDir.Filter.Files |
            QDir.Filter.NoDotAndDotDot
        )

        # Hide certain columns
        self.tree_view.setModel(self.model)
        root_index = self.model.index(self.root_path)
        self.tree_view.setRootIndex(root_index)

        # Hide columns (keep only name)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

    def set_root_path(self, path: str):
        """Set the root directory to display."""
        if os.path.exists(path):
            self.root_path = path
            self.model.setRootPath(path)
            root_index = self.model.index(path)
            self.tree_view.setRootIndex(root_index)
            self.tree_view.expandToDepth(1)

    def _filter_files(self, text: str):
        """Filter files based on search text."""
        if text:
            # Set name filter
            filters = [f"*{text}*"]
            self.model.setNameFilters(filters)
            self.model.setNameFilterDisables(False)
        else:
            # Clear filter
            self.model.setNameFilters([])

    def _on_item_clicked(self, index: QModelIndex):
        """Handle item click."""
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.file_selected.emit(file_path)

    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle item double-click."""
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.file_opened.emit(file_path)

    def _show_context_menu(self, position):
        """Show context menu for file operations."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        is_file = os.path.isfile(file_path)

        menu = QMenu(self)

        # Open action
        if is_file:
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.file_opened.emit(file_path))
            menu.addAction(open_action)

            menu.addSeparator()

        # Rename action
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self._rename_item(index))
        menu.addAction(rename_action)

        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_item(index))
        menu.addAction(delete_action)

        menu.addSeparator()

        # Show in folder action
        show_action = QAction("Show in Folder", self)
        show_action.triggered.connect(lambda: self._show_in_folder(file_path))
        menu.addAction(show_action)

        # Copy path action
        copy_path_action = QAction("Copy Path", self)
        copy_path_action.triggered.connect(lambda: self._copy_path(file_path))
        menu.addAction(copy_path_action)

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _rename_item(self, index: QModelIndex):
        """Rename file or folder."""
        # Enable editing
        self.tree_view.edit(index)

    def _delete_item(self, index: QModelIndex):
        """Delete file or folder."""
        file_path = self.model.filePath(index)
        file_name = os.path.basename(file_path)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{file_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                import shutil
                shutil.rmtree(file_path)

            # Refresh model
            self.model.setRootPath(self.root_path)

    def _show_in_folder(self, file_path: str):
        """Show file in system file manager."""
        import subprocess
        import platform

        folder_path = os.path.dirname(file_path)

        system = platform.system()
        if system == "Windows":
            subprocess.run(["explorer", folder_path])
        elif system == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])

    def _copy_path(self, file_path: str):
        """Copy file path to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)

    def get_selected_file(self) -> Optional[str]:
        """Get currently selected file path."""
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            file_path = self.model.filePath(indexes[0])
            if os.path.isfile(file_path):
                return file_path
        return None

    def expand_all(self):
        """Expand all folders."""
        self.tree_view.expandAll()

    def collapse_all(self):
        """Collapse all folders."""
        self.tree_view.collapseAll()

    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event - import files."""
        urls = event.mimeData().urls()
        file_paths = []

        for url in urls:
            file_path = url.toLocalFile()
            if os.path.exists(file_path):
                file_paths.append(file_path)

        if file_paths:
            self.files_imported.emit(file_paths)
            event.acceptProposedAction()


class ProjectFileTree(FileTreePanel):
    """
    Extended file tree for project structure.

    Creates default project folders if they don't exist:
    - PDFs/
    - Videos/
    - Drafts/
    - Notes/
    - References/
    - Exports/
    """

    def __init__(self, project_path: Optional[str] = None, parent=None):
        # Determine project path
        if project_path is None:
            project_path = os.path.join(os.getcwd(), "B3_Project")

        self.project_path = project_path

        # Create project structure
        self._create_project_structure()

        super().__init__(self.project_path, parent)

        # Expand project root
        self.tree_view.expandToDepth(1)

    def _create_project_structure(self):
        """Create default project folders."""
        folders = [
            "PDFs",
            "Videos",
            "Drafts",
            "Notes",
            "References",
            "Exports"
        ]

        # Create project root
        os.makedirs(self.project_path, exist_ok=True)

        # Create subfolders
        for folder in folders:
            folder_path = os.path.join(self.project_path, folder)
            os.makedirs(folder_path, exist_ok=True)

    def import_file(self, source_path: str) -> str:
        """
        Import file to appropriate project folder based on type.

        Args:
            source_path: Path to file to import

        Returns:
            Destination path where file was copied
        """
        import shutil

        file_name = os.path.basename(source_path)
        suffix = Path(source_path).suffix.lower()

        # Determine destination folder
        if suffix == '.pdf':
            dest_folder = "PDFs"
        elif suffix in ['.mp4', '.avi', '.mov', '.mkv']:
            dest_folder = "Videos"
        elif suffix in ['.md', '.txt']:
            dest_folder = "Drafts"
        else:
            dest_folder = "References"

        dest_path = os.path.join(self.project_path, dest_folder, file_name)

        # Copy file
        if source_path != dest_path:
            shutil.copy2(source_path, dest_path)

        # Refresh tree
        self.model.setRootPath(self.project_path)

        return dest_path

    def get_folder_path(self, folder_name: str) -> str:
        """Get path to a project folder."""
        return os.path.join(self.project_path, folder_name)
