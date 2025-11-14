"""
B3PersonalAssistant Interfaces

This package contains the user interface components including GUI, CLI, and Desktop app.
"""

# Lazy imports to avoid requiring tkinter when only using desktop_app
__all__ = [
    'launch_gui',
    'launch_cli',
    'launch_desktop_app'
]

def __getattr__(name):
    """Lazy import interface launchers to avoid dependency issues."""
    if name == 'launch_gui':
        from .gui_launcher import launch_gui
        return launch_gui
    elif name == 'launch_cli':
        from .cli_launcher import launch_cli
        return launch_cli
    elif name == 'launch_desktop_app':
        from .desktop_app.main_window import launch_desktop_app
        return launch_desktop_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'") 