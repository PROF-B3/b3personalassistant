"""
Main Window for B3 Desktop App

Minimal 2-panel layout with mode-based workspace.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QComboBox, QStatusBar, QMenuBar,
    QMenu, QApplication, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from interfaces.desktop_app.utils.theme import get_stylesheet, DARK_THEME
from interfaces.desktop_app.panels import FileTreePanel, AgentPanel, ResearchPanel
from core.orchestrator import Orchestrator


class DesktopApp(QMainWindow):
    """
    Main application window for B3 Personal Assistant.

    Layout:
    - Left sidebar: File tree + Agents
    - Main workspace: Adapts to mode (Research/Video/Writing)
    - Bottom panel: AI agent chat
    - Status bar: System info
    """

    # Signals
    mode_changed = pyqtSignal(str)  # research, video, writing
    file_opened = pyqtSignal(str)   # file path

    def __init__(self, user_profile: Optional[Dict] = None, config: Optional[Any] = None):
        super().__init__()

        self.user_profile = user_profile or {}
        self.config = config
        self.current_mode = "research"
        self.current_file = None

        # Initialize backend
        self.orchestrator = Orchestrator(self.user_profile)

        self.setWindowTitle("B3 Personal Assistant")
        self.setGeometry(100, 100, 1400, 900)

        # Apply theme
        self.setStyleSheet(get_stylesheet(DARK_THEME))

        # Setup UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        self._setup_shortcuts()

        # Connect signals
        self.mode_changed.connect(self._on_mode_changed)

        # Start status updates
        self._start_status_updates()

        self.showMaximized()

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_file)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        edit_menu.addAction(find_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        toggle_chat_action = QAction("Toggle &Chat", self)
        toggle_chat_action.setShortcut(QKeySequence("Ctrl+J"))
        toggle_chat_action.triggered.connect(self._toggle_chat_panel)
        view_menu.addAction(toggle_chat_action)

        # Research menu
        research_menu = menubar.addMenu("&Research")

        search_papers_action = QAction("&Search Papers...", self)
        search_papers_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        search_papers_action.triggered.connect(self._search_papers)
        research_menu.addAction(search_papers_action)

        extract_citation_action = QAction("&Extract Citation", self)
        extract_citation_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        extract_citation_action.triggered.connect(self._extract_citation)
        research_menu.addAction(extract_citation_action)

        generate_bib_action = QAction("&Generate Bibliography...", self)
        generate_bib_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        generate_bib_action.triggered.connect(self._generate_bibliography)
        research_menu.addAction(generate_bib_action)

        # Video menu
        video_menu = menubar.addMenu("&Video")

        import_video_action = QAction("&Import Video...", self)
        import_video_action.triggered.connect(self._import_video)
        video_menu.addAction(import_video_action)

        cut_segment_action = QAction("&Cut Segment", self)
        cut_segment_action.setShortcut(QKeySequence("Ctrl+K"))
        cut_segment_action.triggered.connect(self._cut_segment)
        video_menu.addAction(cut_segment_action)

        apply_theme_action = QAction("Apply &Theme...", self)
        apply_theme_action.triggered.connect(self._apply_video_theme)
        video_menu.addAction(apply_theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _create_toolbar(self):
        """Create the toolbar with mode switcher."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # Mode label
        mode_label = QLabel("Mode:")
        toolbar.addWidget(mode_label)

        # Mode switcher
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Research", "Video", "Writing"])
        self.mode_combo.setCurrentText("Research")
        self.mode_combo.currentTextChanged.connect(self._change_mode)
        self.mode_combo.setMinimumWidth(150)
        toolbar.addWidget(self.mode_combo)

        toolbar.addSeparator()

        # Quick action buttons (will be populated based on mode)
        self.toolbar = toolbar

    def _create_central_widget(self):
        """Create the main layout with splitters."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter (horizontal: sidebar | workspace)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar with file tree
        sidebar_splitter = QSplitter(Qt.Orientation.Vertical)

        # File tree panel
        self.file_tree = FileTreePanel()
        self.file_tree.file_opened.connect(self._on_file_opened_from_tree)
        self.file_tree.files_imported.connect(self._on_files_imported)
        sidebar_splitter.addWidget(self.file_tree)

        # Compact agent selector (will show in sidebar)
        from interfaces.desktop_app.panels.agent_panel import CompactAgentPanel
        self.compact_agents = CompactAgentPanel()
        self.compact_agents.agent_selected.connect(self._on_agent_selected_sidebar)
        sidebar_splitter.addWidget(self.compact_agents)

        # Set splitter proportions (70% files, 30% agents)
        sidebar_splitter.setSizes([700, 300])

        self.main_splitter.addWidget(sidebar_splitter)

        # Right area: workspace + chat splitter (vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Workspace (will change based on mode)
        self.workspace_widget = QWidget()
        self.workspace_layout = QVBoxLayout(self.workspace_widget)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(0)

        # Create mode-specific panels
        self.research_panel = ResearchPanel(self.orchestrator)
        self.research_panel.citation_extracted.connect(self._on_citation_extracted)
        self.research_panel.note_created.connect(self._on_note_created)
        self.research_panel.summarize_requested.connect(self._on_summarize_requested)
        self.research_panel.setVisible(False)
        self.workspace_layout.addWidget(self.research_panel)

        # Placeholder for other modes
        self.workspace_placeholder = QLabel("Workspace\n\nOpen a file to begin\n\nPDF → Research Mode\nVideo → Video Mode\nMarkdown → Writing Mode")
        self.workspace_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.workspace_placeholder.setStyleSheet("color: #858585; font-size: 14px;")
        self.workspace_layout.addWidget(self.workspace_placeholder)

        right_splitter.addWidget(self.workspace_widget)

        # Agent chat panel
        self.agent_chat = AgentPanel(self.orchestrator)
        self.agent_chat.message_sent.connect(self._on_agent_message_sent)
        self.agent_chat.response_received.connect(self._on_agent_response_received)

        right_splitter.addWidget(self.agent_chat)

        # Set splitter proportions
        right_splitter.setSizes([700, 300])  # 70% workspace, 30% chat

        self.main_splitter.addWidget(right_splitter)

        # Set main splitter proportions
        self.main_splitter.setSizes([250, 1150])  # 250px sidebar, rest for workspace

        main_layout.addWidget(self.main_splitter)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status labels
        self.status_label = QLabel("Ready")
        self.mode_status = QLabel("Mode: Research")
        self.agent_status = QLabel("Agent: Alpha")
        self.file_status = QLabel("No file")
        self.resource_status = QLabel("CPU: 0% | RAM: 0%")

        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.file_status)
        self.status_bar.addPermanentWidget(self.mode_status)
        self.status_bar.addPermanentWidget(self.agent_status)
        self.status_bar.addPermanentWidget(self.resource_status)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Mode switching
        shortcut_research = QKeySequence("Ctrl+1")
        action_research = QAction(self)
        action_research.setShortcut(shortcut_research)
        action_research.triggered.connect(lambda: self.mode_combo.setCurrentText("Research"))
        self.addAction(action_research)

        shortcut_video = QKeySequence("Ctrl+2")
        action_video = QAction(self)
        action_video.setShortcut(shortcut_video)
        action_video.triggered.connect(lambda: self.mode_combo.setCurrentText("Video"))
        self.addAction(action_video)

        shortcut_writing = QKeySequence("Ctrl+3")
        action_writing = QAction(self)
        action_writing.setShortcut(shortcut_writing)
        action_writing.triggered.connect(lambda: self.mode_combo.setCurrentText("Writing"))
        self.addAction(action_writing)

        # Agent chat focus
        shortcut_chat = QKeySequence("Ctrl+Space")
        action_chat = QAction(self)
        action_chat.setShortcut(shortcut_chat)
        action_chat.triggered.connect(self._focus_chat)
        self.addAction(action_chat)

    def _start_status_updates(self):
        """Start periodic status bar updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)  # Update every 2 seconds

    def _update_status(self):
        """Update status bar information."""
        try:
            # Get resource monitor info
            if hasattr(self.orchestrator, 'resource_monitor'):
                status = self.orchestrator.resource_monitor.get_status()
                cpu = status.get('cpu_percent', 0)
                memory = status.get('memory_percent', 0)
                self.resource_status.setText(f"CPU: {cpu:.1f}% | RAM: {memory:.1f}%")
        except Exception:
            pass

    # Slot methods
    def _change_mode(self, mode_text: str):
        """Handle mode change."""
        mode = mode_text.lower()
        if mode != self.current_mode:
            self.current_mode = mode
            self.mode_status.setText(f"Mode: {mode_text}")
            self.mode_changed.emit(mode)

    def _on_mode_changed(self, mode: str):
        """Handle mode changed signal."""
        self.status_label.setText(f"Switched to {mode.title()} mode")
        # Update agent panel for mode
        self.agent_chat.update_for_mode(mode)
        # Update workspace based on mode
        # (Will be implemented when mode-specific panels are added)

    def _toggle_sidebar(self):
        """Toggle sidebar visibility."""
        sidebar = self.main_splitter.widget(0)
        sidebar.setVisible(not sidebar.isVisible())

    def _toggle_chat_panel(self):
        """Toggle chat panel visibility."""
        self.agent_chat.setVisible(not self.agent_chat.isVisible())

    def _focus_chat(self):
        """Focus the chat input."""
        self.agent_chat.focus_input()
        self.status_label.setText("Chat focused")

    # File operations
    def _new_file(self):
        """Create new file."""
        QMessageBox.information(self, "New File", "New file creation will be implemented soon.")

    def _open_file(self):
        """Open file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;PDF Files (*.pdf);;Video Files (*.mp4 *.avi *.mov);;Markdown Files (*.md)"
        )
        if file_path:
            self.current_file = file_path
            self.file_status.setText(Path(file_path).name)
            self.file_opened.emit(file_path)
            self._auto_switch_mode(file_path)

    def _save_file(self):
        """Save current file."""
        if self.current_file:
            self.status_label.setText(f"Saved: {Path(self.current_file).name}")
        else:
            self._save_file_as()

    def _save_file_as(self):
        """Save file as dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_status.setText(Path(file_path).name)
            self.status_label.setText(f"Saved as: {Path(file_path).name}")

    def _export_file(self):
        """Export current file."""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon.")

    def _auto_switch_mode(self, file_path: str):
        """Auto-switch mode based on file type."""
        suffix = Path(file_path).suffix.lower()
        if suffix == '.pdf':
            self.mode_combo.setCurrentText("Research")
        elif suffix in ['.mp4', '.avi', '.mov', '.mkv']:
            self.mode_combo.setCurrentText("Video")
        elif suffix in ['.md', '.txt']:
            self.mode_combo.setCurrentText("Writing")

    # Research operations
    def _search_papers(self):
        """Open paper search dialog."""
        QMessageBox.information(self, "Search Papers", "Paper search will be implemented soon.")

    def _extract_citation(self):
        """Extract citation from current document."""
        QMessageBox.information(self, "Extract Citation", "Citation extraction will be implemented soon.")

    def _generate_bibliography(self):
        """Generate bibliography."""
        QMessageBox.information(self, "Generate Bibliography", "Bibliography generation will be implemented soon.")

    # Video operations
    def _import_video(self):
        """Import video file."""
        self._open_file()

    def _cut_segment(self):
        """Cut video segment."""
        QMessageBox.information(self, "Cut Segment", "Video cutting will be implemented soon.")

    def _apply_video_theme(self):
        """Apply theme to video."""
        QMessageBox.information(self, "Apply Theme", "Video theme application will be implemented soon.")

    # Help operations
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About B3 Personal Assistant",
            """<h2>B3 Personal Assistant</h2>
            <p>Version 1.0</p>
            <p>A multi-agent AI system for research and creative work.</p>
            <p><b>Agents:</b></p>
            <ul>
                <li>Alpha (Α) - Chief Coordinator</li>
                <li>Beta (Β) - Research Analyst</li>
                <li>Gamma (Γ) - Knowledge Manager</li>
                <li>Delta (Δ) - Task Coordinator</li>
                <li>Epsilon (Ε) - Creative Director</li>
                <li>Zeta (Ζ) - Code Architect</li>
                <li>Eta (Η) - Evolution Engineer</li>
            </ul>
            """
        )

    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            """<h3>Mode Switching</h3>
            <p>Ctrl+1 - Research Mode<br/>
            Ctrl+2 - Video Mode<br/>
            Ctrl+3 - Writing Mode</p>

            <h3>Navigation</h3>
            <p>Ctrl+B - Toggle Sidebar<br/>
            Ctrl+J - Toggle Chat Panel<br/>
            Ctrl+Space - Focus Chat</p>

            <h3>File Operations</h3>
            <p>Ctrl+N - New File<br/>
            Ctrl+O - Open File<br/>
            Ctrl+S - Save File<br/>
            Ctrl+Shift+S - Save As<br/>
            Ctrl+E - Export</p>

            <h3>Research</h3>
            <p>Ctrl+Shift+F - Search Papers<br/>
            Ctrl+Shift+C - Extract Citation<br/>
            Ctrl+Shift+B - Generate Bibliography</p>

            <h3>Video</h3>
            <p>Ctrl+K - Cut Segment</p>
            """
        )

    # File tree callbacks
    def _on_file_opened_from_tree(self, file_path: str):
        """Handle file opened from tree."""
        self.current_file = file_path
        self.file_status.setText(Path(file_path).name)
        self.file_opened.emit(file_path)
        self._auto_switch_mode(file_path)
        self._load_file_in_workspace(file_path)
        self.status_label.setText(f"Opened: {Path(file_path).name}")

    def _on_files_imported(self, file_paths: list):
        """Handle files imported via drag-and-drop."""
        count = len(file_paths)
        self.status_label.setText(f"Imported {count} file(s)")

        # Open first file if only one
        if count == 1:
            self._on_file_opened_from_tree(file_paths[0])
        else:
            QMessageBox.information(
                self,
                "Files Imported",
                f"Successfully imported {count} files."
            )

    # Agent panel callbacks
    def _on_agent_selected_sidebar(self, agent_name: str):
        """Handle agent selected from sidebar."""
        # Find and select agent in chat panel
        for i in range(self.agent_chat.agent_selector.count()):
            if self.agent_chat.agent_selector.itemText(i).startswith(agent_name):
                self.agent_chat.agent_selector.setCurrentIndex(i)
                break

        self.agent_status.setText(f"Agent: {agent_name}")

    def _on_agent_message_sent(self, agent: str, message: str):
        """Handle message sent to agent."""
        self.status_label.setText(f"Processing with {agent}...")

    def _on_agent_response_received(self, agent: str, response: str):
        """Handle response received from agent."""
        self.status_label.setText(f"Response from {agent}")

    # Workspace management
    def _load_file_in_workspace(self, file_path: str):
        """Load file in appropriate workspace panel."""
        suffix = Path(file_path).suffix.lower()

        # Hide all panels
        self.research_panel.setVisible(False)
        self.workspace_placeholder.setVisible(False)

        if suffix == '.pdf':
            # Load in research panel
            success = self.research_panel.load_pdf(file_path)
            if success:
                self.research_panel.setVisible(True)
                self.status_label.setText(f"PDF loaded: {Path(file_path).name}")
            else:
                self.workspace_placeholder.setText(
                    "Failed to load PDF\n\n"
                    "Install PyMuPDF with:\npip install PyMuPDF"
                )
                self.workspace_placeholder.setVisible(True)

        elif suffix in ['.mp4', '.avi', '.mov', '.mkv']:
            # Video mode (to be implemented)
            self.workspace_placeholder.setText(
                "Video Mode\n\n"
                "Video player will be implemented in Phase 5"
            )
            self.workspace_placeholder.setVisible(True)

        elif suffix in ['.md', '.txt']:
            # Writing mode (to be implemented)
            self.workspace_placeholder.setText(
                "Writing Mode\n\n"
                "Markdown editor will be implemented in Phase 4"
            )
            self.workspace_placeholder.setVisible(True)

        else:
            # Unsupported file type
            self.workspace_placeholder.setText(
                f"Unsupported file type: {suffix}\n\n"
                "Supported: PDF, Video (MP4/AVI/MOV), Markdown (MD/TXT)"
            )
            self.workspace_placeholder.setVisible(True)

    # Research panel callbacks
    def _on_citation_extracted(self, citation_data: dict):
        """Handle citation extracted."""
        self.status_label.setText("Citation extracted and added to bibliography")

    def _on_note_created(self, note_content: str):
        """Handle note created."""
        self.status_label.setText("Note created from PDF")
        # Could save to Notes/ folder or pass to Gamma agent

    def _on_summarize_requested(self, text: str):
        """Handle summarize request."""
        # Send to Beta agent for summarization
        self.agent_chat.agent_selector.setCurrentText("Beta (Β)")
        message = f"Please summarize this text:\n\n{text[:1000]}"
        self.agent_chat.message_input.setText(message)
        self.agent_chat._send_message()


def launch_desktop_app(user_profile: Optional[Dict] = None, config: Optional[Any] = None):
    """
    Launch the desktop application.

    Args:
        user_profile: User profile dictionary
        config: Configuration object
    """
    app = QApplication(sys.argv)
    app.setApplicationName("B3 Personal Assistant")
    app.setOrganizationName("B3")

    window = DesktopApp(user_profile, config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    # Test launch
    test_profile = {
        'name': 'Test User',
        'communication_style': 'concise',
        'work_style': 'flexible'
    }
    launch_desktop_app(test_profile)
