#!/usr/bin/env python3
"""
B3 Personal Assistant - Desktop App Launcher

Launch the desktop application for dissertation and video editing work.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    # Check PyQt6
    try:
        import PyQt6.QtWidgets
    except ImportError:
        missing.append("PyQt6")

    # Check PyQt6-Multimedia
    try:
        import PyQt6.QtMultimedia
    except ImportError:
        missing.append("PyQt6-Multimedia")

    # Check optional but recommended
    optional = []

    try:
        import fitz  # PyMuPDF
    except ImportError:
        optional.append("PyMuPDF (for PDF viewing)")

    try:
        import markdown
    except ImportError:
        optional.append("markdown (for Markdown preview)")

    try:
        import moviepy
    except ImportError:
        optional.append("moviepy (for video editing)")

    if missing:
        print("ERROR: Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print("  pip install -r requirements-desktop.txt")
        return False

    if optional:
        print("WARNING: Optional features missing:")
        for dep in optional:
            print(f"  - {dep}")
        print("\nSome features may not be available.")
        print("Install all dependencies with:")
        print("  pip install -r requirements-desktop.txt")
        print()

    return True

def main():
    """Launch the desktop application."""
    print("=" * 60)
    print("B3 Personal Assistant - Desktop App")
    print("=" * 60)
    print()

    # Check dependencies
    if not check_dependencies():
        return 1

    # Import and launch
    try:
        from PyQt6.QtWidgets import QApplication
        from interfaces.desktop_app.main_window import launch_desktop_app
        from modules.onboarding import OnboardingManager
        from interfaces.desktop_app.dialogs.onboarding_wizard import show_onboarding_wizard

        # Create QApplication early for wizard
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("B3 Personal Assistant")
            app.setOrganizationName("B3")

        # Check for first run and show onboarding
        onboarding_manager = OnboardingManager()

        if onboarding_manager.is_first_run():
            print("First run detected - showing onboarding wizard...")
            wizard_completed = show_onboarding_wizard()

            if not wizard_completed:
                print("Onboarding cancelled")
                return 0

            print("Onboarding completed!")
            print()

        # Load user preferences
        user_profile = onboarding_manager.preferences.to_dict()

        print("Starting application...")
        print(f"Welcome, {user_profile['name']}!")
        print()

        # Launch app with user profile
        return launch_desktop_app(user_profile)

    except Exception as e:
        print(f"ERROR: Failed to launch application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
