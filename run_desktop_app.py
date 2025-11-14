#!/usr/bin/env python3
"""
B3 Personal Assistant - Desktop App Launcher

Launch the minimal desktop application with all three modes:
- Research: PDF viewing and citation management
- Video: Video editing and theme application
- Writing: Markdown editing and export

Usage:
    python run_desktop_app.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.desktop_app.main_window import launch_desktop_app


def load_user_profile():
    """Load user profile from databases/user_profile.json if it exists."""
    import json
    profile_path = Path("databases/user_profile.json")
    if profile_path.exists():
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load user profile: {e}")

    # Default profile
    return {
        'name': 'User',
        'communication_style': 'concise',
        'work_style': 'flexible',
        'interests': ['research', 'writing', 'video'],
        'task_preferences': 'simple',
        'knowledge_preferences': 'zettelkasten'
    }


def main():
    """Main entry point."""
    print("🚀 Starting B3 Personal Assistant Desktop App...")
    print()
    print("Features:")
    print("  • Research Mode: PDF viewing, citation extraction, bibliography")
    print("  • Video Mode: Video editing, theme application, segment export")
    print("  • Writing Mode: Markdown editing, live preview, export to Word/LaTeX")
    print()
    print("Keyboard Shortcuts:")
    print("  Ctrl+1, 2, 3  - Switch modes")
    print("  Ctrl+Space    - Focus agent chat")
    print("  Ctrl+B        - Toggle sidebar")
    print("  Ctrl+O        - Open file")
    print()

    # Load user profile
    user_profile = load_user_profile()
    print(f"Welcome, {user_profile['name']}!")
    print()

    # Launch app
    try:
        sys.exit(launch_desktop_app(user_profile))
    except Exception as e:
        print(f"❌ Error launching desktop app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
