"""
Onboarding Wizard Dialog

First-run wizard to set up the application.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton,
    QTextEdit, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.onboarding import OnboardingManager, UserPreferences
from modules.sample_data import generate_sample_data_for_onboarding


class WelcomePage(QWizardPage):
    """Welcome page."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Welcome to B3 Personal Assistant!")
        self.setSubTitle("Your AI-powered companion for research, writing, and video editing")

        layout = QVBoxLayout(self)

        # Welcome text
        welcome_text = QLabel(
            "<h2>🎉 Welcome!</h2>"
            "<p>B3 Personal Assistant helps you:</p>"
            "<ul>"
            "<li><b>Research</b>: Manage PDFs, extract citations, search papers</li>"
            "<li><b>Write</b>: Create documents with live preview and export</li>"
            "<li><b>Create Videos</b>: Edit with futuristic themes and effects</li>"
            "</ul>"
            "<p>This wizard will help you set up your workspace.</p>"
            "<p><i>This will only take 2 minutes!</i></p>"
        )
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)

        layout.addStretch()


class UserInfoPage(QWizardPage):
    """Collect user information."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Your Profile")
        self.setSubTitle("Tell us a bit about yourself")

        layout = QVBoxLayout(self)

        # Name
        name_label = QLabel("Your Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name (optional)")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        layout.addSpacing(20)

        # Primary use case
        use_case_label = QLabel("What will you primarily use B3 for?")
        layout.addWidget(use_case_label)

        self.use_case_group = QButtonGroup(self)

        self.research_radio = QRadioButton("Research & Academic Writing")
        self.video_radio = QRadioButton("Video Editing & Creation")
        self.both_radio = QRadioButton("Both Research and Video")
        self.both_radio.setChecked(True)

        self.use_case_group.addButton(self.research_radio, 1)
        self.use_case_group.addButton(self.video_radio, 2)
        self.use_case_group.addButton(self.both_radio, 3)

        layout.addWidget(self.research_radio)
        layout.addWidget(self.video_radio)
        layout.addWidget(self.both_radio)

        layout.addStretch()


class PreferencesPage(QWizardPage):
    """Set preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Preferences")
        self.setSubTitle("Customize your experience")

        layout = QVBoxLayout(self)

        # Citation style
        citation_label = QLabel("Default Citation Style:")
        self.citation_combo = QComboBox()
        self.citation_combo.addItems(["APA", "MLA", "Chicago", "BibTeX"])
        layout.addWidget(citation_label)
        layout.addWidget(self.citation_combo)

        layout.addSpacing(10)

        # Video theme
        theme_label = QLabel("Default Video Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Neon Cyberpunk",
            "Green Solarpunk",
            "Cosmic Voyage",
            "AI Consciousness",
            "Bio Evolution"
        ])
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)

        layout.addSpacing(10)

        # Options
        self.auto_save_check = QCheckBox("Enable auto-save")
        self.auto_save_check.setChecked(True)
        layout.addWidget(self.auto_save_check)

        self.tooltips_check = QCheckBox("Show helpful tooltips")
        self.tooltips_check.setChecked(True)
        layout.addWidget(self.tooltips_check)

        layout.addStretch()


class WorkspacePage(QWizardPage):
    """Set up workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Workspace Setup")
        self.setSubTitle("Create your project workspace")

        layout = QVBoxLayout(self)

        # Workspace info
        info_label = QLabel(
            "<p>We'll create a workspace folder with:</p>"
            "<ul>"
            "<li><b>Papers/</b>: PDF research papers</li>"
            "<li><b>Notes/</b>: Markdown notes</li>"
            "<li><b>Documents/</b>: Written documents</li>"
            "<li><b>Videos/</b>: Video projects</li>"
            "<li><b>Assets/</b>: Video assets (images, audio)</li>"
            "</ul>"
            "<p>Location: <code>~/B3Workspace</code></p>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addSpacing(20)

        # Sample data option
        self.sample_data_check = QCheckBox("Include sample files to get started")
        self.sample_data_check.setChecked(True)
        self.sample_data_check.setToolTip(
            "Creates example Markdown files and a quick start guide"
        )
        layout.addWidget(self.sample_data_check)

        layout.addStretch()


class CompletePage(QWizardPage):
    """Completion page."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("You're All Set!")
        self.setSubTitle("Start using B3 Personal Assistant")

        layout = QVBoxLayout(self)

        # Success message
        success_label = QLabel(
            "<h2>✅ Setup Complete!</h2>"
            "<p>Your workspace has been created and configured.</p>"
            "<p><b>Next Steps:</b></p>"
            "<ol>"
            "<li>Check out the <b>Quick Start Guide</b> in your workspace</li>"
            "<li>Try the <b>interactive tutorials</b> (Help → Tutorials)</li>"
            "<li>Import your first file and explore!</li>"
            "</ol>"
            "<p><b>Quick Tips:</b></p>"
            "<ul>"
            "<li>Press <kbd>Ctrl+1/2/3</kbd> to switch modes</li>"
            "<li>Press <kbd>Ctrl+Space</kbd> to focus AI chat</li>"
            "<li>Drag & drop files for quick import</li>"
            "</ul>"
            "<p><i>Click Finish to start!</i></p>"
        )
        success_label.setWordWrap(True)
        layout.addWidget(success_label)

        layout.addStretch()


class OnboardingWizard(QWizard):
    """
    Onboarding wizard for first-time setup.

    Shows on first run to:
    - Collect user info
    - Set preferences
    - Create workspace
    - Generate sample data
    """

    # Signal emitted when setup is complete
    setup_complete = pyqtSignal(dict)  # Preferences dict

    def __init__(self, parent=None):
        super().__init__(parent)

        self.onboarding_manager = OnboardingManager()

        self.setWindowTitle("B3 Setup Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setFixedSize(600, 500)

        # Add pages
        self.welcome_page = WelcomePage()
        self.user_info_page = UserInfoPage()
        self.preferences_page = PreferencesPage()
        self.workspace_page = WorkspacePage()
        self.complete_page = CompletePage()

        self.addPage(self.welcome_page)
        self.addPage(self.user_info_page)
        self.addPage(self.preferences_page)
        self.addPage(self.workspace_page)
        self.addPage(self.complete_page)

        # Connect finish
        self.finished.connect(self._on_finish)

    def _on_finish(self, result):
        """Handle wizard finish."""
        if result == QDialog.DialogCode.Accepted:
            # Collect preferences
            name = self.user_info_page.name_input.text() or "User"

            citation_map = {
                "APA": "APA",
                "MLA": "MLA",
                "Chicago": "Chicago",
                "BibTeX": "BibTeX"
            }
            citation_style = citation_map[self.preferences_page.citation_combo.currentText()]

            theme_map = {
                "Neon Cyberpunk": "neon_cyberpunk",
                "Green Solarpunk": "green_solarpunk",
                "Cosmic Voyage": "cosmic_voyage",
                "AI Consciousness": "ai_consciousness",
                "Bio Evolution": "bio_evolution"
            }
            video_theme = theme_map[self.preferences_page.theme_combo.currentText()]

            # Update preferences
            self.onboarding_manager.preferences.name = name
            self.onboarding_manager.preferences.default_citation_style = citation_style
            self.onboarding_manager.preferences.default_video_theme = video_theme
            self.onboarding_manager.preferences.auto_save = self.preferences_page.auto_save_check.isChecked()
            self.onboarding_manager.preferences.show_tooltips = self.tooltips_check.isChecked()

            # Save preferences
            self.onboarding_manager.save_preferences()

            # Create workspace
            workspace_path = self.onboarding_manager.create_default_workspace()

            # Generate sample data if requested
            if self.workspace_page.sample_data_check.isChecked():
                try:
                    sample_files = generate_sample_data_for_onboarding()
                    print(f"Generated sample data: {sample_files}")
                except Exception as e:
                    print(f"Failed to generate sample data: {e}")

            # Mark first run complete
            self.onboarding_manager.mark_first_run_complete()

            # Emit signal with preferences
            self.setup_complete.emit(self.onboarding_manager.preferences.to_dict())


def show_onboarding_wizard(parent=None) -> bool:
    """
    Show onboarding wizard if this is first run.

    Args:
        parent: Parent widget

    Returns:
        True if wizard was shown and completed, False if skipped
    """
    onboarding_manager = OnboardingManager()

    if onboarding_manager.is_first_run():
        wizard = OnboardingWizard(parent)
        result = wizard.exec()
        return result == QDialog.DialogCode.Accepted

    return False
