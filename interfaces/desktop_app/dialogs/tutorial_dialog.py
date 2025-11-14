"""
Tutorial Dialog

Interactive step-by-step tutorials.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextBrowser, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.onboarding import OnboardingManager, get_tutorial, get_all_tutorials


class TutorialDialog(QDialog):
    """
    Interactive tutorial dialog.

    Shows step-by-step tutorials with progress tracking.
    """

    # Signal emitted when tutorial is completed
    tutorial_completed = pyqtSignal(str)  # tutorial_id

    def __init__(self, tutorial_id: str, parent=None):
        super().__init__(parent)

        self.tutorial_id = tutorial_id
        self.tutorial_data = get_tutorial(tutorial_id)

        if not self.tutorial_data:
            raise ValueError(f"Unknown tutorial: {tutorial_id}")

        self.onboarding_manager = OnboardingManager()
        self.current_step = 0

        self.setWindowTitle(f"Tutorial: {self.tutorial_data['title']}")
        self.setMinimumSize(700, 500)

        self._create_ui()
        self._load_step()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(self.tutorial_data['title'])
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        duration_label = QLabel(f"⏱️ {self.tutorial_data['duration']}")
        header_layout.addWidget(duration_label)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.tutorial_data['description'])
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.tutorial_data['steps']))
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Step counter
        self.step_label = QLabel()
        layout.addWidget(self.step_label)

        # Content area
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(False)
        layout.addWidget(self.content_browser)

        # Action hint
        self.action_label = QLabel()
        self.action_label.setWordWrap(True)
        self.action_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D30;
                border-left: 4px solid #007ACC;
                padding: 10px;
                color: #CCCCCC;
            }
        """)
        layout.addWidget(self.action_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.skip_btn = QPushButton("Skip Tutorial")
        self.skip_btn.clicked.connect(self._skip_tutorial)
        button_layout.addWidget(self.skip_btn)

        button_layout.addStretch()

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._previous_step)
        self.prev_btn.setEnabled(False)
        button_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_step)
        self.next_btn.setDefault(True)
        button_layout.addWidget(self.next_btn)

        layout.addLayout(button_layout)

    def _load_step(self):
        """Load current step."""
        steps = self.tutorial_data['steps']

        if self.current_step >= len(steps):
            self._complete_tutorial()
            return

        step = steps[self.current_step]

        # Update step counter
        self.step_label.setText(
            f"Step {self.current_step + 1} of {len(steps)}"
        )

        # Update progress
        self.progress_bar.setValue(self.current_step + 1)

        # Update content
        content_html = f"""
        <h2>{step['title']}</h2>
        <div style='font-size: 14px; line-height: 1.6;'>
        {step['content'].replace('\n', '<br>')}
        </div>
        """
        self.content_browser.setHtml(content_html)

        # Update action hint
        self.action_label.setText(f"💡 {step['action']}")

        # Update buttons
        self.prev_btn.setEnabled(self.current_step > 0)

        if self.current_step == len(steps) - 1:
            self.next_btn.setText("Finish ✓")
        else:
            self.next_btn.setText("Next →")

    def _next_step(self):
        """Go to next step."""
        if self.current_step < len(self.tutorial_data['steps']) - 1:
            self.current_step += 1
            self._load_step()
        else:
            self._complete_tutorial()

    def _previous_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._load_step()

    def _complete_tutorial(self):
        """Complete tutorial."""
        # Mark as completed
        self.onboarding_manager.mark_tutorial_complete(self.tutorial_id)

        # Show completion message
        completion_pct = self.onboarding_manager.get_completion_percentage()

        msg = f"Tutorial '{self.tutorial_data['title']}' completed!\n\n"
        msg += f"Overall progress: {completion_pct}%"

        next_tutorial_id = self.onboarding_manager.get_next_tutorial()
        if next_tutorial_id:
            next_tutorial = get_tutorial(next_tutorial_id)
            msg += f"\n\nNext tutorial: {next_tutorial['title']}"

        QMessageBox.information(
            self,
            "Tutorial Complete!",
            msg
        )

        # Emit signal
        self.tutorial_completed.emit(self.tutorial_id)

        # Close dialog
        self.accept()

    def _skip_tutorial(self):
        """Skip tutorial."""
        reply = QMessageBox.question(
            self,
            "Skip Tutorial?",
            "Are you sure you want to skip this tutorial?\n\n"
            "You can always access it later from Help → Tutorials.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reject()


class TutorialListDialog(QDialog):
    """
    Dialog showing all available tutorials.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.onboarding_manager = OnboardingManager()

        self.setWindowTitle("Interactive Tutorials")
        self.setMinimumSize(600, 500)

        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>📚 Interactive Tutorials</h2>")
        layout.addWidget(header)

        desc = QLabel(
            "Learn B3 features with step-by-step interactive tutorials."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Progress
        completion_pct = self.onboarding_manager.get_completion_percentage()
        progress_label = QLabel(f"Overall Progress: {completion_pct}%")
        layout.addWidget(progress_label)

        progress_bar = QProgressBar()
        progress_bar.setValue(completion_pct)
        layout.addWidget(progress_bar)

        layout.addSpacing(10)

        # Tutorials list
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem

        self.tutorials_list = QListWidget()

        tutorials = get_all_tutorials()
        for tutorial_id, tutorial_data in tutorials.items():
            is_completed = self.onboarding_manager.is_tutorial_completed(tutorial_id)

            status = "✓" if is_completed else "○"
            item_text = f"{status} {tutorial_data['title']} ({tutorial_data['duration']})"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, tutorial_id)

            if is_completed:
                item.setForeground(Qt.GlobalColor.gray)

            self.tutorials_list.addItem(item)

        self.tutorials_list.itemDoubleClicked.connect(self._start_tutorial)

        layout.addWidget(self.tutorials_list)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        start_btn = QPushButton("Start Tutorial")
        start_btn.clicked.connect(self._start_selected_tutorial)
        start_btn.setDefault(True)
        button_layout.addWidget(start_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _start_selected_tutorial(self):
        """Start selected tutorial."""
        current_item = self.tutorials_list.currentItem()
        if current_item:
            self._start_tutorial(current_item)

    def _start_tutorial(self, item):
        """Start tutorial."""
        tutorial_id = item.data(Qt.ItemDataRole.UserRole)

        # Create and show tutorial dialog
        tutorial_dialog = TutorialDialog(tutorial_id, self)
        tutorial_dialog.tutorial_completed.connect(self._on_tutorial_completed)
        tutorial_dialog.exec()

    def _on_tutorial_completed(self, tutorial_id):
        """Handle tutorial completion."""
        # Refresh list to update checkmarks
        self.close()
        # Reopen to show updated progress
        TutorialListDialog(self.parent()).exec()


def show_next_tutorial(parent=None) -> bool:
    """
    Show the next uncompleted tutorial.

    Args:
        parent: Parent widget

    Returns:
        True if tutorial was shown, False if all completed
    """
    onboarding_manager = OnboardingManager()
    next_tutorial_id = onboarding_manager.get_next_tutorial()

    if next_tutorial_id:
        tutorial_dialog = TutorialDialog(next_tutorial_id, parent)
        tutorial_dialog.exec()
        return True

    return False


def show_tutorial_list(parent=None):
    """
    Show list of all tutorials.

    Args:
        parent: Parent widget
    """
    dialog = TutorialListDialog(parent)
    dialog.exec()
