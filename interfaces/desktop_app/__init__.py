"""
B3PersonalAssistant Desktop Application

Minimal, efficient desktop app for dissertation and video work.
Three modes: Research, Video, Writing
"""

# Lazy imports to avoid requiring PyQt6 when only importing submodules
__all__ = ['DesktopApp', 'launch_desktop_app']

def __getattr__(name):
    """Lazy import desktop app components to avoid PyQt6 dependency issues."""
    if name == 'DesktopApp':
        from .main_window import DesktopApp
        return DesktopApp
    elif name == 'launch_desktop_app':
        from .main_window import launch_desktop_app
        return launch_desktop_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
