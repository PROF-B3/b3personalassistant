# B3 Personal Assistant - Complete Beginner's Guide

## 🎯 What You're Going to Do

You're going to run the B3 Personal Assistant desktop application on your computer. It's like installing and running any other program, but we'll do it step by step together.

---

## ✅ Step 1: Check What You Already Have

First, let's see what's already on your computer:

```bash
# Check if Python is installed
python3 --version

# You should see something like: Python 3.9.x or Python 3.10.x
# If you see an error, we'll install Python next
```

**What you should see:**
- ✅ `Python 3.9.x` or higher = Great! Continue to Step 2
- ❌ Error or version lower than 3.9 = Go to "Installing Python" below

### Installing Python (if needed)

**On Ubuntu/Debian Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**On macOS:**
```bash
# Install Homebrew first (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python
brew install python3
```

**On Windows:**
- Download from: https://www.python.org/downloads/
- Run installer
- ✅ Check "Add Python to PATH"
- Click "Install Now"

---

## ✅ Step 2: Make Sure You're in the Right Place

You should already be in the B3PersonalAssistant directory:

```bash
# Check where you are
pwd

# You should see something ending with: /b3personalassistant
# Example: /home/user/b3personalassistant
```

If you're not in the right place:
```bash
cd /home/user/b3personalassistant
```

---

## ✅ Step 3: Install Required Packages

This installs all the software B3 needs to run:

```bash
# Install desktop app requirements
pip install -r requirements-desktop.txt

# This will take 2-5 minutes
# You'll see lots of text scrolling - that's normal!
```

**What's happening:**
- Installing PyQt6 (the desktop interface)
- Installing MoviePy (video editing)
- Installing other tools B3 needs

**If you see "Permission denied" error:**
```bash
# Add --user flag
pip install --user -r requirements-desktop.txt
```

---

## ✅ Step 4: Run the Desktop App!

Now for the exciting part - let's launch B3:

```bash
python3 run_desktop.py
```

**What happens:**
1. A window will appear on your screen
2. Since this is your first time, you'll see the **Onboarding Wizard**
3. Follow the wizard - it's easy!

---

## 🎓 First-Run Experience (Onboarding Wizard)

When you run B3 for the first time, you'll see 5 pages:

### Page 1: Welcome
- Introduces B3 Personal Assistant
- Click **"Next"** to continue

### Page 2: Tell Us About You
- **Your Name**: Type your name (e.g., "John Doe")
- **Use Case**: Choose what you'll use B3 for
  - Academic (for research/writing)
  - Professional (for work)
  - Personal (for personal projects)
  - Creative (for creative work)
- Click **"Next"**

### Page 3: Preferences
- **Citation Style**: Choose one (APA, MLA, Chicago, Harvard)
  - If unsure, choose **APA** (most common)
- **Video Theme**: Choose your favorite visual style
  - "Neon Cyberpunk" is cool!
- **Options**:
  - ✅ Auto-save (recommended - keeps checking this)
  - ✅ Show line numbers (helpful for coding)
  - ✅ Word wrap (makes text easier to read)
- Click **"Next"**

### Page 4: Workspace
- **Workspace Path**: Where B3 stores your files
  - Default: `/home/yourusername/B3Workspace`
  - You can change it or keep the default
- **Create sample data**: ✅ Check this box!
  - This creates example files so you can learn
- Click **"Next"**

### Page 5: Complete
- Shows summary of your settings
- Click **"Finish"**

**The wizard closes and the main app opens!** 🎉

---

## 🖥️ Using B3 Desktop App

### Main Window Overview

When B3 opens, you'll see:

```
┌─────────────────────────────────────────┐
│  File  Edit  View  Video  Help          │  ← Menu bar
├─────────────────────────────────────────┤
│  Mode: [Research ▼] [Video] [Writing]  │  ← Mode switcher
├──────────┬──────────────────────────────┤
│          │                              │
│  Files   │     Main Workspace           │
│  Tree    │     (Your work area)         │
│          │                              │
│          │                              │
├──────────┼──────────────────────────────┤
│  AI      │                              │
│  Agents  │                              │
└──────────┴──────────────────────────────┘
```

### The Three Modes

B3 has 3 modes - switch between them anytime!

**1. Research Mode** (Ctrl+1)
- For reading PDFs
- Taking notes while reading
- Organizing research papers

**2. Video Mode** (Ctrl+2)
- For editing videos
- Applying cool effects and themes
- Creating video remixes

**3. Writing Mode** (Ctrl+3)
- For writing documents
- Markdown editor with live preview
- Export to PDF, Word, HTML

### Quick Keyboard Shortcuts

- **Ctrl+1** = Switch to Research mode
- **Ctrl+2** = Switch to Video mode
- **Ctrl+3** = Switch to Writing mode
- **Ctrl+Space** = Talk to AI assistant

---

## 📚 Your First 5 Minutes

Let's try something simple:

### Try the Tutorials

1. Click **Help** menu at the top
2. Click **"📚 Interactive Tutorials"**
3. You'll see 7 tutorials
4. Double-click **"Basic Navigation"** (the first one)
5. Follow along - it takes 2 minutes!

### Open the Quick Start Guide

1. Click **Help** menu
2. Click **"🚀 Quick Start Guide"**
3. Read through it - has lots of helpful tips!

### Try Creating a Note

1. Make sure you're in **Writing mode** (Ctrl+3)
2. Click the **"+ New"** button or File → New
3. Type something like:
   ```
   # My First Note

   This is my first note in B3!

   ## Things I want to learn:
   - Research mode
   - Video editing
   - AI assistance
   ```
4. Click **Save** (Ctrl+S)
5. See the preview on the right!

---

## 🎯 What to Explore Next

After your first 5 minutes, try:

### 1. Complete More Tutorials
- Help → Interactive Tutorials
- Start with "Getting Started" (5 min)
- Then try "Research Mode" (7 min)

### 2. Check Your Workspace
Open your file manager and look at:
```
~/B3Workspace/
  ├── Research/        ← Put PDFs here
  ├── Notes/          ← Your notes
  ├── Drafts/         ← Writing drafts
  ├── Videos/         ← Video files
  └── QuickStart.md   ← Guide you just read
```

### 3. Try AI Assistance
- Press **Ctrl+Space** to focus on AI chat
- Ask something like: "How do I import a PDF?"
- The AI will help you!

---

## 🆘 Common Issues & Solutions

### Issue: "Command not found: python3"
**Solution:**
```bash
# Try just 'python' instead
python run_desktop.py

# Or install Python (see Step 1)
```

### Issue: "No module named 'PyQt6'"
**Solution:**
```bash
# Install the requirements again
pip install -r requirements-desktop.txt
```

### Issue: Window doesn't appear
**Solution:**
```bash
# Check for errors in terminal
# Try running with verbose output
python3 run_desktop.py --verbose
```

### Issue: "Permission denied"
**Solution:**
```bash
# Make scripts executable
chmod +x run_desktop.py
chmod +x build_executable.sh

# Then try again
./run_desktop.py
```

### Issue: Onboarding wizard stuck
**Solution:**
```bash
# Reset onboarding
rm -rf ~/.b3assistant/

# Run again
python3 run_desktop.py
```

---

## 📝 Quick Reference Card

Save this for later:

### Running B3
```bash
cd /home/user/b3personalassistant
python3 run_desktop.py
```

### Reset Everything
```bash
# Clears settings, starts fresh
rm -rf ~/.b3assistant/
```

### Update B3
```bash
git pull origin main
pip install -r requirements-desktop.txt
```

### Get Help
- In app: Help → Interactive Tutorials
- In app: Help → Quick Start Guide
- Online: Check README.md in the folder

---

## 🎉 You're Ready!

That's it! You now know how to:
- ✅ Install requirements
- ✅ Run B3 desktop app
- ✅ Complete onboarding
- ✅ Use the three modes
- ✅ Access tutorials
- ✅ Get help when stuck

**Next command to run:**
```bash
python3 run_desktop.py
```

**Have fun exploring B3 Personal Assistant!** 🚀

---

## 💡 Pro Tips

1. **Learn keyboard shortcuts** - Makes things faster
2. **Complete all 7 tutorials** - Takes ~1 hour, worth it
3. **Use sample data** - Learn from examples
4. **Ask AI for help** - Ctrl+Space anytime
5. **Keep workspace organized** - Use the folders

---

## 📞 Need More Help?

- Check `ONBOARDING_GUIDE.md` in the folder
- Check `README.md` for detailed info
- Look at `VIDEO_EDITING_GUIDE.md` for video features
- Check `TROUBLESHOOTING.md` if something breaks

**You've got this!** 🎊
