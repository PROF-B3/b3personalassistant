#!/bin/bash
# Create macOS DMG installer for B3PersonalAssistant

set -e

echo "=========================================="
echo "  Creating macOS DMG Installer"
echo "=========================================="
echo

APP_NAME="B3PersonalAssistant"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
VOLUME_NAME="${APP_NAME} ${VERSION}"

# Check if app bundle exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "Error: dist/${APP_NAME}.app not found"
    echo "Run ./build_executable.sh first"
    exit 1
fi

# Create temporary directory
TMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TMP_DIR"

# Copy app bundle
echo "Copying app bundle..."
cp -R "dist/${APP_NAME}.app" "$TMP_DIR/"

# Create Applications symlink for easy installation
echo "Creating Applications symlink..."
ln -s /Applications "$TMP_DIR/Applications"

# Optional: Add README or background image
if [ -f "README.md" ]; then
    cp README.md "$TMP_DIR/"
fi

# Create DMG
echo "Creating DMG..."
mkdir -p installers

# Remove old DMG if exists
rm -f "installers/${DMG_NAME}"

# Create DMG with hdiutil
hdiutil create -volname "${VOLUME_NAME}" \
    -srcfolder "$TMP_DIR" \
    -ov -format UDZO \
    "installers/${DMG_NAME}"

# Clean up
echo "Cleaning up..."
rm -rf "$TMP_DIR"

echo
echo "=========================================="
echo "  DMG Created Successfully!"
echo "=========================================="
echo
echo "Location: installers/${DMG_NAME}"
echo "Size: $(du -h installers/${DMG_NAME} | cut -f1)"
echo
echo "To install:"
echo "  1. Open the DMG file"
echo "  2. Drag ${APP_NAME}.app to Applications folder"
echo "  3. Eject the DMG"
echo "  4. Launch from Applications or Spotlight"
echo
