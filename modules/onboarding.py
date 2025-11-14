"""
Onboarding and First-Run Initialization Module

Handles first-time setup, user onboarding, and tutorials.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

@dataclass
class UserPreferences:
    """User preferences and settings."""
    name: str = "User"
    theme: str = "dark"
    auto_save: bool = True
    default_citation_style: str = "APA"
    default_video_theme: str = "neon_cyberpunk"
    show_tooltips: bool = True
    completed_tutorials: list = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'theme': self.theme,
            'auto_save': self.auto_save,
            'default_citation_style': self.default_citation_style,
            'default_video_theme': self.default_video_theme,
            'show_tooltips': self.show_tooltips,
            'completed_tutorials': self.completed_tutorials
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create from dictionary."""
        return cls(**data)

class OnboardingManager:
    """
    Manage onboarding, first-run setup, and user preferences.

    Features:
    - First-run detection
    - User profile creation
    - Sample data generation
    - Tutorial tracking
    - Preference management
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize onboarding manager.

        Args:
            config_dir: Configuration directory (default: ~/.b3assistant)
        """
        self.logger = logging.getLogger("onboarding")

        # Set config directory
        if config_dir is None:
            self.config_dir = Path.home() / ".b3assistant"
        else:
            self.config_dir = Path(config_dir)

        # Create config directory
        self.config_dir.mkdir(exist_ok=True)

        # Config files
        self.first_run_file = self.config_dir / "first_run.json"
        self.preferences_file = self.config_dir / "preferences.json"
        self.tutorials_file = self.config_dir / "tutorials.json"

        # Load or initialize
        self.preferences = self._load_preferences()
        self.tutorial_status = self._load_tutorial_status()

    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return not self.first_run_file.exists()

    def mark_first_run_complete(self):
        """Mark first run as complete."""
        with open(self.first_run_file, 'w') as f:
            json.dump({
                'completed': True,
                'version': '1.0.0',
                'timestamp': self._get_timestamp()
            }, f, indent=2)
        self.logger.info("First run marked as complete")

    def _load_preferences(self) -> UserPreferences:
        """Load user preferences."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                return UserPreferences.from_dict(data)
            except Exception as e:
                self.logger.error(f"Failed to load preferences: {e}")
                return UserPreferences()
        return UserPreferences()

    def save_preferences(self):
        """Save user preferences."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
            self.logger.info("Preferences saved")
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")

    def _load_tutorial_status(self) -> Dict[str, bool]:
        """Load tutorial completion status."""
        if self.tutorials_file.exists():
            try:
                with open(self.tutorials_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load tutorial status: {e}")
                return {}
        return {}

    def save_tutorial_status(self):
        """Save tutorial status."""
        try:
            with open(self.tutorials_file, 'w') as f:
                json.dump(self.tutorial_status, f, indent=2)
            self.logger.info("Tutorial status saved")
        except Exception as e:
            self.logger.error(f"Failed to save tutorial status: {e}")

    def mark_tutorial_complete(self, tutorial_id: str):
        """Mark a tutorial as completed."""
        self.tutorial_status[tutorial_id] = True
        if tutorial_id not in self.preferences.completed_tutorials:
            self.preferences.completed_tutorials.append(tutorial_id)
        self.save_tutorial_status()
        self.save_preferences()
        self.logger.info(f"Tutorial '{tutorial_id}' marked as complete")

    def is_tutorial_completed(self, tutorial_id: str) -> bool:
        """Check if a tutorial is completed."""
        return self.tutorial_status.get(tutorial_id, False)

    def get_next_tutorial(self) -> Optional[str]:
        """Get the next uncompleted tutorial."""
        tutorials = [
            'basic_navigation',
            'research_mode',
            'writing_mode',
            'video_mode',
            'agent_chat',
            'citation_management',
            'video_editing'
        ]

        for tutorial_id in tutorials:
            if not self.is_tutorial_completed(tutorial_id):
                return tutorial_id

        return None  # All completed

    def get_completion_percentage(self) -> int:
        """Get tutorial completion percentage."""
        total_tutorials = 7  # Total number of tutorials
        completed = len(self.preferences.completed_tutorials)
        return int((completed / total_tutorials) * 100)

    def create_default_workspace(self):
        """Create default workspace structure."""
        workspace = Path.home() / "B3Workspace"

        # Create directories
        directories = [
            workspace,
            workspace / "Papers",
            workspace / "Notes",
            workspace / "Documents",
            workspace / "Videos",
            workspace / "Projects",
            workspace / "Assets" / "videos",
            workspace / "Assets" / "images",
            workspace / "Assets" / "audio",
            workspace / "Exports"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Create README
        readme_path = workspace / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write("""# B3 Personal Assistant Workspace

Welcome to your B3 workspace!

## Directory Structure

- **Papers/** - Research papers and PDFs
- **Notes/** - Markdown notes and Zettelkasten
- **Documents/** - Written documents and exports
- **Videos/** - Video projects and exports
- **Projects/** - Multi-file projects
- **Assets/** - Video assets (videos, images, audio)
- **Exports/** - Exported files (Word, LaTeX, videos)

## Getting Started

1. **Research Mode**: Drop PDFs into Papers/ folder
2. **Writing Mode**: Create .md files in Documents/
3. **Video Mode**: Import videos to Videos/ folder

## Tips

- Use Ctrl+1, Ctrl+2, Ctrl+3 to switch modes
- Drag and drop files for quick import
- Use AI agents for help (Ctrl+Space to focus chat)

Happy creating!
""")

        self.logger.info(f"Workspace created at: {workspace}")
        return str(workspace)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def reset_onboarding(self):
        """Reset onboarding status (for testing)."""
        if self.first_run_file.exists():
            self.first_run_file.unlink()
        self.tutorial_status = {}
        self.preferences.completed_tutorials = []
        self.save_tutorial_status()
        self.save_preferences()
        self.logger.info("Onboarding reset")

# Tutorial definitions
TUTORIALS = {
    'basic_navigation': {
        'title': 'Basic Navigation',
        'description': 'Learn to navigate the B3 desktop app',
        'duration': '2 minutes',
        'steps': [
            {
                'title': 'Welcome to B3',
                'content': 'B3 Personal Assistant helps you with research, writing, and video editing.',
                'action': 'Click Next to continue'
            },
            {
                'title': 'The Interface',
                'content': 'The app has 2 main panels:\n- Left: File tree and agent selector\n- Right: Workspace and AI chat',
                'action': 'Look at the interface layout'
            },
            {
                'title': 'Mode Switcher',
                'content': 'Use the mode dropdown to switch between:\n- Research (for PDFs)\n- Writing (for Markdown)\n- Video (for videos)',
                'action': 'Try switching modes'
            },
            {
                'title': 'Keyboard Shortcuts',
                'content': 'Quick shortcuts:\n- Ctrl+1: Research mode\n- Ctrl+2: Video mode\n- Ctrl+3: Writing mode\n- Ctrl+Space: Focus AI chat',
                'action': 'Press Ctrl+1 to switch to Research mode'
            }
        ]
    },
    'research_mode': {
        'title': 'Research Mode',
        'description': 'Learn to work with PDFs and citations',
        'duration': '3 minutes',
        'steps': [
            {
                'title': 'Opening PDFs',
                'content': 'Open a PDF by:\n1. File → Open\n2. Drag & drop into file tree\n3. Double-click in file tree',
                'action': 'Try opening a PDF'
            },
            {
                'title': 'PDF Viewer',
                'content': 'Navigate with:\n- Page up/down buttons\n- Zoom +/- buttons\n- Mouse wheel to scroll',
                'action': 'Navigate through pages'
            },
            {
                'title': 'Extract Citation',
                'content': 'Click "Extract Citation" to automatically extract bibliographic info.\nWorks with most academic papers!',
                'action': 'Extract citation from current PDF'
            },
            {
                'title': 'Search Papers',
                'content': 'Click "Search Papers" to find related work using:\n- arXiv\n- CrossRef\n- Semantic Scholar',
                'action': 'Search for papers on your topic'
            }
        ]
    },
    'writing_mode': {
        'title': 'Writing Mode',
        'description': 'Learn to write documents with live preview',
        'duration': '3 minutes',
        'steps': [
            {
                'title': 'Creating Documents',
                'content': 'Switch to Writing mode (Ctrl+3) and create a .md file.\nThe editor supports Markdown with syntax highlighting.',
                'action': 'Create a new Markdown file'
            },
            {
                'title': 'Live Preview',
                'content': 'See your formatted text in real-time!\nUse the formatting toolbar for quick markup.',
                'action': 'Type some text and watch the preview'
            },
            {
                'title': 'Insert Citations',
                'content': 'Click "Insert Citation" to add references.\nUse [@AuthorYear] syntax for inline citations.',
                'action': 'Insert a citation'
            },
            {
                'title': 'Export',
                'content': 'Export your document to:\n- Word (.docx)\n- LaTeX (.tex)\n\nPerfect for academic submissions!',
                'action': 'Try exporting to Word'
            }
        ]
    },
    'video_mode': {
        'title': 'Video Mode',
        'description': 'Learn video editing with themes',
        'duration': '4 minutes',
        'steps': [
            {
                'title': 'Loading Videos',
                'content': 'Switch to Video mode (Ctrl+2) and load a video.\nSupports MP4, AVI, MOV, MKV, and more!',
                'action': 'Load a video file'
            },
            {
                'title': 'Timeline Navigation',
                'content': 'Use the timeline to:\n- Scrub through video\n- See segment markers\n- Click to jump to time',
                'action': 'Scrub through your video'
            },
            {
                'title': 'Mark Segments',
                'content': 'Create segments:\n1. Play to start point → Click "[ Mark Start"\n2. Play to end point → Click "Mark End ]"\nSegment appears in list!',
                'action': 'Mark a video segment'
            },
            {
                'title': 'Apply Themes',
                'content': '5 futuristic themes:\n- Neon Cyberpunk\n- Green Solarpunk\n- Cosmic Voyage\n- AI Consciousness\n- Bio Evolution',
                'action': 'Select a theme'
            },
            {
                'title': 'Export',
                'content': 'Export options:\n- Export segment (selected)\n- Export full video (with theme)\n- Create futuristic remix (full pipeline)',
                'action': 'Export a segment with theme'
            }
        ]
    },
    'agent_chat': {
        'title': 'AI Agent Chat',
        'description': 'Learn to use the 7 AI agents',
        'duration': '3 minutes',
        'steps': [
            {
                'title': 'Meet the Agents',
                'content': '7 specialized agents:\n- Alpha: Coordinator\n- Beta: Researcher\n- Gamma: Knowledge Manager\n- Delta: Optimizer\n- Epsilon: Creative Director\n- Zeta: Technical Specialist\n- Eta: Monitor',
                'action': 'View the agent list'
            },
            {
                'title': 'Selecting Agents',
                'content': 'Click an agent in the sidebar or use the dropdown.\nEach agent has unique expertise!',
                'action': 'Select Beta (Researcher)'
            },
            {
                'title': 'Asking Questions',
                'content': 'Type your question in the chat.\nAgents provide specialized assistance based on current context.',
                'action': 'Ask Beta to summarize a paper'
            },
            {
                'title': 'Quick Actions',
                'content': 'Use quick action buttons for common tasks:\n- Summarize\n- Improve Writing\n- Generate Ideas',
                'action': 'Try a quick action'
            }
        ]
    },
    'citation_management': {
        'title': 'Citation Management',
        'description': 'Master bibliography and references',
        'duration': '2 minutes',
        'steps': [
            {
                'title': 'Citation Styles',
                'content': 'Supported styles:\n- APA\n- MLA\n- Chicago\n- BibTeX',
                'action': 'Choose your preferred style'
            },
            {
                'title': 'Auto-Extract',
                'content': 'Extract citations from PDFs automatically!\nThe system reads metadata and creates proper citations.',
                'action': 'Extract a citation from PDF'
            },
            {
                'title': 'Bibliography',
                'content': 'Generate bibliography from all your citations.\nClick "Generate Bibliography" in Writing mode.',
                'action': 'Generate a bibliography'
            }
        ]
    },
    'video_editing': {
        'title': 'Advanced Video Editing',
        'description': 'Create videos from prompts',
        'duration': '5 minutes',
        'steps': [
            {
                'title': 'Futuristic Remix',
                'content': 'Create a complete themed video:\n1. Load video\n2. Select theme\n3. Click "Create Futuristic Remix"\nSystem applies effects, gradients, and titles!',
                'action': 'Start a remix'
            },
            {
                'title': 'AI Images',
                'content': 'Generate theme-based gradient images.\nThese overlay on your video for visual effects.',
                'action': 'Generate AI images'
            },
            {
                'title': 'Segment Export',
                'content': 'Export individual segments with themes applied.\nPerfect for creating highlight reels!',
                'action': 'Export a themed segment'
            },
            {
                'title': 'Video Creation',
                'content': 'Create videos from prompts and assets!\nCombine videos, images, and text into 1-20 minute videos.',
                'action': 'Learn about VideoCreator API'
            }
        ]
    }
}

def get_tutorial(tutorial_id: str) -> Optional[Dict[str, Any]]:
    """Get tutorial by ID."""
    return TUTORIALS.get(tutorial_id)

def get_all_tutorials() -> Dict[str, Dict[str, Any]]:
    """Get all tutorials."""
    return TUTORIALS
