# B3 Personal Assistant - Release Guide

Quick reference for creating and publishing new releases.

## 🚀 Quick Release (Automated)

### Step 1: Create Icons (First Time Only)

```bash
# Generate application icons
python3 create_icons.py

# On macOS, also create .icns file
iconutil -c icns icon.iconset
```

### Step 2: Create Release

```bash
# Run automated release script
./create_release.sh 1.0.0

# This will:
# - Update version numbers in all files
# - Commit changes
# - Create git tag
# - Push to GitHub
# - Trigger GitHub Actions build
```

### Step 3: Monitor Build

- Go to: https://github.com/PROF-B3/b3personalassistant/actions
- Wait for all builds to complete (~30-45 minutes)
- Builds for Windows, macOS, and Linux run in parallel

### Step 4: Release is Published

- GitHub automatically creates release
- All installers are attached
- Release notes are generated
- Users can download from: https://github.com/PROF-B3/b3personalassistant/releases

---

## 📋 Manual Release Process

If you prefer to do it manually:

### 1. Update Version Numbers

```bash
# In B3PersonalAssistant.spec
CFBundleShortVersionString': '1.0.0'

# In create_installer_windows.iss
#define MyAppVersion "1.0.0"

# In create_installer_mac.sh
VERSION="1.0.0"

# In create_installer_linux.sh
VERSION="1.0.0"
```

### 2. Build Executables Locally

**Windows:**
```bash
build_executable.bat
# Then open create_installer_windows.iss in Inno Setup
```

**macOS:**
```bash
./build_executable.sh
./create_installer_mac.sh
```

**Linux:**
```bash
./build_executable.sh
./create_installer_linux.sh
# Choose 3 (both DEB and AppImage)
```

### 3. Test Installers

Install on clean systems and verify:
- [ ] Onboarding wizard appears
- [ ] All three modes work
- [ ] Tutorials are accessible
- [ ] Sample data generates correctly

### 4. Create GitHub Release

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Go to GitHub → Releases → Create Release
# Upload installers
# Publish
```

---

## 🔧 GitHub Actions Workflow

The workflow is triggered by:
- Pushing tags starting with `v` (e.g., `v1.0.0`)
- Manual trigger via Actions tab

### What It Does

1. **Build Windows** (~20 minutes)
   - Builds executable with PyInstaller
   - Creates Inno Setup installer
   - Uploads artifacts

2. **Build macOS** (~15 minutes)
   - Builds app bundle
   - Creates DMG installer
   - Uploads artifacts

3. **Build Linux** (~15 minutes)
   - Builds executable
   - Creates AppImage (universal)
   - Creates DEB package
   - Uploads artifacts

4. **Create Release** (~2 minutes)
   - Downloads all artifacts
   - Creates GitHub Release
   - Attaches all installers
   - Generates release notes

### Manual Trigger

```bash
# Go to GitHub Actions tab
# Select "Build Standalone Executables" workflow
# Click "Run workflow"
# Enter version (optional)
# Click "Run workflow"
```

---

## 📦 Release Checklist

Before releasing:

### Pre-Release
- [ ] All tests pass (`./validate_onboarding.sh`)
- [ ] Version numbers updated
- [ ] Changelog/release notes prepared
- [ ] Icons created (`python3 create_icons.py`)
- [ ] Build tested locally on one platform

### Build
- [ ] Windows installer builds successfully
- [ ] macOS DMG builds successfully
- [ ] Linux AppImage builds successfully
- [ ] Linux DEB package builds successfully

### Testing
- [ ] Windows: Install and run on Windows 10/11
- [ ] macOS: Install and run on macOS 10.15+
- [ ] Linux: Test AppImage and DEB on Ubuntu/Debian

### Verification
- [ ] Onboarding wizard appears on first run
- [ ] All three modes accessible
- [ ] Tutorials work correctly
- [ ] Sample data generates
- [ ] File operations work
- [ ] No crashes or errors

### Publication
- [ ] GitHub Release created
- [ ] All installers attached
- [ ] Release notes complete
- [ ] README updated with download links
- [ ] Documentation up to date

---

## 📝 Release Notes Template

```markdown
## B3 Personal Assistant v1.0.0

### 🎉 New Features
- Complete desktop application with PyQt6
- Interactive onboarding wizard
- 7 step-by-step tutorials
- Research, Writing, and Video modes
- AI-powered video editing

### 🐛 Bug Fixes
- Fixed [issue description]
- Resolved [issue description]

### 🔧 Improvements
- Enhanced [feature]
- Optimized [feature]

### 📦 Downloads
- Windows: `B3PersonalAssistant-Setup-1.0.0.exe` (150 MB)
- macOS: `B3PersonalAssistant-1.0.0.dmg` (200 MB)
- Linux AppImage: `B3PersonalAssistant-1.0.0-x86_64.AppImage` (400 MB)
- Linux DEB: `b3personalassistant_1.0.0_amd64.deb` (180 MB)

### 📖 Documentation
- [User Guide](link)
- [Onboarding Guide](link)
- [Video Editing Guide](link)

### 🔗 Links
- Full Changelog: [link]
- Issues: [link]
```

---

## 🔍 Troubleshooting Releases

### Build Fails on GitHub Actions

**Check:**
- Actions logs for specific error
- Dependencies in requirements-desktop.txt
- PyInstaller spec file syntax
- Platform-specific issues

**Common Issues:**
```bash
# Windows: Missing DLL
# Solution: Add to binaries in spec file

# macOS: Code signing fails
# Solution: Remove codesign_identity or set up signing

# Linux: Missing system libraries
# Solution: Add to apt-get install in workflow
```

### Installer Doesn't Work

**Windows:**
- Verify Inno Setup syntax
- Check file paths in .iss script
- Test on clean Windows VM

**macOS:**
- Check DMG mounts correctly
- Verify app bundle structure
- Test drag-to-Applications

**Linux:**
- Verify AppImage is executable
- Check DEB package with `dpkg -c`
- Test on fresh Ubuntu install

### GitHub Release Not Created

**Check:**
- Tag starts with 'v' (e.g., v1.0.0)
- All build jobs succeeded
- GITHUB_TOKEN permissions
- softprops/action-gh-release version

---

## 🎯 Release Schedule

Suggested schedule:

- **Major releases (1.0.0, 2.0.0)**: Quarterly
- **Minor releases (1.1.0, 1.2.0)**: Monthly
- **Patch releases (1.0.1, 1.0.2)**: As needed for bugs

### Version Numbering

- **Major (X.0.0)**: Breaking changes, major features
- **Minor (1.X.0)**: New features, improvements
- **Patch (1.0.X)**: Bug fixes only

---

## 📊 Post-Release

After publishing:

1. **Announce Release**
   - GitHub Discussions
   - Project README
   - Social media (if applicable)

2. **Monitor Issues**
   - Watch for installation problems
   - Check for crash reports
   - Respond to user feedback

3. **Update Documentation**
   - Keep docs in sync with release
   - Update screenshots if UI changed
   - Add new features to guides

4. **Plan Next Release**
   - Review feedback
   - Prioritize features
   - Schedule development

---

## 🚀 Quick Commands

```bash
# Full release (automated)
./create_release.sh 1.0.0

# Create icons
python3 create_icons.py

# Build locally (all platforms)
./build_executable.sh  # or .bat on Windows

# Create installers
./create_installer_mac.sh       # macOS
./create_installer_linux.sh     # Linux
# Windows: Use Inno Setup GUI

# Test validation
./validate_onboarding.sh

# Push release
git push origin v1.0.0
```

---

## 📞 Support

- **Build Issues**: Check [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)
- **Release Problems**: Open issue on GitHub
- **Questions**: GitHub Discussions

Happy releasing! 🎉
