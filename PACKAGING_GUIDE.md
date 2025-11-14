# B3 Personal Assistant - Packaging Guide

## 📦 Creating Standalone Executables

This guide explains how to package B3PersonalAssistant into standalone executables for Windows, macOS, and Linux, so users can install without Python.

---

## Prerequisites

### All Platforms

```bash
# Install PyInstaller
pip install pyinstaller

# Install all dependencies
pip install -r requirements-desktop.txt
```

### Platform-Specific Tools

**Windows:**
- [Inno Setup](https://jrsoftware.org/isdl.php) - For creating installers

**macOS:**
- Xcode Command Line Tools - `xcode-select --install`
- hdiutil (built-in) - For creating DMG files

**Linux:**
- dpkg (usually pre-installed) - For DEB packages
- [appimagetool](https://github.com/AppImage/AppImageKit) - For AppImage (auto-downloaded by script)

---

## Quick Start

### 1. Build Executable

```bash
# Make build script executable
chmod +x build_executable.sh

# Run build
./build_executable.sh
```

This creates `dist/B3PersonalAssistant/` with the standalone executable.

**Build time:** 5-10 minutes
**Output size:** ~300-500 MB (includes all dependencies)

### 2. Create Installer (Optional)

#### Windows

```bash
# Option 1: Use Inno Setup GUI
# Open create_installer_windows.iss in Inno Setup Compiler

# Option 2: Command line (if ISCC is in PATH)
iscc create_installer_windows.iss
```

Output: `installers/B3PersonalAssistant-Setup-1.0.0.exe`

#### macOS

```bash
chmod +x create_installer_mac.sh
./create_installer_mac.sh
```

Output: `installers/B3PersonalAssistant-1.0.0.dmg`

#### Linux

```bash
chmod +x create_installer_linux.sh
./create_installer_linux.sh
# Choose: 1) DEB, 2) AppImage, or 3) Both
```

Output:
- `installers/b3personalassistant_1.0.0_amd64.deb`
- `installers/B3PersonalAssistant-1.0.0-x86_64.AppImage`

---

## Detailed Instructions

### Building with PyInstaller

PyInstaller bundles your Python application and all dependencies into a single package.

**What gets included:**
- Python interpreter
- All Python packages (PyQt6, MoviePy, etc.)
- Your application code
- Documentation files

**Build process:**

```bash
# Clean build (recommended)
rm -rf build/ dist/

# Build using spec file
pyinstaller B3PersonalAssistant.spec --clean --noconfirm

# Test the executable
./dist/B3PersonalAssistant/B3PersonalAssistant  # Linux/Mac
# or
dist\B3PersonalAssistant\B3PersonalAssistant.exe  # Windows
```

**Customizing the build:**

Edit `B3PersonalAssistant.spec` to:
- Add/remove files to bundle
- Change executable name
- Add application icon
- Exclude unnecessary modules
- Adjust hidden imports

---

### Creating Windows Installer

**Using Inno Setup:**

1. Install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Build executable first: `./build_executable.sh`
3. Open `create_installer_windows.iss` in Inno Setup Compiler
4. Click "Build" → "Compile"
5. Installer created in `installers/` directory

**Features:**
- Professional Windows installer
- Start menu shortcuts
- Desktop icon (optional)
- Uninstaller included
- ~150 MB installer size

**Customizing:**

Edit `create_installer_windows.iss` to change:
- App name, version, publisher
- Installation directory
- Icons and shortcuts
- License agreement
- Welcome message

---

### Creating macOS DMG

**Process:**

```bash
# Build app bundle first
./build_executable.sh

# Create DMG
./create_installer_mac.sh
```

**What it does:**
1. Creates temporary directory
2. Copies `.app` bundle
3. Creates Applications symlink
4. Packages into DMG with compression

**Result:**
- Drag-and-drop installer
- Professional appearance
- ~200 MB DMG size

**Customizing:**

Edit `create_installer_mac.sh` to:
- Add background image
- Change volume name
- Include README
- Adjust compression

**Advanced: Code Signing (for distribution)**

```bash
# Sign the app (requires Apple Developer account)
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name" \
    dist/B3PersonalAssistant.app

# Verify signature
codesign --verify --verbose dist/B3PersonalAssistant.app

# Notarize for Gatekeeper (macOS 10.15+)
xcrun altool --notarize-app \
    --primary-bundle-id "com.profb3.b3personalassistant" \
    --username "your@email.com" \
    --password "@keychain:AC_PASSWORD" \
    --file installers/B3PersonalAssistant-1.0.0.dmg
```

---

### Creating Linux Packages

#### DEB Package (Ubuntu/Debian)

```bash
./create_installer_linux.sh
# Choose option 1
```

**Installation:**

```bash
sudo dpkg -i installers/b3personalassistant_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

**Features:**
- Integrates with system package manager
- Creates desktop entry
- Installs to `/usr/share/B3PersonalAssistant/`
- Creates `/usr/bin` wrapper script

#### AppImage (Universal Linux)

```bash
./create_installer_linux.sh
# Choose option 2
```

**Running:**

```bash
chmod +x installers/B3PersonalAssistant-1.0.0-x86_64.AppImage
./installers/B3PersonalAssistant-1.0.0-x86_64.AppImage
```

**Features:**
- Single-file executable
- No installation required
- Works on most Linux distributions
- Portable (can run from USB stick)

---

## Testing Installers

### Windows

```bash
# Test installer
installers/B3PersonalAssistant-Setup-1.0.0.exe

# Silent install (for testing)
installers/B3PersonalAssistant-Setup-1.0.0.exe /VERYSILENT /SUPPRESSMSGBOXES

# Check installed location
dir "%PROGRAMFILES%\B3 Personal Assistant"

# Run installed app
"%PROGRAMFILES%\B3 Personal Assistant\B3PersonalAssistant.exe"
```

### macOS

```bash
# Mount DMG
open installers/B3PersonalAssistant-1.0.0.dmg

# Copy to Applications (manually or via script)
cp -R /Volumes/B3PersonalAssistant\ 1.0.0/B3PersonalAssistant.app /Applications/

# Run
open /Applications/B3PersonalAssistant.app
```

### Linux

**DEB:**
```bash
# Install
sudo dpkg -i installers/b3personalassistant_1.0.0_amd64.deb

# Run
B3PersonalAssistant

# Uninstall
sudo dpkg -r b3personalassistant
```

**AppImage:**
```bash
# Make executable
chmod +x installers/B3PersonalAssistant-1.0.0-x86_64.AppImage

# Run
./installers/B3PersonalAssistant-1.0.0-x86_64.AppImage

# Or double-click in file manager
```

---

## Troubleshooting Build Issues

### Issue: PyInstaller fails with missing module

**Solution:**
```python
# Edit B3PersonalAssistant.spec
# Add to hiddenimports list:
hiddenimports=[
    'missing_module_name',
    # ...
]
```

### Issue: Executable too large

**Solution:**
```python
# Edit B3PersonalAssistant.spec
# Add to excludes list:
excludes=[
    'tkinter',
    'matplotlib',
    'scipy',
    'pandas',  # if not used
    # ...
]
```

### Issue: Missing DLL on Windows

**Solution:**
```bash
# Install Visual C++ Redistributable
# Download from Microsoft and include in installer

# Or add to spec file:
binaries=[
    ('path/to/missing.dll', '.'),
]
```

### Issue: macOS Gatekeeper blocks app

**Solution:**
```bash
# Remove quarantine attribute
xattr -dr com.apple.quarantine /Applications/B3PersonalAssistant.app

# Or: System Preferences → Security → Allow anyway
```

### Issue: Linux missing libraries

**Solution:**
```bash
# Check dependencies
ldd dist/B3PersonalAssistant/B3PersonalAssistant

# Install missing libraries
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

---

## File Size Optimization

### Reduce Executable Size

```bash
# 1. Exclude unused modules in spec file
excludes=['tkinter', 'matplotlib', 'scipy']

# 2. Use UPX compression
upx=True  # Already enabled in spec

# 3. Strip debug symbols
strip=True

# 4. One-file mode (slower startup, smaller)
# Change in spec:
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Include these
    a.zipfiles,
    a.datas,
    [],
    name='B3PersonalAssistant',
    # ... single file
)
```

### Typical Sizes

| Platform | Executable | Installer | Notes |
|----------|-----------|-----------|-------|
| Windows | 350 MB | 150 MB | Compressed installer |
| macOS | 400 MB | 200 MB | DMG compressed |
| Linux DEB | 350 MB | 180 MB | Compressed package |
| Linux AppImage | 400 MB | N/A | Single file |

---

## Automated Builds (GitHub Actions)

Create `.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt pyinstaller
      - name: Build executable
        run: pyinstaller B3PersonalAssistant.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: B3PersonalAssistant-Windows
          path: dist/B3PersonalAssistant

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt pyinstaller
      - name: Build executable
        run: pyinstaller B3PersonalAssistant.spec
      - name: Create DMG
        run: chmod +x create_installer_mac.sh && ./create_installer_mac.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: B3PersonalAssistant-macOS
          path: installers/*.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt pyinstaller
      - name: Build executable
        run: pyinstaller B3PersonalAssistant.spec
      - name: Create AppImage
        run: |
          chmod +x create_installer_linux.sh
          echo "2" | ./create_installer_linux.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: B3PersonalAssistant-Linux
          path: installers/*.AppImage
```

---

## Distribution

### GitHub Releases

1. Build installers for all platforms
2. Create release on GitHub
3. Upload installers as assets:
   - `B3PersonalAssistant-Setup-1.0.0.exe` (Windows)
   - `B3PersonalAssistant-1.0.0.dmg` (macOS)
   - `B3PersonalAssistant-1.0.0-x86_64.AppImage` (Linux)
   - `b3personalassistant_1.0.0_amd64.deb` (Linux DEB)

### Download Page Example

```markdown
## Download B3 Personal Assistant v1.0.0

### Windows
- [Download Installer](link) (150 MB)
- Requires: Windows 10/11
- Install and run - no Python needed

### macOS
- [Download DMG](link) (200 MB)
- Requires: macOS 10.15+
- Drag to Applications folder

### Linux
- [Download AppImage](link) (400 MB) - Universal
- [Download DEB](link) (180 MB) - Ubuntu/Debian
- Requires: Modern Linux distribution
```

---

## Summary

```bash
# Complete build workflow:

# 1. Build executable
./build_executable.sh

# 2. Create installer (choose platform)
./create_installer_windows.iss  # Windows (via Inno Setup)
./create_installer_mac.sh        # macOS
./create_installer_linux.sh      # Linux

# 3. Test installer
# Install and verify onboarding works

# 4. Distribute
# Upload to GitHub Releases or hosting
```

---

## Checklist for Release

- [ ] Update version in all files:
  - `B3PersonalAssistant.spec`
  - `create_installer_windows.iss`
  - `create_installer_mac.sh`
  - `create_installer_linux.sh`
- [ ] Build on all platforms
- [ ] Test installers on clean systems
- [ ] Verify onboarding wizard appears
- [ ] Test all three modes (Research, Video, Writing)
- [ ] Check tutorials are accessible
- [ ] Verify sample data generation
- [ ] Create release notes
- [ ] Upload to GitHub Releases
- [ ] Update download links in README

---

## Support

For packaging issues:
- Check build logs in `build/` directory
- Review PyInstaller warnings
- Test on virtual machine before release
- Consult [PyInstaller documentation](https://pyinstaller.org/)

Happy packaging! 🚀
