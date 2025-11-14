# Onboarding System Testing Guide

## Quick Test Commands

```bash
# 1. Test basic imports (without PyQt6)
python3 -c "from modules.onboarding import OnboardingManager; print('✓ Onboarding imports OK')"
python3 -c "from modules.sample_data import SampleDataGenerator; print('✓ Sample data imports OK')"

# 2. Test OnboardingManager functionality
python3 -c "
from modules.onboarding import OnboardingManager, get_all_tutorials
mgr = OnboardingManager()
print(f'✓ First run: {mgr.is_first_run()}')
print(f'✓ Tutorials available: {len(get_all_tutorials())}')
print('✓ OnboardingManager OK')
"

# 3. Test sample data generation
python3 -c "
from modules.sample_data import SampleDataGenerator
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    gen = SampleDataGenerator(Path(tmp))
    gen.generate_quickstart_guide(Path(tmp))
    print('✓ Sample data generation OK')
"

# 4. Full desktop app test (requires PyQt6)
python3 run_desktop.py
```

## Manual Testing Checklist

### 1. First-Run Experience

#### Reset First Run Status
```bash
# Clear onboarding data to test fresh installation
rm -rf ~/.b3assistant/
echo "✓ Onboarding data cleared"
```

#### Launch Desktop App
```bash
python3 run_desktop.py
```

**Expected Behavior**:
- [ ] Onboarding wizard appears automatically
- [ ] Wizard has 5 pages
- [ ] Cannot proceed without required fields
- [ ] Can navigate back and forth between pages
- [ ] Workspace directory can be customized
- [ ] Sample data checkbox is visible
- [ ] Wizard completes successfully
- [ ] Desktop app launches after wizard

#### Wizard Page 1: Welcome
- [ ] Welcome message displays
- [ ] Feature overview visible
- [ ] "Next" button works

#### Wizard Page 2: User Info
- [ ] Name field is editable
- [ ] Use case dropdown has 4 options (Academic, Professional, Personal, Creative)
- [ ] Cannot proceed without name
- [ ] Previous button works

#### Wizard Page 3: Preferences
- [ ] Citation style dropdown shows: APA, MLA, Chicago, Harvard
- [ ] Video theme dropdown shows: Neon Cyberpunk, Matrix, Tron, Blade Runner, Synthwave
- [ ] Auto-save checkbox works
- [ ] Line numbers checkbox works
- [ ] Word wrap checkbox works
- [ ] All preferences are saved

#### Wizard Page 4: Workspace
- [ ] Default workspace path shown: ~/B3Workspace
- [ ] Browse button opens directory selector
- [ ] Custom path can be entered
- [ ] "Create sample data" checkbox visible
- [ ] Sample data description shown

#### Wizard Page 5: Completion
- [ ] Summary of settings shown
- [ ] Next steps information visible
- [ ] "Finish" button completes wizard

### 2. Workspace Creation

After completing wizard:

```bash
# Check workspace structure
ls -la ~/B3Workspace/
```

**Expected Structure**:
- [ ] `Research/` directory exists
- [ ] `Notes/` directory exists
- [ ] `Drafts/` directory exists
- [ ] `Videos/` directory exists
- [ ] `Assets/` directory exists with subdirectories:
  - [ ] `Assets/videos/`
  - [ ] `Assets/images/`
  - [ ] `Assets/audio/`
  - [ ] `Assets/texts/`
- [ ] `Exports/` directory exists

**If sample data was enabled**:
- [ ] `QuickStart.md` file exists
- [ ] `Research/sample_chapter.md` exists
- [ ] `Notes/sample_note.md` exists

### 3. Preferences Persistence

```bash
# Check preferences file
cat ~/.b3assistant/preferences.json
```

**Expected**:
- [ ] File exists
- [ ] Valid JSON format
- [ ] Contains `name` field
- [ ] Contains `use_case` field
- [ ] Contains `citation_style` field
- [ ] Contains `video_theme` field
- [ ] Contains `workspace_path` field
- [ ] Contains `completed_tutorials` array

```bash
# Verify preferences persist across launches
python3 run_desktop.py  # Launch again - wizard should NOT appear
```

- [ ] Wizard does not appear on second launch
- [ ] User name is remembered
- [ ] Preferences are loaded

### 4. Interactive Tutorials

From the desktop app:

#### Access Tutorials
- [ ] Help menu exists
- [ ] "📚 Interactive Tutorials" menu item visible
- [ ] Clicking opens tutorial list dialog

#### Tutorial List Dialog
- [ ] Shows all 7 tutorials:
  1. Getting Started (5 minutes)
  2. Research Mode (7 minutes)
  3. Writing Mode (8 minutes)
  4. Video Editing (10 minutes)
  5. AI Agents (6 minutes)
  6. Video Creation (10 minutes)
  7. Organization & Workflow (8 minutes)
- [ ] Each tutorial shows duration
- [ ] Completion status shows (✓ for completed)
- [ ] Overall progress percentage displayed
- [ ] Double-click opens tutorial
- [ ] "Start Tutorial" button works
- [ ] "Close" button works

#### Individual Tutorial Dialog
- [ ] Tutorial title displayed
- [ ] Step X of Y shown
- [ ] Progress bar updates
- [ ] Content area shows step description
- [ ] Action hint area shows what to do
- [ ] "Previous" button works (except on first step)
- [ ] "Next" button works
- [ ] "Skip" button works
- [ ] Final step has "Complete" instead of "Next"
- [ ] Completion marks tutorial as done

#### Test Tutorial Completion
```python
# Run this to check tutorial tracking
python3 << 'EOF'
from modules.onboarding import OnboardingManager

mgr = OnboardingManager()
print(f"Completion: {mgr.get_completion_percentage()}%")
print(f"Completed: {mgr.preferences.completed_tutorials}")
print(f"Next tutorial: {mgr.get_next_tutorial()}")
print(f"Uncompleted: {mgr.get_uncompleted_tutorials()}")
EOF
```

### 5. Quick Start Guide

From the desktop app:

- [ ] Help menu has "🚀 Quick Start Guide" item
- [ ] Clicking opens QuickStart.md in Writing mode
- [ ] File loads in Markdown editor
- [ ] Preview shows formatted content
- [ ] If file doesn't exist, shows helpful message

### 6. Sample Data Content

Check generated files:

```bash
# View sample chapter
cat ~/B3Workspace/Research/sample_chapter.md

# View sample note
cat ~/B3Workspace/Notes/sample_note.md

# View quick start
cat ~/B3Workspace/QuickStart.md
```

**Verify**:
- [ ] Sample chapter has academic content
- [ ] Sample chapter has proper Markdown formatting
- [ ] Sample note follows Zettelkasten format
- [ ] Sample note has metadata, content, links
- [ ] Quick start has comprehensive guide
- [ ] Quick start covers all modes
- [ ] Quick start has keyboard shortcuts
- [ ] Quick start has troubleshooting section

### 7. Edge Cases & Error Handling

#### Test with Invalid Data

```python
# Test with invalid workspace path
python3 << 'EOF'
from modules.onboarding import OnboardingManager
from pathlib import Path

mgr = OnboardingManager()
mgr.preferences.workspace_path = "/nonexistent/invalid/path"

try:
    workspace = mgr.create_workspace(Path("/nonexistent/invalid/path"))
    print("ERROR: Should have failed")
except Exception as e:
    print(f"✓ Correctly handled invalid path: {type(e).__name__}")
EOF
```

#### Test Wizard Cancellation
- [ ] Click "Cancel" on wizard
- [ ] App should close gracefully
- [ ] First run file should NOT be created
- [ ] Wizard appears again on next launch

#### Test Tutorial Skip
- [ ] Start a tutorial
- [ ] Click "Skip" button
- [ ] Tutorial closes
- [ ] Tutorial is NOT marked as completed
- [ ] Can restart the same tutorial

#### Test Rapid Tutorial Completion
- [ ] Open tutorial
- [ ] Click "Next" repeatedly without reading
- [ ] Should work smoothly
- [ ] Last step should show "Complete"
- [ ] Completing marks tutorial as done

### 8. Import Isolation Tests

#### Test Without PyQt6 (Lazy Import Validation)

```bash
# Create a virtual environment without PyQt6
python3 -m venv test_env
source test_env/bin/activate
pip install dataclasses pathlib

# Test core modules work without GUI
python3 << 'EOF'
# This should work even without PyQt6
from modules.onboarding import OnboardingManager, UserPreferences, get_all_tutorials
from modules.sample_data import SampleDataGenerator, generate_sample_data_for_onboarding

print("✓ Core modules import without PyQt6")

mgr = OnboardingManager()
print(f"✓ OnboardingManager created: {mgr.is_first_run()}")

tutorials = get_all_tutorials()
print(f"✓ Tutorials loaded: {len(tutorials)}")

gen = SampleDataGenerator()
print(f"✓ SampleDataGenerator created")
EOF

# This should fail gracefully
python3 -c "from interfaces.desktop_app.dialogs.onboarding_wizard import OnboardingWizard" 2>&1 | grep -q "No module named 'PyQt6'" && echo "✓ PyQt6 import fails as expected"

deactivate
```

#### Test Lazy Import Behavior

```python
# Verify lazy imports don't load modules eagerly
python3 << 'EOF'
import sys

# Import interfaces package
import interfaces

# Check that gui_launcher is NOT loaded yet
assert 'interfaces.gui_launcher' not in sys.modules, "ERROR: gui_launcher loaded eagerly!"
print("✓ gui_launcher not loaded eagerly")

# Now actually use it - should load on demand
try:
    launch_gui = interfaces.launch_gui
    print("✓ Lazy import of launch_gui works (though may fail if tkinter missing)")
except ModuleNotFoundError as e:
    print(f"✓ Lazy import attempted correctly: {e}")

# Check desktop_app
import interfaces.desktop_app
assert 'interfaces.desktop_app.main_window' not in sys.modules, "ERROR: main_window loaded eagerly!"
print("✓ main_window not loaded eagerly")
EOF
```

### 9. Integration Tests

#### Test Desktop App Modes

With desktop app running:

**Research Mode**:
- [ ] Can switch to Research mode
- [ ] PDF panel loads
- [ ] Can import a PDF (drag & drop or button)
- [ ] AI panel accessible
- [ ] Can ask research questions

**Video Mode**:
- [ ] Can switch to Video mode
- [ ] Video panel loads
- [ ] Can load a video file
- [ ] Theme selector shows 5 themes
- [ ] Can mark segments
- [ ] Export buttons work
- [ ] Can create remix

**Writing Mode**:
- [ ] Can switch to Writing mode
- [ ] Editor loads
- [ ] Can type Markdown
- [ ] Preview updates in real-time
- [ ] Can export to PDF/Word/HTML
- [ ] AI panel provides writing assistance

#### Test Keyboard Shortcuts

- [ ] Ctrl+1 switches to Research mode
- [ ] Ctrl+2 switches to Video mode
- [ ] Ctrl+3 switches to Writing mode
- [ ] Ctrl+Space focuses AI chat
- [ ] Ctrl+S saves current work (if auto-save disabled)

### 10. Performance Tests

#### Startup Time
```bash
time python3 run_desktop.py
```
- [ ] App launches in < 5 seconds
- [ ] Wizard (if first run) appears quickly
- [ ] No visible lag or freezing

#### Tutorial Navigation
- [ ] Switching between tutorial steps is instant
- [ ] No lag when opening tutorial list
- [ ] Progress updates immediately

#### Sample Data Generation
```bash
time python3 << 'EOF'
from modules.sample_data import generate_sample_data_for_onboarding
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    generate_sample_data_for_onboarding(Path(tmp))
EOF
```
- [ ] Completes in < 2 seconds
- [ ] All files created successfully

### 11. Data Persistence Tests

```bash
# Complete some tutorials, then check persistence
python3 << 'EOF'
from modules.onboarding import OnboardingManager

# First session - mark tutorial complete
mgr1 = OnboardingManager()
mgr1.mark_tutorial_complete('getting_started')
mgr1.save_tutorial_status()
print(f"Session 1: {mgr1.preferences.completed_tutorials}")

# Second session - verify persistence
mgr2 = OnboardingManager()
print(f"Session 2: {mgr2.preferences.completed_tutorials}")
assert 'getting_started' in mgr2.preferences.completed_tutorials
print("✓ Tutorial completion persists across sessions")
EOF
```

#### Preferences Update Test
```python
python3 << 'EOF'
from modules.onboarding import OnboardingManager

mgr = OnboardingManager()
mgr.preferences.name = "Test User"
mgr.preferences.citation_style = "mla"
mgr.save_preferences()

# Reload
mgr2 = OnboardingManager()
assert mgr2.preferences.name == "Test User"
assert mgr2.preferences.citation_style == "mla"
print("✓ Preferences persist correctly")
EOF
```

### 12. Cleanup & Reset Tests

```bash
# Test reset functionality
python3 << 'EOF'
from modules.onboarding import OnboardingManager

mgr = OnboardingManager()
mgr.preferences.name = "Original Name"
mgr.save_preferences()

# Reset
mgr.reset_preferences()

# Verify reset
mgr2 = OnboardingManager()
assert mgr2.preferences.name == ""
print("✓ Reset preferences works")
EOF
```

## Automated Test Suite

Create `tests/test_onboarding.py`:

```python
import unittest
import tempfile
from pathlib import Path
from modules.onboarding import OnboardingManager, UserPreferences, get_all_tutorials
from modules.sample_data import SampleDataGenerator

class TestOnboardingSystem(unittest.TestCase):
    def setUp(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".b3assistant"
        self.manager = OnboardingManager(self.config_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_first_run_detection(self):
        """Test first run detection."""
        self.assertTrue(self.manager.is_first_run())
        self.manager.mark_first_run_complete()
        self.assertFalse(self.manager.is_first_run())

    def test_preferences_persistence(self):
        """Test preference saving and loading."""
        self.manager.preferences.name = "Test User"
        self.manager.preferences.citation_style = "mla"
        self.manager.save_preferences()

        # Create new manager to test loading
        manager2 = OnboardingManager(self.config_dir)
        self.assertEqual(manager2.preferences.name, "Test User")
        self.assertEqual(manager2.preferences.citation_style, "mla")

    def test_tutorial_tracking(self):
        """Test tutorial completion tracking."""
        self.assertFalse(self.manager.is_tutorial_completed('getting_started'))

        self.manager.mark_tutorial_complete('getting_started')
        self.assertTrue(self.manager.is_tutorial_completed('getting_started'))

        progress = self.manager.get_completion_percentage()
        self.assertGreater(progress, 0)
        self.assertLessEqual(progress, 100)

    def test_workspace_creation(self):
        """Test workspace directory creation."""
        workspace = self.manager.create_workspace(Path(self.temp_dir) / "workspace")

        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / "Research").exists())
        self.assertTrue((workspace / "Notes").exists())
        self.assertTrue((workspace / "Drafts").exists())
        self.assertTrue((workspace / "Videos").exists())
        self.assertTrue((workspace / "Assets").exists())
        self.assertTrue((workspace / "Exports").exists())

    def test_all_tutorials_loaded(self):
        """Test that all 7 tutorials are available."""
        tutorials = get_all_tutorials()
        self.assertEqual(len(tutorials), 7)

        # Check specific tutorials exist
        expected_ids = [
            'getting_started', 'research_mode', 'writing_mode',
            'video_editing', 'ai_agents', 'video_creation',
            'organization_workflow'
        ]
        for tutorial_id in expected_ids:
            self.assertIn(tutorial_id, tutorials)

    def test_sample_data_generation(self):
        """Test sample data generation."""
        workspace = Path(self.temp_dir) / "workspace"
        workspace.mkdir()

        generator = SampleDataGenerator(workspace)

        # Test each generation function
        quickstart = generator.generate_quickstart_guide(workspace)
        self.assertTrue(Path(quickstart).exists())

        sample_md = generator.generate_sample_markdown(workspace / "Research")
        self.assertTrue(Path(sample_md).exists())

        sample_note = generator.generate_sample_notes(workspace / "Notes")
        self.assertTrue(Path(sample_note).exists())

    def test_preferences_reset(self):
        """Test preferences reset."""
        self.manager.preferences.name = "Test User"
        self.manager.save_preferences()

        self.manager.reset_preferences()

        # Reload and verify
        manager2 = OnboardingManager(self.config_dir)
        self.assertEqual(manager2.preferences.name, "")

    def test_next_tutorial(self):
        """Test next tutorial suggestion."""
        # Initially should suggest first tutorial
        next_tut = self.manager.get_next_tutorial()
        self.assertIsNotNone(next_tut)

        # Complete all tutorials
        for tutorial_id in get_all_tutorials().keys():
            self.manager.mark_tutorial_complete(tutorial_id)

        # Should return None when all complete
        next_tut = self.manager.get_next_tutorial()
        self.assertIsNone(next_tut)

if __name__ == '__main__':
    unittest.main()
```

Run the automated tests:

```bash
python3 -m pytest tests/test_onboarding.py -v
# or
python3 tests/test_onboarding.py
```

## Test Report Template

After testing, document results:

```markdown
# Onboarding System Test Report

**Date**: [DATE]
**Tester**: [NAME]
**Version**: [COMMIT HASH]

## Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Success Rate: Y/X%

## Test Results

### First-Run Experience: ✓ PASS / ✗ FAIL
- Notes: [Any issues or observations]

### Workspace Creation: ✓ PASS / ✗ FAIL
- Notes:

### Tutorials: ✓ PASS / ✗ FAIL
- Notes:

### Preferences: ✓ PASS / ✗ FAIL
- Notes:

### Sample Data: ✓ PASS / ✗ FAIL
- Notes:

### Edge Cases: ✓ PASS / ✗ FAIL
- Notes:

## Issues Found
1. [Issue description]
2. [Issue description]

## Recommendations
- [Improvement suggestions]
```

## Common Issues & Solutions

### Issue: Wizard doesn't appear
**Solution**: Delete `~/.b3assistant/first_run.json` and relaunch

### Issue: Tutorials not loading
**Check**:
```bash
python3 -c "from modules.onboarding import get_all_tutorials; print(len(get_all_tutorials()))"
```

### Issue: Sample data not generated
**Check**:
```bash
ls -la ~/B3Workspace/
cat ~/B3Workspace/QuickStart.md
```

### Issue: Import errors
**Solution**: Install dependencies:
```bash
pip install -r requirements-desktop.txt
```

## Quick Validation Script

Save this as `validate_onboarding.sh`:

```bash
#!/bin/bash

echo "=== Onboarding System Validation ==="
echo

# Test 1: Module imports
echo "Test 1: Module imports..."
python3 -c "from modules.onboarding import OnboardingManager; from modules.sample_data import SampleDataGenerator" && echo "✓ PASS" || echo "✗ FAIL"

# Test 2: Tutorial loading
echo "Test 2: Tutorial loading..."
python3 -c "from modules.onboarding import get_all_tutorials; assert len(get_all_tutorials()) == 7" && echo "✓ PASS" || echo "✗ FAIL"

# Test 3: OnboardingManager
echo "Test 3: OnboardingManager..."
python3 -c "from modules.onboarding import OnboardingManager; mgr = OnboardingManager(); assert hasattr(mgr, 'is_first_run')" && echo "✓ PASS" || echo "✗ FAIL"

# Test 4: Sample data generation
echo "Test 4: Sample data generation..."
python3 -c "from modules.sample_data import SampleDataGenerator; gen = SampleDataGenerator()" && echo "✓ PASS" || echo "✗ FAIL"

# Test 5: Lazy imports
echo "Test 5: Lazy imports..."
python3 -c "import interfaces; import interfaces.desktop_app" && echo "✓ PASS" || echo "✗ FAIL"

echo
echo "=== Validation Complete ==="
```

Make executable and run:
```bash
chmod +x validate_onboarding.sh
./validate_onboarding.sh
```
