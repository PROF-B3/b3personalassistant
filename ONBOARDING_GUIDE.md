# B3 Personal Assistant - Onboarding System Guide

## Overview

The B3 Personal Assistant includes a comprehensive onboarding system designed to help new users get started quickly and learn the application's features through interactive tutorials.

### Key Features

- **First-Run Wizard**: 5-page setup wizard that collects user preferences and creates workspace
- **Interactive Tutorials**: 7 step-by-step tutorials covering all major features
- **Sample Data Generation**: Automatic creation of example files for learning
- **Progress Tracking**: Monitors tutorial completion and overall progress
- **User Preferences**: Persistent settings for personalized experience
- **Quick Start Guide**: Comprehensive guide available from Help menu

## System Architecture

### Components

```
modules/
├── onboarding.py           # Core onboarding manager, preferences, tutorials
└── sample_data.py          # Sample data generation

interfaces/desktop_app/dialogs/
├── onboarding_wizard.py    # First-run wizard UI
└── tutorial_dialog.py      # Interactive tutorial UI

run_desktop.py              # Checks first run and launches wizard
```

### Data Storage

User data is stored in `~/.b3assistant/`:
- `first_run.json` - Marks first run as complete
- `preferences.json` - User preferences and settings
- `tutorial_status.json` - Tutorial completion tracking

## First-Run Wizard

### Wizard Pages

#### 1. Welcome Page
- Introduction to B3 Personal Assistant
- Overview of features
- Set completion percentage for continuation

#### 2. User Info Page
- **Name**: User's name for personalization
- **Use Case**: Primary use (Academic, Professional, Personal, Creative)
- Required fields for continuation

#### 3. Preferences Page
- **Citation Style**: APA, MLA, Chicago, Harvard
- **Video Theme**: Default theme for video editing
- **Auto-save**: Enable automatic saving
- **Line Numbers**: Show line numbers in editor
- **Word Wrap**: Enable word wrapping

#### 4. Workspace Page
- **Workspace Path**: Location for B3Workspace directory
- **Create Sample Data**: Option to generate example files
- Creates workspace structure automatically

#### 5. Completion Page
- Summary of setup
- Next steps
- Tutorial suggestions

### Workspace Structure

When created, the workspace includes:

```
~/B3Workspace/
├── Research/              # Research papers and PDFs
├── Notes/                 # Markdown notes and Zettelkasten
├── Drafts/                # Writing drafts
├── Videos/                # Video files for editing
├── Assets/                # Video creation assets
│   ├── videos/
│   ├── images/
│   ├── audio/
│   └── texts/
├── Exports/               # Exported content
└── QuickStart.md          # Quick start guide
```

### Sample Data

If enabled, the wizard generates:
- **Sample Markdown Document**: Example dissertation chapter
- **Sample Notes**: Zettelkasten-style note example
- **Quick Start Guide**: Comprehensive usage guide
- **Asset Directories**: Organized folders for video creation

## Interactive Tutorial System

### Available Tutorials

#### 1. Getting Started (5 minutes)
- Interface overview
- Mode switching
- Basic navigation
- File operations

#### 2. Research Mode (7 minutes)
- Opening PDFs
- Viewing research papers
- Taking notes while reading
- Organizing research files

#### 3. Writing Mode (8 minutes)
- Creating Markdown documents
- Real-time preview
- Formatting text
- Exporting to PDF/Word

#### 4. Video Editing (10 minutes)
- Loading videos
- Applying themes
- Exporting segments
- Creating remixes

#### 5. AI Agents (6 minutes)
- Agent panel
- Asking questions
- Getting research help
- Code assistance

#### 6. Video Creation (10 minutes)
- Creating videos from prompts
- Managing assets
- Using themes
- Advanced composition

#### 7. Organization & Workflow (8 minutes)
- File organization
- Workspace management
- Keyboard shortcuts
- Productivity tips

### Tutorial Features

- **Step-by-Step Navigation**: Previous/Next buttons
- **Progress Bar**: Visual progress indicator
- **Action Hints**: Clear instructions for each step
- **Skip Option**: Can skip and return later
- **Completion Tracking**: Marks tutorials as completed
- **Overall Progress**: Shows percentage across all tutorials

### Accessing Tutorials

From the desktop app:
1. **Help Menu** → "📚 Interactive Tutorials"
2. Shows list of all tutorials with completion status
3. Double-click or select and click "Start Tutorial"
4. Navigate through steps
5. Mark as complete when finished

### Tutorial Structure (API)

```python
tutorial_data = {
    'id': 'getting_started',
    'title': 'Getting Started',
    'description': 'Learn the basics...',
    'duration': '5 minutes',
    'steps': [
        {
            'title': 'Welcome!',
            'content': 'Step description...',
            'action': 'What to do next...'
        },
        # More steps...
    ]
}
```

## User Preferences System

### UserPreferences Class

```python
@dataclass
class UserPreferences:
    name: str = ""
    use_case: str = "academic"
    citation_style: str = "apa"
    video_theme: str = "neon_cyberpunk"
    auto_save: bool = True
    line_numbers: bool = True
    word_wrap: bool = True
    workspace_path: str = ""
    completed_tutorials: List[str] = field(default_factory=list)
```

### Accessing Preferences

```python
from modules.onboarding import OnboardingManager

manager = OnboardingManager()
prefs = manager.preferences

# Read preference
user_name = prefs.name
citation = prefs.citation_style

# Update preference
prefs.citation_style = "mla"
manager.save_preferences()

# Convert to dict
prefs_dict = prefs.to_dict()
```

## OnboardingManager API

### Core Methods

#### First-Run Management

```python
manager = OnboardingManager()

# Check if first run
if manager.is_first_run():
    # Show wizard
    pass

# Mark first run complete
manager.mark_first_run_complete()
```

#### Preferences

```python
# Save preferences
manager.save_preferences()

# Reset to defaults
manager.reset_preferences()
```

#### Tutorial Tracking

```python
# Mark tutorial complete
manager.mark_tutorial_complete('getting_started')

# Check if completed
is_done = manager.is_tutorial_completed('getting_started')

# Get completion percentage
progress = manager.get_completion_percentage()  # 0-100

# Get next tutorial
next_id = manager.get_next_tutorial()  # Returns ID or None

# Get uncompleted tutorials
remaining = manager.get_uncompleted_tutorials()  # List of IDs
```

#### Workspace Management

```python
# Create default workspace
workspace_path = manager.create_default_workspace()

# Create custom workspace
custom_path = manager.create_workspace('/path/to/workspace')
```

## Sample Data Generation

### SampleDataGenerator Class

```python
from modules.sample_data import SampleDataGenerator

generator = SampleDataGenerator()

# Generate sample Markdown document
doc_path = generator.generate_sample_markdown(output_dir)

# Generate sample notes
notes_path = generator.generate_sample_notes(output_dir)

# Generate quick start guide
guide_path = generator.generate_quickstart_guide(output_dir)

# Create video asset directories
generator.create_sample_video_assets(output_dir)

# Generate all sample data
generator.generate_all_samples(output_dir)
```

### Convenience Function

```python
from modules.sample_data import generate_sample_data_for_onboarding

# Generates all sample data in workspace
success = generate_sample_data_for_onboarding()
```

## Customization

### Adding New Tutorials

Edit `modules/onboarding.py` and add to `TUTORIALS` dictionary:

```python
TUTORIALS = {
    # Existing tutorials...

    'my_tutorial': {
        'id': 'my_tutorial',
        'title': 'My Custom Tutorial',
        'description': 'Learn about custom features',
        'duration': '5 minutes',
        'steps': [
            {
                'title': 'Step 1 Title',
                'content': 'Detailed step instructions...',
                'action': 'Try this action...'
            },
            # More steps...
        ]
    }
}
```

### Tutorial Order

Tutorials are shown in the order defined in the `TUTORIALS` dictionary. To change order, reorder the dictionary entries.

### Customizing Wizard Pages

Edit `interfaces/desktop_app/dialogs/onboarding_wizard.py`:

```python
# Add custom page
class CustomPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Custom Setup")
        # Add widgets...

# Add to wizard
class OnboardingWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ...
        self.addPage(CustomPage())  # Add custom page
```

### Customizing Sample Data

Edit `modules/sample_data.py` to modify generated content:

```python
class SampleDataGenerator:
    def generate_custom_sample(self, output_dir: Path) -> str:
        """Generate custom sample file."""
        content = """
        # Your custom content here
        """

        output_path = output_dir / "custom_sample.md"
        with open(output_path, 'w') as f:
            f.write(content)

        return str(output_path)
```

## Integration with Main App

### run_desktop.py Integration

```python
from modules.onboarding import OnboardingManager
from interfaces.desktop_app.dialogs.onboarding_wizard import show_onboarding_wizard

def main():
    # Create QApplication
    app = QApplication(sys.argv)

    # Check first run
    onboarding_manager = OnboardingManager()

    if onboarding_manager.is_first_run():
        wizard_completed = show_onboarding_wizard()
        if not wizard_completed:
            return 0  # User cancelled

    # Load preferences
    user_profile = onboarding_manager.preferences.to_dict()

    # Launch with profile
    return launch_desktop_app(user_profile)
```

### MainWindow Integration

```python
# In main_window.py Help menu
tutorials_action = QAction("📚 &Interactive Tutorials", self)
tutorials_action.triggered.connect(self._show_tutorials)
help_menu.addAction(tutorials_action)

quick_start_action = QAction("🚀 &Quick Start Guide", self)
quick_start_action.triggered.connect(self._show_quick_start)
help_menu.addAction(quick_start_action)

# Methods
def _show_tutorials(self):
    """Show interactive tutorials dialog."""
    from interfaces.desktop_app.dialogs.tutorial_dialog import show_tutorial_list
    show_tutorial_list(self)

def _show_quick_start(self):
    """Show quick start guide."""
    quick_start_path = Path.home() / "B3Workspace" / "QuickStart.md"
    if quick_start_path.exists():
        self._load_file_in_workspace(str(quick_start_path))
        self.mode_combo.setCurrentText("Writing")
```

## User Flow

### First-Time User Experience

1. **Launch Application**
   - `run_desktop.py` detects first run
   - Onboarding wizard appears automatically

2. **Complete Wizard**
   - Enter name and preferences
   - Choose workspace location
   - Optionally generate sample data
   - Wizard creates workspace structure

3. **Application Launches**
   - Welcome message with user's name
   - Sample data loaded (if generated)
   - Quick start guide available

4. **Explore Features**
   - Try different modes (Research, Video, Writing)
   - Access tutorials from Help menu
   - Follow interactive step-by-step guides

5. **Track Progress**
   - Complete tutorials as you learn
   - See overall completion percentage
   - Get suggestions for next tutorial

### Returning User Experience

1. **Launch Application**
   - No wizard (first run complete)
   - Preferences automatically loaded
   - Last workspace reopened

2. **Continue Learning**
   - Access tutorials from Help → Interactive Tutorials
   - See which tutorials are completed (✓)
   - Start remaining tutorials

3. **Quick Reference**
   - Open Quick Start Guide from Help menu
   - Review keyboard shortcuts
   - Check documentation

## Testing

### Manual Testing Checklist

#### First-Run Wizard
- [ ] Wizard appears on first run
- [ ] All pages load correctly
- [ ] Can navigate forward/backward
- [ ] Required fields prevent continuation
- [ ] Workspace is created successfully
- [ ] Sample data is generated when enabled
- [ ] Preferences are saved correctly
- [ ] App launches after wizard completion
- [ ] Canceling wizard exits gracefully

#### Tutorials
- [ ] Tutorial list shows all tutorials
- [ ] Completion status displays correctly
- [ ] Can start tutorial from list
- [ ] Step navigation works (Next/Previous)
- [ ] Progress bar updates correctly
- [ ] Action hints are visible
- [ ] Skip option works
- [ ] Completion is tracked
- [ ] Can access tutorials from Help menu

#### Preferences
- [ ] Preferences persist across sessions
- [ ] Citation style is applied
- [ ] Video theme default works
- [ ] Auto-save functions correctly
- [ ] Line numbers toggle works
- [ ] Word wrap toggle works

#### Sample Data
- [ ] Sample files are created in workspace
- [ ] QuickStart.md is accessible
- [ ] Sample Markdown is properly formatted
- [ ] Sample notes follow Zettelkasten format
- [ ] Asset directories are created

### Automated Testing

```python
import unittest
from pathlib import Path
from modules.onboarding import OnboardingManager, UserPreferences

class TestOnboarding(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('/tmp/test_b3')
        self.manager = OnboardingManager(self.test_dir)

    def tearDown(self):
        # Cleanup
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)

    def test_first_run(self):
        """Test first run detection."""
        self.assertTrue(self.manager.is_first_run())
        self.manager.mark_first_run_complete()
        self.assertFalse(self.manager.is_first_run())

    def test_preferences(self):
        """Test preference saving and loading."""
        self.manager.preferences.name = "Test User"
        self.manager.preferences.citation_style = "mla"
        self.manager.save_preferences()

        # Create new manager instance
        manager2 = OnboardingManager(self.test_dir)
        self.assertEqual(manager2.preferences.name, "Test User")
        self.assertEqual(manager2.preferences.citation_style, "mla")

    def test_tutorial_tracking(self):
        """Test tutorial completion tracking."""
        self.assertFalse(self.manager.is_tutorial_completed('getting_started'))

        self.manager.mark_tutorial_complete('getting_started')
        self.assertTrue(self.manager.is_tutorial_completed('getting_started'))

        progress = self.manager.get_completion_percentage()
        self.assertGreater(progress, 0)

    def test_workspace_creation(self):
        """Test workspace creation."""
        workspace = self.manager.create_workspace(self.test_dir / 'workspace')
        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / 'Research').exists())
        self.assertTrue((workspace / 'Notes').exists())

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting

### Wizard Doesn't Appear

**Problem**: Wizard doesn't show on first run

**Solutions**:
- Check if `~/.b3assistant/first_run.json` exists (delete it to reset)
- Verify `run_desktop.py` includes onboarding check
- Check console for errors

### Preferences Not Saving

**Problem**: Changes to preferences don't persist

**Solutions**:
- Verify `~/.b3assistant/` directory exists and is writable
- Check `preferences.json` file permissions
- Look for JSON serialization errors in logs

### Tutorials Not Loading

**Problem**: Tutorial list is empty or won't open

**Solutions**:
- Verify `modules/onboarding.py` defines TUTORIALS
- Check for import errors in tutorial_dialog.py
- Ensure PyQt6 is properly installed

### Sample Data Not Generated

**Problem**: Sample files aren't created

**Solutions**:
- Check workspace directory permissions
- Verify workspace path in preferences
- Look for errors in `modules/sample_data.py`

### Wizard Crashes

**Problem**: Wizard crashes during setup

**Solutions**:
- Check PyQt6 version compatibility
- Verify all wizard pages are properly initialized
- Check logs for traceback

## Best Practices

### For Users

1. **Complete Onboarding**: Take time to go through the wizard
2. **Try Tutorials**: Interactive tutorials provide hands-on learning
3. **Use Sample Data**: Generated samples show best practices
4. **Explore Modes**: Try all three modes (Research, Video, Writing)
5. **Check Help Menu**: Quick Start Guide and tutorials always available

### For Developers

1. **Keep Tutorials Updated**: Update tutorials when features change
2. **Test First-Run**: Regularly test first-run experience
3. **Validate Preferences**: Ensure preferences are properly validated
4. **Handle Errors Gracefully**: Wizard should handle missing data
5. **Provide Clear Instructions**: Tutorial steps should be actionable
6. **Track Analytics**: Consider tracking tutorial completion rates

## Future Enhancements

### Potential Improvements

1. **Video Tutorials**: Embed video walkthroughs in tutorials
2. **Interactive Hotspots**: Highlight UI elements during tutorials
3. **Contextual Help**: Show tooltips based on current action
4. **Advanced Settings**: More customization options in wizard
5. **Import/Export Preferences**: Share settings between installations
6. **Tutorial Feedback**: Let users rate tutorial helpfulness
7. **Progressive Disclosure**: Show advanced features after basics
8. **Onboarding Analytics**: Track where users struggle
9. **AI-Assisted Setup**: Use AI to recommend settings
10. **Theme Customization**: Let users customize UI theme in wizard

### Planned Features

- **Cloud Sync**: Sync preferences across devices
- **Team Onboarding**: Multi-user setup for teams
- **Custom Tutorial Creation**: Let users create their own tutorials
- **Certification**: Issue completion certificates for all tutorials
- **Achievements**: Gamify the learning experience

## Resources

### Documentation
- [README.md](README.md) - Main documentation
- [VIDEO_EDITING_GUIDE.md](VIDEO_EDITING_GUIDE.md) - Video features
- [QuickStart.md](~/B3Workspace/QuickStart.md) - User quick start

### Code Files
- `modules/onboarding.py` - Core onboarding system
- `modules/sample_data.py` - Sample data generation
- `interfaces/desktop_app/dialogs/onboarding_wizard.py` - Wizard UI
- `interfaces/desktop_app/dialogs/tutorial_dialog.py` - Tutorial UI

### Support
- GitHub Issues: Report bugs and request features
- Documentation: Check docs for detailed guides
- Help Menu: In-app help and tutorials

## Conclusion

The B3 Personal Assistant onboarding system provides a comprehensive, user-friendly introduction to the application. Through the first-run wizard, interactive tutorials, and sample data, new users can quickly become productive while learning best practices.

The system is designed to be extensible, allowing developers to easily add new tutorials, customize the wizard, and enhance the learning experience as the application evolves.

For questions or feedback, please refer to the project documentation or open an issue on GitHub.
