# B3PersonalAssistant Desktop App - Dissertation Workbench

## Vision Statement

Transform B3PersonalAssistant into a **unified dissertation workspace** where you can research papers, manage citations, organize knowledge, write chapters, and coordinate with AI agents—all in one integrated desktop application.

---

## 🎯 Core Design Principles

### 1. Workflow-First Design
Every interface element supports the dissertation lifecycle:
- **Research Phase:** Find papers → Import PDFs → Read & annotate
- **Organization Phase:** Extract citations → Create notes → Build knowledge graph
- **Writing Phase:** Draft chapters → Insert citations → Get AI assistance
- **Revision Phase:** Review → Refine → Export

### 2. Context Awareness
The app understands what you're doing and adapts:
- Reading a PDF? Show citation extraction, note creation
- Writing a chapter? Show outline, citations, AI writing help
- Organizing notes? Show Zettelkasten graph, connections

### 3. Minimal Friction
- One-click actions for common tasks
- Drag-and-drop everywhere
- Keyboard shortcuts for power users
- AI agents always accessible
- No context switching

### 4. Academic-First
- Citations are first-class citizens
- Bibliography always visible
- Reference management integrated
- Export to academic formats (LaTeX, Word)
- Structure-aware (chapters, sections, subsections)

---

## 🏗️ Application Architecture

### Technology Stack: PyQt6

**Choice Rationale:**
- Native Python integration (direct access to all modules)
- Professional desktop UI
- Cross-platform (Windows, Mac, Linux)
- Rich widget ecosystem
- Excellent PDF support via PyMuPDF
- Mature and stable

### Directory Structure
```
interfaces/
├── desktop_app/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── file_tree_panel.py  # Document explorer
│   │   ├── document_viewer.py   # PDF/document viewer
│   │   ├── editor_panel.py      # Markdown/text editor
│   │   ├── agent_panel.py       # AI agent chat
│   │   ├── bibliography_panel.py # Citation browser
│   │   ├── outline_panel.py     # Chapter/section outline
│   │   ├── notes_panel.py       # Zettelkasten notes
│   │   └── tasks_panel.py       # Task list
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── citation_browser.py  # Citation table widget
│   │   ├── pdf_viewer.py        # PDF rendering widget
│   │   ├── markdown_editor.py   # Editor with preview
│   │   ├── agent_chat.py        # Chat interface widget
│   │   └── progress_tracker.py  # Word count/progress
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── paper_search.py      # Academic search dialog
│   │   ├── export_dialog.py     # Export options
│   │   ├── settings.py          # App settings
│   │   └── quick_actions.py     # Command palette
│   ├── models/
│   │   ├── __init__.py
│   │   ├── file_model.py        # File tree data model
│   │   ├── citation_model.py    # Bibliography data model
│   │   └── outline_model.py     # Document structure model
│   └── utils/
│       ├── __init__.py
│       ├── theme.py             # Color schemes and styling
│       ├── shortcuts.py         # Keyboard shortcut manager
│       └── persistence.py       # Window state/layout saving
```

---

## 🖥️ Main Window Layout

### Primary Layout: Three-Column Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│ File  Edit  View  Research  Write  Export  Help          [―][□][×]    │
├───────────┬──────────────────────────────────────────┬──────────────────┤
│           │                                          │                  │
│  [Tabs]   │            Main Content Area            │   [Sidebar]      │
│           │                                          │                  │
│  📁 Files │   ┌──────────────────────────────────┐  │  📚 Bibliography │
│  📄 Doc1  │   │                                  │  │  ┌─────────────┐ │
│  📄 Doc2  │   │     Document Viewer/Editor       │  │  │ Smith2023   │ │
│  📑 Paper │   │                                  │  │  │ Jones2022   │ │
│           │   │                                  │  │  │ Brown2021   │ │
│  📝 Notes │   └──────────────────────────────────┘  │  └─────────────┘ │
│  ✏️ Note1 │                                          │                  │
│  ✏️ Note2 │   ┌──────────────────────────────────┐  │  📋 Outline     │
│           │   │                                  │  │  • Chapter 1    │
│  ✅ Tasks │   │     AI Agent Chat Panel          │  │    - Intro      │
│  □ Task1  │   │                                  │  │    - Background │
│  ☑ Task2  │   └──────────────────────────────────┘  │  • Chapter 2    │
│           │                                          │                  │
├───────────┴──────────────────────────────────────────┴──────────────────┤
│ Status: Ready | Agent: Alpha | Words: 2,451 | Citations: 23 | CPU: 2%  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layout Breakdown

#### Left Panel (200-300px, Resizable)
**Tabbed Interface:**
1. **📁 Files** - Project file tree
   - Folders for: PDFs, Drafts, Notes, References, Exports
   - Drag-and-drop to import
   - Context menu: Open, Extract Citation, Create Note, Export
   - Search bar at top

2. **📝 Notes** - Zettelkasten browser
   - List of all notes with IDs
   - Search and filter
   - Click to open in main area
   - Shows connections count
   - Drag to link notes

3. **✅ Tasks** - Task list
   - Today's tasks at top
   - Priority indicators
   - Click to mark complete
   - Quick add at bottom

#### Main Content Area (Flexible, Splittable)
**Two-Panel Stacked Layout:**

**Top Panel (60-80%)** - Document View/Edit
- **PDF Viewer:**
  - Render PDFs with PyMuPDF
  - Highlight and annotate
  - Quick action: "Extract Citation"
  - Sidebar thumbnails

- **Markdown Editor:**
  - Split view: edit + preview
  - Syntax highlighting
  - Auto-save
  - Word count live update
  - Quick citation insertion: `[@SmithKey]`

- **Document Preview:**
  - Preview exported Word/LaTeX
  - Read-only formatted view

**Bottom Panel (20-40%, Collapsible)** - AI Agent Chat
- Chat interface with active agent
- Agent selector dropdown
- Context indicator: "Reading paper.pdf"
- Quick actions: buttons for common commands
- Response history
- Suggested prompts based on context

#### Right Sidebar (250-350px, Resizable)
**Tabbed Interface:**

1. **📚 Bibliography** - Citation browser
   - Table view: Author, Year, Title
   - Search bar
   - Sort by: date, author, citations
   - Click to see details
   - Drag citation key to insert in editor
   - Buttons: "Add Citation", "Generate Bibliography", "Export"

2. **📋 Outline** - Document structure
   - Tree view of chapters/sections
   - Click to jump to section
   - Drag to reorder
   - Show word count per section
   - Progress bars

3. **🔍 Research** - Paper search
   - Search bar
   - Results list
   - One-click import to project
   - Save to reading list

---

## 🎨 Visual Design

### Color Scheme: Academic Dark Theme (Default)

**Background:**
- Main BG: #1E1E1E (Dark gray)
- Panel BG: #252525 (Slightly lighter)
- Sidebar BG: #2D2D2D

**Text:**
- Primary: #E0E0E0 (Light gray)
- Secondary: #A0A0A0 (Medium gray)
- Accent: #4A9EFF (Blue)
- Success: #6CC24A (Green)
- Warning: #FFA500 (Orange)
- Error: #FF4444 (Red)

**UI Elements:**
- Borders: #3E3E3E
- Highlights: #3A3A3A
- Selection: #0D47A1 (Dark blue)
- Links: #4A9EFF

### Light Theme Alternative

**Background:**
- Main BG: #FFFFFF (White)
- Panel BG: #F5F5F5
- Sidebar BG: #FAFAFA

**Text:**
- Primary: #212121
- Secondary: #666666
- Accent: #1976D2

### Typography

**Fonts:**
- Interface: Inter, SF Pro, Segoe UI (system)
- Editor: JetBrains Mono, Fira Code, Consolas (monospace)
- Sizes: 11-12pt interface, 14pt editor

---

## ⚡ Key Features & Interactions

### 1. Document Import & Management

**Drag-and-Drop PDF Import:**
```
User drags PDF → App detects → Shows dialog:
┌────────────────────────────────────────┐
│ Import PDF                             │
├────────────────────────────────────────┤
│ 📄 paper.pdf                           │
│                                        │
│ Actions:                               │
│ ☑ Extract citation metadata            │
│ ☑ Add to bibliography                  │
│ ☑ Create Zettelkasten note             │
│ ☐ Add to reading list                  │
│                                        │
│ Destination: /PDFs/                    │
│                                        │
│          [Cancel]  [Import]            │
└────────────────────────────────────────┘
```

**Automatic Processing:**
1. Copy PDF to project folder
2. Extract metadata (title, authors, year, DOI)
3. Generate citation key
4. Add to bibliography
5. Create note linked to PDF
6. Show in file tree

### 2. Citation Workflow

**One-Click Citation Insertion:**
```
Writing in editor → Type `@` → Autocomplete shows:
┌─────────────────────────────┐
│ @Smith2023                  │  ← Most recent
│ @Jones2022                  │
│ @Brown2021                  │
│ ────────────────────────── │
│ Search: [________]          │
└─────────────────────────────┘
```

**Citation Detail View:**
Click citation in bibliography →
```
┌────────────────────────────────────────────────┐
│ Smith, J., & Doe, A. (2023)                    │
├────────────────────────────────────────────────┤
│ Title: Machine Learning Applications           │
│ Year: 2023                                     │
│ Venue: Journal of AI Research, 45(2), 123-145 │
│ DOI: 10.1234/jair.2023.123                     │
│ Citations: 47                                  │
│                                                │
│ Cite Key: @Smith2023                           │
│                                                │
│ [📋 Copy BibTeX]  [🔗 Open DOI]  [📄 View PDF]│
│                                                │
│ Used in: Chapter 2, Chapter 4                  │
└────────────────────────────────────────────────┘
```

**Generate Bibliography:**
```
Write menu → "Generate Bibliography" →
┌────────────────────────────────────────┐
│ Generate Bibliography                  │
├────────────────────────────────────────┤
│ Style:   [APA 7th Edition ▾]          │
│ Format:  [BibTeX ▾]                   │
│ Filter:  [All citations ▾]            │
│                                        │
│ Preview:                               │
│ ┌────────────────────────────────────┐│
│ │ Smith, J., & Doe, A. (2023).       ││
│ │   Machine learning applications.   ││
│ │   Journal of AI Research, 45(2),   ││
│ │   123-145.                          ││
│ │                                    ││
│ │ Jones, B. (2022). Neural networks. ││
│ └────────────────────────────────────┘│
│                                        │
│ [Copy to Clipboard]  [Insert in Doc]  │
│ [Export to File]     [Cancel]         │
└────────────────────────────────────────┘
```

### 3. AI Agent Integration

**Context-Aware Agent Panel:**

**When viewing PDF:**
```
┌──────────────────────────────────────────┐
│ 🤖 Agent: Gamma (Knowledge Manager)     │
├──────────────────────────────────────────┤
│ Context: Reading "paper.pdf"             │
│                                          │
│ Quick Actions:                           │
│ [Extract Citation] [Summarize]          │
│ [Create Note]      [Find Related]       │
│                                          │
│ ─────────────────────────────────────── │
│ Chat:                                    │
│ You: Summarize this paper               │
│ Gamma: This paper discusses...          │
│                                          │
│ [Type message...                    ]→  │
└──────────────────────────────────────────┘
```

**When writing in editor:**
```
┌──────────────────────────────────────────┐
│ 🤖 Agent: Epsilon (Creative Assistant)   │
├──────────────────────────────────────────┤
│ Context: Editing "Chapter_1.md"          │
│                                          │
│ Quick Actions:                           │
│ [Improve Writing] [Expand Section]      │
│ [Check Grammar]   [Suggest Citations]   │
│                                          │
│ Suggestions:                             │
│ • Consider citing Smith (2023) here      │
│ • This section could be expanded         │
│                                          │
│ [Type message...                    ]→  │
└──────────────────────────────────────────┘
```

**Agent Selector:**
Quick switch between agents via dropdown or keyboard:
- `Ctrl+Shift+A` → Alpha (General)
- `Ctrl+Shift+B` → Beta (Research)
- `Ctrl+Shift+G` → Gamma (Knowledge)
- `Ctrl+Shift+D` → Delta (Tasks)
- `Ctrl+Shift+E` → Epsilon (Writing)

### 4. Paper Search Interface

**Research → Search Papers:**
```
┌────────────────────────────────────────────────────────┐
│ Search Academic Papers                                 │
├────────────────────────────────────────────────────────┤
│ Query: [machine learning optimization___________]  🔍  │
│                                                        │
│ Sources: ☑ arXiv  ☑ Semantic Scholar  ☑ CrossRef     │
│ Years: [2020] to [2024]   Sort by: [Citations ▾]     │
│                                                        │
│ Results: 47 papers found                              │
│ ┌────────────────────────────────────────────────────┐│
│ │ ⭐ 245 citations                                   ││
│ │ Optimization Methods for Deep Learning (2023)     ││
│ │ Smith, J.; Doe, A.; Brown, C.                      ││
│ │ arXiv:2301.12345 | [PDF] [DOI] [Import] [Cite]   ││
│ │ Abstract: This paper presents novel...            ││
│ │                                                    ││
│ │ ⭐ 189 citations                                   ││
│ │ Neural Network Training Efficiency (2022)         ││
│ │ Jones, B.; Wilson, K.                              ││
│ │ ACL 2022 | [PDF] [DOI] [Import] [Cite]           ││
│ │ Abstract: We introduce a method...                ││
│ └────────────────────────────────────────────────────┘│
│                                                        │
│ [Import Selected]  [Export Results]  [Close]         │
└────────────────────────────────────────────────────────┘
```

**Import Action:**
1. Downloads/copies PDF
2. Extracts citation
3. Adds to bibliography
4. Creates note
5. Shows notification

### 5. Writing Environment

**Markdown Editor with Live Preview:**
```
┌──────────────────┬──────────────────────────────┐
│ # Chapter 1      │ Chapter 1                    │
│                  │                              │
│ ## Introduction  │ Introduction                 │
│                  │                              │
│ Recent work by   │ Recent work by Smith (2023)  │
│ @Smith2023 has   │ has shown that machine       │
│ shown that...    │ learning can...              │
│                  │                              │
│ [Editor]         │ [Preview]                    │
└──────────────────┴──────────────────────────────┘
```

**Outline Sidebar Sync:**
As you write headers, outline updates automatically:
```
📋 Outline
 • Chapter 1 (523 words)
   - Introduction (203 words) ←  Current
   - Background (320 words)
   - [ ] Literature Review (0 words)
 • Chapter 2 (0 words)
   - [ ] Methodology (0 words)
```

Click section → Jump to that part of document

**Word Count & Progress:**
```
Status bar:
Words: 2,451 / 10,000 (24.5%) | Target: 500 words/day | Citations: 23
```

### 6. Export Workflow

**File → Export Document:**
```
┌──────────────────────────────────────────────┐
│ Export Document                              │
├──────────────────────────────────────────────┤
│ Document: [Chapter_1.md ▾]                  │
│ Format:   [⦿ Word (.docx)                   │
│            ○ LaTeX (.tex)                    │
│            ○ PDF (via LaTeX)]                │
│                                              │
│ Options:                                     │
│ ☑ Include bibliography                      │
│ ☑ Include title page                        │
│ ☑ Number sections                           │
│ ☐ Include table of contents                 │
│                                              │
│ Bibliography style: [APA 7th ▾]            │
│                                              │
│ Output: [~/Dissertation/Exports/chapter1.docx│
│          ...........................] 📁     │
│                                              │
│          [Cancel]  [Export]                  │
└──────────────────────────────────────────────┘
```

**Background Processing:**
Shows progress notification:
```
⏳ Exporting chapter1.docx...
✅ Export complete! (2.3s)
   📄 chapter1.docx (156 KB)
   [Open] [Show in Folder]
```

### 7. Zettelkasten Integration

**Note Creation from Document:**
While reading PDF or writing:
```
Right-click text → "Create Note" →
┌────────────────────────────────────────┐
│ Create Zettelkasten Note               │
├────────────────────────────────────────┤
│ Title: [Deep Learning Optimization__]  │
│                                        │
│ Content:                               │
│ ┌────────────────────────────────────┐│
│ │ Deep learning optimization methods ││
│ │ have evolved significantly...      ││
│ │                                    ││
│ │ Source: @Smith2023                 ││
│ └────────────────────────────────────┘│
│                                        │
│ Tags: [machine-learning] [optimization]│
│                                        │
│ Link to notes: [+ Add link]            │
│                                        │
│          [Cancel]  [Create]            │
└────────────────────────────────────────┘
```

**Note Browser:**
```
📝 Notes (156 notes)
Search: [_____________] 🔍

📌 Recent:
┌─────────────────────────────────────┐
│ [#123] Deep Learning Optimization   │
│ Tags: machine-learning              │
│ Links: 3 notes ↔                    │
│ Created: 2024-01-15                 │
├─────────────────────────────────────┤
│ [#122] Neural Network Training      │
│ Tags: deep-learning                 │
│ Links: 5 notes ↔                    │
│ Created: 2024-01-14                 │
└─────────────────────────────────────┘

[New Note]  [Graph View]
```

**Graph View (Optional Future Feature):**
Visual network of linked notes

---

## ⌨️ Keyboard Shortcuts

### Global
- `Ctrl+N` - New document
- `Ctrl+O` - Open file dialog
- `Ctrl+S` - Save current document
- `Ctrl+Shift+S` - Save as
- `Ctrl+W` - Close current document
- `Ctrl+Q` - Quit application
- `Ctrl+,` - Settings
- `Ctrl+K` - Command palette (quick actions)

### Navigation
- `Ctrl+1` - Focus file tree
- `Ctrl+2` - Focus editor
- `Ctrl+3` - Focus bibliography
- `Ctrl+Tab` - Cycle between open documents
- `Ctrl+\` - Toggle sidebar
- `Ctrl+B` - Toggle left panel

### Research
- `Ctrl+Shift+F` - Search papers
- `Ctrl+Shift+I` - Import file
- `Ctrl+Shift+C` - Extract citation
- `Ctrl+Shift+N` - Create note

### Writing
- `Ctrl+@` - Insert citation
- `Ctrl+Shift+B` - Generate bibliography
- `Ctrl+Shift+E` - Export document
- `Ctrl+L` - Jump to line/section
- `Ctrl+G` - Word count statistics

### AI Agents
- `Ctrl+Space` - Activate agent chat
- `Ctrl+Shift+A` - Switch to Alpha
- `Ctrl+Shift+B` - Switch to Beta
- `Ctrl+Shift+G` - Switch to Gamma

---

## 📦 Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
**Goal:** Main window, basic layout, theming

**Tasks:**
1. Create main window with menu bar
2. Implement three-panel layout (left, main, right)
3. Add panel resizing and collapsing
4. Implement dark/light themes
5. Create settings persistence (window size, layout)
6. Add status bar with basic info

**Deliverable:** Empty app with working layout

### Phase 2: File Management (Week 2-3)
**Goal:** File tree, document viewer, import

**Tasks:**
1. Implement file tree widget
2. Add file operations (open, rename, delete)
3. Create PDF viewer with PyMuPDF
4. Add drag-and-drop file import
5. Implement document tabs
6. Add file search

**Deliverable:** Can import and view PDFs

### Phase 3: Citation System (Week 3-4)
**Goal:** Bibliography panel, citation extraction

**Tasks:**
1. Create bibliography table widget
2. Integrate citation_manager module
3. Add citation detail dialog
4. Implement "Extract Citation" action
5. Add bibliography search and filter
6. Create citation insertion in editor

**Deliverable:** Full citation workflow

### Phase 4: Editor (Week 4-5)
**Goal:** Markdown editor with preview

**Tasks:**
1. Implement markdown editor widget
2. Add syntax highlighting
3. Create live preview panel
4. Add citation autocomplete
5. Implement word count
6. Add auto-save

**Deliverable:** Working writing environment

### Phase 5: Agent Integration (Week 5-6)
**Goal:** AI agent chat panel

**Tasks:**
1. Create agent chat widget
2. Connect to orchestrator
3. Add agent selector
4. Implement context awareness
5. Add quick action buttons
6. Create suggested prompts

**Deliverable:** AI agents accessible from UI

### Phase 6: Research Tools (Week 6-7)
**Goal:** Paper search, notes, outline

**Tasks:**
1. Create paper search dialog
2. Integrate academic_search module
3. Implement notes browser
4. Create outline panel
5. Add Zettelkasten graph view (basic)
6. Implement note linking

**Deliverable:** Complete research workflow

### Phase 7: Export & Polish (Week 7-8)
**Goal:** Export, keyboard shortcuts, refinement

**Tasks:**
1. Create export dialog
2. Integrate document_export module
3. Add all keyboard shortcuts
4. Implement command palette
5. Add progress tracking
6. Polish UI and fix bugs
7. User testing and feedback

**Deliverable:** Production-ready desktop app

---

## 🚀 Quick Start (Post-Implementation)

### Installation
```bash
# Install PyQt6 dependencies
pip install PyQt6 PyQt6-WebEngine PyMuPDF

# Run desktop app
python -m interfaces.desktop_app
```

### First Use
1. App opens to welcome screen
2. "Create New Project" or "Open Existing"
3. Project structure created:
   ```
   MyDissertation/
   ├── PDFs/
   ├── Drafts/
   ├── Notes/
   ├── References/
   ├── Exports/
   └── .b3project (config)
   ```
4. Main window opens with empty workspace
5. Import first PDF via drag-and-drop
6. Start writing!

---

## 📊 Success Metrics

### User Experience
- ✅ Zero context switching (everything in one app)
- ✅ < 2 clicks for common actions
- ✅ Keyboard-driven workflow available
- ✅ Visual feedback for all actions
- ✅ No data loss (auto-save)

### Performance
- ✅ App launch < 2 seconds
- ✅ PDF rendering < 1 second
- ✅ Search results < 500ms
- ✅ Agent response streaming
- ✅ Smooth scrolling and interactions

### Functionality
- ✅ Import PDF → Citation extracted automatically
- ✅ Write document → Export to Word/LaTeX
- ✅ Search papers → Import → Read → Cite
- ✅ Create notes → Link → Build knowledge graph
- ✅ Chat with agents → Get assistance → Apply changes

---

## 🎯 Conclusion

This desktop app transforms B3PersonalAssistant from a powerful multi-agent CLI into a **complete dissertation workbench**. By integrating document management, citation tools, AI agents, and writing environment into one unified interface, it enables a seamless workflow from research to final export.

**Next Step:** Begin Phase 1 implementation—create the main window and core layout infrastructure.
