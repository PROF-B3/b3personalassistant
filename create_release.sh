#!/bin/bash
# Automated release creation script
# Builds executables and creates GitHub release

set -e

echo "=========================================="
echo "  B3PersonalAssistant Release Creator"
echo "=========================================="
echo

# Check if version is provided
if [ -z "$1" ]; then
    echo "Usage: ./create_release.sh <version>"
    echo "Example: ./create_release.sh 1.0.0"
    exit 1
fi

VERSION="$1"
TAG="v${VERSION}"

echo "Creating release for version: $VERSION"
echo "Git tag: $TAG"
echo

# Confirm
read -p "Proceed with release? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled"
    exit 0
fi

# Check if git is clean
if [[ -n $(git status -s) ]]; then
    echo "Warning: Git working directory is not clean"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Update version in files
echo
echo "Updating version numbers..."

# Update spec file
if [ -f "B3PersonalAssistant.spec" ]; then
    sed -i.bak "s/version='[0-9.]*'/version='${VERSION}'/" B3PersonalAssistant.spec
fi

# Update Inno Setup script
if [ -f "create_installer_windows.iss" ]; then
    sed -i.bak "s/#define MyAppVersion \"[0-9.]*\"/#define MyAppVersion \"${VERSION}\"/" create_installer_windows.iss
fi

# Update macOS DMG script
if [ -f "create_installer_mac.sh" ]; then
    sed -i.bak "s/VERSION=\"[0-9.]*\"/VERSION=\"${VERSION}\"/" create_installer_mac.sh
fi

# Update Linux installer script
if [ -f "create_installer_linux.sh" ]; then
    sed -i.bak "s/VERSION=\"[0-9.]*\"/VERSION=\"${VERSION}\"/" create_installer_linux.sh
fi

echo "Version numbers updated to $VERSION"

# Clean backup files
rm -f *.bak

# Commit version changes
echo
echo "Committing version changes..."
git add -A
git commit -m "Bump version to $VERSION" || echo "No changes to commit"

# Create git tag
echo
echo "Creating git tag: $TAG"
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Tag $TAG already exists"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$TAG"
    else
        exit 1
    fi
fi

git tag -a "$TAG" -m "Release version $VERSION"

# Push to remote
echo
echo "Pushing changes and tags to remote..."
read -p "Push to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin $(git branch --show-current)
    git push origin "$TAG"
    echo
    echo "=========================================="
    echo "  Release Created!"
    echo "=========================================="
    echo
    echo "Tag $TAG has been pushed to GitHub"
    echo
    echo "GitHub Actions will now:"
    echo "  1. Build Windows executable and installer"
    echo "  2. Build macOS app bundle and DMG"
    echo "  3. Build Linux executable and packages"
    echo "  4. Create GitHub Release with all installers"
    echo
    echo "Monitor progress at:"
    echo "  https://github.com/PROF-B3/b3personalassistant/actions"
    echo
    echo "Release will be available at:"
    echo "  https://github.com/PROF-B3/b3personalassistant/releases/tag/$TAG"
    echo
else
    echo "Release NOT pushed to GitHub"
    echo "To push later, run:"
    echo "  git push origin $(git branch --show-current)"
    echo "  git push origin $TAG"
fi
