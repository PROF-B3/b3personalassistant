# B3 Personal Assistant - Desktop App

Minimal, efficient desktop application for dissertation and video work.

## Status

**Phase 1: Core Infrastructure** ✅ Complete
- Main window with menu bar
- Mode switcher (Research/Video/Writing)
- 2-panel layout (sidebar + workspace)
- Agent chat panel
- Status bar with resource monitoring
- Keyboard shortcuts
- Clean dark theme (VS Code inspired)

**Phase 2-4:** In Progress
- File tree panel
- PDF viewer
- Markdown editor
- Video player
- Citation management UI
- Export dialogs

## Installation

### Dependencies

```bash
# Install desktop app dependencies
pip install -r requirements-desktop.txt
```

### Key Dependencies:
- **PyQt6** - GUI framework
- **PyMuPDF** - PDF viewing
- **MoviePy** - Video editing
- **python-docx** - Word export

## Running the App

```bash
python run_desktop_app.py
```

## Features

### Three Modes

**1. Research Mode** (Ctrl+1)
- PDF viewer with annotations
- Citation extraction
- Bibliography management
- Paper search
- Export citations

**2. Video Mode** (Ctrl+2)
- Video player with timeline
- Segment cutting
- Theme application (5 futuristic themes)
- AI image generation
- Export segments

**3. Writing Mode** (Ctrl+3)
- Markdown editor
- Live preview
- Citation insertion
- Word count
- Export to Word/LaTeX

### Keyboard Shortcuts

**Mode Switching:**
- `Ctrl+1` - Research mode
- `Ctrl+2` - Video mode
- `Ctrl+3` - Writing mode

**Navigation:**
- `Ctrl+B` - Toggle sidebar
- `Ctrl+J` - Toggle chat panel
- `Ctrl+Space` - Focus agent chat

**File Operations:**
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+E` - Export

**Research:**
- `Ctrl+Shift+F` - Search papers
- `Ctrl+Shift+C` - Extract citation
- `Ctrl+Shift+B` - Generate bibliography

**Video:**
- `Ctrl+K` - Cut segment

## Architecture

```
interfaces/desktop_app/
├── main_window.py          # Main application window
├── panels/                 # UI panels
│   ├── file_tree_panel.py
│   ├── agent_panel.py
│   ├── pdf_viewer_panel.py
│   ├── video_player_panel.py
│   └── markdown_editor_panel.py
├── widgets/                # Reusable widgets
│   ├── citation_browser.py
│   ├── bibliography_view.py
│   └── timeline.py
├── dialogs/                # Dialogs
│   ├── paper_search_dialog.py
│   ├── export_dialog.py
│   └── theme_selector.py
├── models/                 # Data models
│   ├── file_model.py
│   └── citation_model.py
└── utils/                  # Utilities
    ├── theme.py            # Styling
    └── shortcuts.py        # Keyboard shortcuts
```

## Design Philosophy

**Minimal & Efficient:**
- One window, one task at a time
- Mode-based workspace (auto-switches by file type)
- Keyboard-first navigation
- Clean, fast, focused

**80/20 Principle:**
- Core features only
- No feature bloat
- Workflow over features

## Workflow

### Research Workflow
```
Open PDF → Extract citation → Add to bibliography → Create notes → Export
```

### Writing Workflow
```
Create Markdown → Write with citations → Preview → Export to Word/LaTeX
```

### Video Workflow
```
Import video → Cut segments → Apply themes → Generate images → Export
```

## Backend Integration

The desktop app connects directly to:
- **Orchestrator** - Agent coordination
- **Academic Search** - Paper search (arXiv, CrossRef, Semantic Scholar)
- **Citation Manager** - Bibliography management
- **Document Export** - Word/LaTeX export
- **Video Processor** - Video editing
- **Zettelkasten** - Knowledge management

All 7 agents accessible via chat panel:
- Alpha (Α) - Chief Coordinator
- Beta (Β) - Research Analyst
- Gamma (Γ) - Knowledge Manager
- Delta (Δ) - Task Coordinator
- Epsilon (Ε) - Creative Director
- Zeta (Ζ) - Code Architect
- Eta (Η) - Evolution Engineer

## Next Steps

1. **File Tree Panel** - Browse files, drag-and-drop import
2. **PDF Viewer** - View PDFs with PyMuPDF
3. **Citation UI** - Browse and manage bibliography
4. **Markdown Editor** - Write with syntax highlighting
5. **Video Player** - Play and edit videos
6. **Export Dialogs** - Export to various formats

## Timeline

- **Week 1:** Research + Writing modes
- **Week 2:** Video mode
- **Total:** 2 weeks for complete minimal app

## Contributing

See main CONTRIBUTING.md for development guidelines.
