#!/bin/bash
# Create Linux installer packages for B3PersonalAssistant
# Creates .deb package and optionally AppImage

set -e

echo "=========================================="
echo "  Creating Linux Installer Packages"
echo "=========================================="
echo

APP_NAME="B3PersonalAssistant"
VERSION="1.0.0"
ARCH="amd64"  # or i386, arm64, etc.

# Check if executable exists
if [ ! -f "dist/${APP_NAME}/${APP_NAME}" ]; then
    echo "Error: dist/${APP_NAME}/${APP_NAME} not found"
    echo "Run ./build_executable.sh first"
    exit 1
fi

# Create installers directory
mkdir -p installers

echo "Choose installer type:"
echo "  1) DEB package (Ubuntu/Debian)"
echo "  2) AppImage (Universal Linux)"
echo "  3) Both"
read -p "Enter choice (1-3): " choice

create_deb() {
    echo
    echo "Creating DEB package..."

    # Create package directory structure
    PKG_DIR="installers/${APP_NAME}_${VERSION}_${ARCH}"
    rm -rf "$PKG_DIR"
    mkdir -p "$PKG_DIR/DEBIAN"
    mkdir -p "$PKG_DIR/usr/bin"
    mkdir -p "$PKG_DIR/usr/share/applications"
    mkdir -p "$PKG_DIR/usr/share/${APP_NAME}"
    mkdir -p "$PKG_DIR/usr/share/doc/${APP_NAME}"
    mkdir -p "$PKG_DIR/usr/share/pixmaps"

    # Create control file
    cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: b3personalassistant
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: libc6, libstdc++6
Maintainer: Prof. B3 <prof.b3@example.com>
Description: B3 Personal Assistant - AI-powered productivity tool
 B3PersonalAssistant is a sophisticated multi-agent AI system featuring
 7 specialized agents for research, writing, and video editing.
 .
 Features include:
  - Research Mode with PDF viewing
  - Writing Mode with Markdown editor
  - Video Mode with AI-powered editing
  - Interactive onboarding and tutorials
  - Multi-agent AI assistance
Homepage: https://github.com/PROF-B3/b3personalassistant
EOF

    # Copy executable and files
    echo "Copying files..."
    cp -R "dist/${APP_NAME}"/* "$PKG_DIR/usr/share/${APP_NAME}/"

    # Create wrapper script
    cat > "$PKG_DIR/usr/bin/${APP_NAME}" << 'EOF'
#!/bin/bash
cd /usr/share/B3PersonalAssistant
exec ./B3PersonalAssistant "$@"
EOF
    chmod +x "$PKG_DIR/usr/bin/${APP_NAME}"

    # Create desktop entry
    cat > "$PKG_DIR/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=B3 Personal Assistant
Comment=AI-powered productivity tool for research, writing, and video editing
Exec=${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Type=Application
Categories=Office;Utility;Education;
Keywords=AI;research;writing;video;productivity;
EOF

    # Copy documentation
    cp README.md "$PKG_DIR/usr/share/doc/${APP_NAME}/" 2>/dev/null || true
    cp ONBOARDING_GUIDE.md "$PKG_DIR/usr/share/doc/${APP_NAME}/" 2>/dev/null || true

    # Build package
    echo "Building DEB package..."
    dpkg-deb --build "$PKG_DIR"

    echo "DEB package created: ${PKG_DIR}.deb"
    echo "Size: $(du -h ${PKG_DIR}.deb | cut -f1)"

    echo
    echo "To install:"
    echo "  sudo dpkg -i ${PKG_DIR}.deb"
    echo "  sudo apt-get install -f  # Fix dependencies if needed"
}

create_appimage() {
    echo
    echo "Creating AppImage..."

    # Check if appimagetool is available
    if ! command -v appimagetool &> /dev/null; then
        echo "Downloading appimagetool..."
        wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
            -O appimagetool
        chmod +x appimagetool
    fi

    # Create AppDir structure
    APPDIR="installers/${APP_NAME}.AppDir"
    rm -rf "$APPDIR"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

    # Copy files
    cp -R "dist/${APP_NAME}"/* "$APPDIR/usr/bin/"

    # Create AppRun script
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
cd "${HERE}/usr/bin"
exec ./B3PersonalAssistant "$@"
EOF
    chmod +x "$APPDIR/AppRun"

    # Create desktop file
    cat > "$APPDIR/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=B3 Personal Assistant
Exec=B3PersonalAssistant
Icon=${APP_NAME}
Type=Application
Categories=Office;Utility;
EOF

    # Copy desktop file to usr/share/applications
    cp "$APPDIR/${APP_NAME}.desktop" "$APPDIR/usr/share/applications/"

    # Create default icon (placeholder)
    # In production, replace with actual icon
    echo "Note: Add icon to $APPDIR/${APP_NAME}.png for better appearance"

    # Build AppImage
    echo "Building AppImage..."
    ARCH=x86_64 ./appimagetool "$APPDIR" "installers/${APP_NAME}-${VERSION}-x86_64.AppImage"

    echo "AppImage created: installers/${APP_NAME}-${VERSION}-x86_64.AppImage"
    echo "Size: $(du -h installers/${APP_NAME}-${VERSION}-x86_64.AppImage | cut -f1)"

    echo
    echo "To run:"
    echo "  chmod +x installers/${APP_NAME}-${VERSION}-x86_64.AppImage"
    echo "  ./installers/${APP_NAME}-${VERSION}-x86_64.AppImage"
}

# Execute based on choice
case $choice in
    1)
        create_deb
        ;;
    2)
        create_appimage
        ;;
    3)
        create_deb
        create_appimage
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo
echo "=========================================="
echo "  Installer(s) Created Successfully!"
echo "=========================================="
echo
ls -lh installers/
