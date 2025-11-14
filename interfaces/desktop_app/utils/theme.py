"""
Theme and styling for B3 Desktop App

Minimal, clean design inspired by VS Code dark theme.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class Theme:
    """Color theme for the application."""

    # Background colors
    bg_main: str = "#1E1E1E"
    bg_sidebar: str = "#252526"
    bg_panel: str = "#2D2D2D"
    bg_hover: str = "#2A2D2E"
    bg_selected: str = "#37373D"

    # Text colors
    text_primary: str = "#CCCCCC"
    text_secondary: str = "#858585"
    text_disabled: str = "#656565"

    # Accent colors
    accent: str = "#007ACC"
    accent_hover: str = "#0098FF"
    success: str = "#4EC9B0"
    warning: str = "#CE9178"
    error: str = "#F48771"

    # Border colors
    border: str = "#3E3E42"
    border_focus: str = "#007ACC"

    # Special
    selection: str = "#264F78"
    highlight: str = "#FFA500"


def get_stylesheet(theme: Theme = None) -> str:
    """
    Generate Qt stylesheet from theme.

    Args:
        theme: Theme object (uses default if None)

    Returns:
        Qt stylesheet string
    """
    if theme is None:
        theme = Theme()

    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {theme.bg_main};
        color: {theme.text_primary};
    }}

    /* Menu Bar */
    QMenuBar {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_primary};
        border-bottom: 1px solid {theme.border};
        padding: 4px;
    }}

    QMenuBar::item {{
        padding: 4px 12px;
        background: transparent;
    }}

    QMenuBar::item:selected {{
        background-color: {theme.bg_hover};
    }}

    QMenu {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
    }}

    QMenu::item:selected {{
        background-color: {theme.bg_selected};
    }}

    /* Tool Bar */
    QToolBar {{
        background-color: {theme.bg_sidebar};
        border: none;
        spacing: 8px;
        padding: 4px;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        border-radius: 2px;
        padding: 6px 16px;
        min-height: 22px;
    }}

    QPushButton:hover {{
        background-color: {theme.bg_hover};
        border-color: {theme.accent};
    }}

    QPushButton:pressed {{
        background-color: {theme.bg_selected};
    }}

    QPushButton:disabled {{
        color: {theme.text_disabled};
        border-color: {theme.border};
    }}

    /* Primary Button */
    QPushButton[primary="true"] {{
        background-color: {theme.accent};
        color: white;
        border: none;
    }}

    QPushButton[primary="true"]:hover {{
        background-color: {theme.accent_hover};
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        border-radius: 2px;
        padding: 4px 8px;
        min-height: 22px;
    }}

    QComboBox:hover {{
        border-color: {theme.accent};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {theme.text_secondary};
        margin-right: 6px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        selection-background-color: {theme.bg_selected};
        border: 1px solid {theme.border};
    }}

    /* Line Edit */
    QLineEdit {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        border-radius: 2px;
        padding: 4px 8px;
        selection-background-color: {theme.selection};
    }}

    QLineEdit:focus {{
        border-color: {theme.border_focus};
    }}

    /* Text Edit */
    QTextEdit, QPlainTextEdit {{
        background-color: {theme.bg_main};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        selection-background-color: {theme.selection};
    }}

    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {theme.border_focus};
    }}

    /* Tree View (File Tree) */
    QTreeView {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_primary};
        border: none;
        outline: none;
        show-decoration-selected: 1;
    }}

    QTreeView::item {{
        padding: 4px;
        border: none;
    }}

    QTreeView::item:hover {{
        background-color: {theme.bg_hover};
    }}

    QTreeView::item:selected {{
        background-color: {theme.bg_selected};
    }}

    QTreeView::branch {{
        background-color: {theme.bg_sidebar};
    }}

    /* List View */
    QListView {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_primary};
        border: none;
        outline: none;
    }}

    QListView::item {{
        padding: 6px;
    }}

    QListView::item:hover {{
        background-color: {theme.bg_hover};
    }}

    QListView::item:selected {{
        background-color: {theme.bg_selected};
    }}

    /* Table View */
    QTableView {{
        background-color: {theme.bg_main};
        color: {theme.text_primary};
        gridline-color: {theme.border};
        border: none;
        selection-background-color: {theme.bg_selected};
    }}

    QHeaderView::section {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_secondary};
        padding: 6px;
        border: none;
        border-bottom: 1px solid {theme.border};
        border-right: 1px solid {theme.border};
    }}

    /* Splitter */
    QSplitter::handle {{
        background-color: {theme.border};
    }}

    QSplitter::handle:horizontal {{
        width: 1px;
    }}

    QSplitter::handle:vertical {{
        height: 1px;
    }}

    /* Scroll Bar */
    QScrollBar:vertical {{
        background-color: {theme.bg_sidebar};
        width: 12px;
        border: none;
    }}

    QScrollBar::handle:vertical {{
        background-color: {theme.bg_hover};
        min-height: 30px;
        border-radius: 6px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {theme.text_secondary};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background-color: {theme.bg_sidebar};
        height: 12px;
        border: none;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {theme.bg_hover};
        min-width: 30px;
        border-radius: 6px;
        margin: 2px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {theme.text_secondary};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {theme.border};
        background-color: {theme.bg_main};
    }}

    QTabBar::tab {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_secondary};
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid transparent;
    }}

    QTabBar::tab:hover {{
        background-color: {theme.bg_hover};
        color: {theme.text_primary};
    }}

    QTabBar::tab:selected {{
        color: {theme.text_primary};
        border-bottom: 2px solid {theme.accent};
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {theme.bg_sidebar};
        color: {theme.text_secondary};
        border-top: 1px solid {theme.border};
    }}

    /* Label */
    QLabel {{
        color: {theme.text_primary};
        background-color: transparent;
    }}

    /* Group Box */
    QGroupBox {{
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
    }}

    /* Tooltip */
    QToolTip {{
        background-color: {theme.bg_panel};
        color: {theme.text_primary};
        border: 1px solid {theme.border};
        padding: 4px;
    }}
    """


# Preset themes
DARK_THEME = Theme()

LIGHT_THEME = Theme(
    bg_main="#FFFFFF",
    bg_sidebar="#F3F3F3",
    bg_panel="#FAFAFA",
    bg_hover="#E5E5E5",
    bg_selected="#E0E0E0",
    text_primary="#1E1E1E",
    text_secondary="#6E6E6E",
    text_disabled="#B4B4B4",
    accent="#0078D4",
    accent_hover="#106EBE",
    success="#107C10",
    warning="#CA5010",
    error="#A80000",
    border="#CCCCCC",
    border_focus="#0078D4",
    selection="#CCE8FF",
    highlight="#0078D4"
)
