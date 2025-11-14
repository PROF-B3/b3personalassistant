"""
Sample Data Generator

Creates sample files and data for onboarding and tutorials.
"""

import os
from pathlib import Path
from typing import Optional
import logging

class SampleDataGenerator:
    """
    Generate sample data for onboarding.

    Creates sample PDFs, Markdown files, and demonstrates system features.
    """

    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        Initialize sample data generator.

        Args:
            workspace_dir: Workspace directory (default: ~/B3Workspace)
        """
        self.logger = logging.getLogger("sample_data")

        if workspace_dir is None:
            self.workspace_dir = Path.home() / "B3Workspace"
        else:
            self.workspace_dir = Path(workspace_dir)

        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def generate_sample_markdown(self) -> str:
        """
        Generate sample Markdown document.

        Returns:
            Path to created file
        """
        content = """# My First Document

Welcome to B3 Personal Assistant!

## Introduction

This is a sample Markdown document to help you get started. You can:

- **Bold text** with `**bold**`
- *Italic text* with `*italic*`
- `Code snippets` with backticks
- [Links](https://example.com) with `[text](url)`

## Features

### Lists

Numbered lists:
1. First item
2. Second item
3. Third item

Bullet lists:
- Research papers
- Write documents
- Edit videos

### Code Blocks

```python
def hello_world():
    print("Hello from B3!")
```

### Quotes

> "The best way to predict the future is to invent it."
> - Alan Kay

## Citations

You can insert citations like this: [@Smith2023]

Then generate a bibliography at the end!

## Next Steps

1. Try editing this text
2. Watch the live preview
3. Export to Word or LaTeX
4. Insert citations
5. Generate bibliography

Happy writing!
"""

        file_path = self.workspace_dir / "Documents" / "GettingStarted.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Created sample Markdown: {file_path}")
        return str(file_path)

    def generate_sample_notes(self) -> str:
        """
        Generate sample note for Zettelkasten.

        Returns:
            Path to created file
        """
        content = """# Sample Research Note

#research #methodology #example

## Main Idea

This is a sample Zettelkasten note demonstrating linked thinking.

## Key Points

- Notes are atomic (one idea per note)
- Use backlinks to connect ideas: [[Related Note]]
- Tags help with organization: #topic #subtopic
- Markdown formatting makes notes readable

## Related Concepts

- [[Literature Review Process]]
- [[Citation Management]]
- [[Writing Workflow]]

## References

Smith, J. (2023). *Academic Writing Made Easy*. Academic Press.

## Metadata

Created: 2024-01-15
Updated: 2024-01-15
Status: Active
"""

        file_path = self.workspace_dir / "Notes" / "Sample_Note.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Created sample note: {file_path}")
        return str(file_path)

    def generate_quickstart_guide(self) -> str:
        """
        Generate quick start guide.

        Returns:
            Path to created file
        """
        content = """# B3 Personal Assistant - Quick Start Guide

Welcome! This guide will get you started in 5 minutes.

## 🚀 Quick Start (5 Minutes)

### Step 1: Choose Your Mode (30 seconds)

Use the mode dropdown or keyboard shortcuts:
- **Ctrl+1**: Research Mode (PDFs)
- **Ctrl+2**: Video Mode (videos)
- **Ctrl+3**: Writing Mode (Markdown)

### Step 2: Import a File (1 minute)

**Option A**: Drag & Drop
- Drag any file into the file tree
- It will open in the appropriate mode

**Option B**: File Menu
- File → Open (Ctrl+O)
- Select your file

### Step 3: Try a Feature (2 minutes)

**Research Mode:**
1. Open a PDF
2. Click "Extract Citation"
3. Click "Create Note"

**Writing Mode:**
1. Create new .md file
2. Type some text
3. Watch live preview!

**Video Mode:**
1. Load a video
2. Mark a segment ([ Mark Start → Mark End ])
3. Select a theme
4. Export!

### Step 4: Use AI Agents (1 minute)

1. Press **Ctrl+Space** to focus chat
2. Select an agent (try Beta for research)
3. Ask a question!

### Step 5: Explore (30 seconds)

- Check out keyboard shortcuts (Help → Shortcuts)
- Browse the 7 AI agents
- Try different themes in Video mode

## 📚 Common Tasks

### Working with PDFs
```
1. Open PDF (Ctrl+O)
2. Extract Citation (Ctrl+Shift+C)
3. Search Related Papers (Ctrl+Shift+F)
4. Create Note from PDF
5. Generate Bibliography (Ctrl+Shift+B)
```

### Writing Documents
```
1. Create .md file (Ctrl+N)
2. Use formatting toolbar
3. Insert citations: [@AuthorYear]
4. Generate bibliography
5. Export to Word/LaTeX (Ctrl+E)
```

### Editing Videos
```
1. Load video
2. Mark segments ([ Mark Start, Mark End ])
3. Select theme
4. Export:
   - Single segment
   - Full video with theme
   - Futuristic remix (full pipeline!)
```

## 🎨 5 Video Themes

- **Neon Cyberpunk**: Cyan/magenta, tech vibes
- **Green Solarpunk**: Eco-friendly, nature
- **Cosmic Voyage**: Space, deep blue
- **AI Consciousness**: Neural networks, digital
- **Bio Evolution**: DNA, bioluminescent green

## 🤖 The 7 Agents

1. **Alpha (Α)**: Chief coordinator, project planning
2. **Beta (Β)**: Research analyst, data gathering
3. **Gamma (Γ)**: Knowledge manager, documentation
4. **Delta (Δ)**: Optimizer, performance
5. **Epsilon (Ε)**: Creative director, writing help
6. **Zeta (Ζ)**: Technical specialist
7. **Eta (Η)**: Monitor, performance tracking

## ⌨️ Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+1 | Research mode |
| Ctrl+2 | Video mode |
| Ctrl+3 | Writing mode |
| Ctrl+Space | Focus AI chat |
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+E | Export |
| Ctrl+B | Toggle sidebar |
| Ctrl+J | Toggle chat panel |

## 💡 Pro Tips

1. **Drag & Drop**: Fastest way to import files
2. **Keyboard Navigation**: Faster than mouse
3. **AI Agents**: Don't hesitate to ask for help
4. **Auto-Save**: Enabled by default
5. **Themes**: Try all 5 video themes!

## 📖 Documentation

- **Full Guide**: See DESKTOP_APP_COMPLETE.md
- **Video Editing**: See VIDEO_EDITING_GUIDE.md
- **Help Menu**: Help → Keyboard Shortcuts

## 🎯 Next Steps

1. Complete the interactive tutorials
2. Set up your workspace structure
3. Import your first real file
4. Try each of the 3 modes
5. Experiment with AI agents

## 🆘 Need Help?

- Interactive tutorials: Help → Tutorials
- Keyboard shortcuts: Help → Shortcuts (F1)
- Documentation: See markdown files in project root
- Agent chat: Ask any agent for help!

---

**You're all set!** Start by opening a file or creating a new document.

Press Ctrl+1, Ctrl+2, or Ctrl+3 to choose your mode and begin!
"""

        file_path = self.workspace_dir / "QuickStart.md"

        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Created quick start guide: {file_path}")
        return str(file_path)

    def generate_all_samples(self) -> dict:
        """
        Generate all sample data.

        Returns:
            Dictionary with paths to created files
        """
        return {
            'markdown': self.generate_sample_markdown(),
            'note': self.generate_sample_notes(),
            'quickstart': self.generate_quickstart_guide()
        }

    def create_sample_video_assets(self):
        """Create placeholders for video assets."""
        assets_dir = self.workspace_dir / "Assets"

        # Create README for video assets
        readme_path = assets_dir / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write("""# Video Assets

Place your video assets here for easy access.

## Structure

- **videos/**: Video clips for editing
- **images/**: Images for slideshows and overlays
- **audio/**: Background music and audio files

## Usage

These assets will be available in:
- Video Mode for editing
- VideoCreator API for prompt-based creation
- Slideshow creator

## Recommended Formats

**Videos**: MP4, AVI, MOV, MKV
**Images**: JPG, PNG, GIF
**Audio**: MP3, WAV, M4A

## Tips

- Organize by project
- Use descriptive filenames
- Keep originals backed up
- Test assets before big projects

Happy creating!
""")

        self.logger.info(f"Created video assets structure: {assets_dir}")

def generate_sample_data_for_onboarding(workspace_dir: Optional[Path] = None) -> dict:
    """
    Convenience function to generate all sample data.

    Args:
        workspace_dir: Workspace directory

    Returns:
        Dictionary with paths to created files
    """
    generator = SampleDataGenerator(workspace_dir)
    return generator.generate_all_samples()
