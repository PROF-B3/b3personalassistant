#!/bin/bash
# Build script for B3PersonalAssistant standalone executable
# Supports Windows, macOS, and Linux

set -e  # Exit on error

echo "=========================================="
echo "  B3PersonalAssistant Build Script"
echo "=========================================="
echo

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="Windows"
else
    PLATFORM="Unknown"
fi

echo "Platform: $PLATFORM"
echo

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo

# Install dependencies if needed
echo "Checking dependencies..."
pip install -r requirements-desktop.txt --quiet

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec.backup

# Build with PyInstaller
echo
echo "Building executable with PyInstaller..."
echo "This may take 5-10 minutes..."
echo

pyinstaller B3PersonalAssistant.spec --clean --noconfirm

# Check if build succeeded
if [ -d "dist/B3PersonalAssistant" ]; then
    echo
    echo "=========================================="
    echo "  Build Successful!"
    echo "=========================================="
    echo
    echo "Executable location: dist/B3PersonalAssistant/"
    echo

    # Platform-specific instructions
    case $PLATFORM in
        "Linux")
            echo "To run: ./dist/B3PersonalAssistant/B3PersonalAssistant"
            echo
            echo "To create installer, run: ./create_installer_linux.sh"
            ;;
        "macOS")
            if [ -d "dist/B3PersonalAssistant.app" ]; then
                echo "macOS app bundle created: dist/B3PersonalAssistant.app"
                echo "To run: open dist/B3PersonalAssistant.app"
                echo
                echo "To create DMG installer, run: ./create_installer_mac.sh"
            else
                echo "To run: ./dist/B3PersonalAssistant/B3PersonalAssistant"
            fi
            ;;
        "Windows")
            echo "To run: dist\\B3PersonalAssistant\\B3PersonalAssistant.exe"
            echo
            echo "To create installer, run: create_installer_windows.bat"
            ;;
    esac

    # Show size
    echo
    du -sh dist/B3PersonalAssistant* 2>/dev/null || echo "Size: $(ls -lh dist/ | grep B3PersonalAssistant)"

else
    echo
    echo "=========================================="
    echo "  Build Failed!"
    echo "=========================================="
    echo
    echo "Check the error messages above."
    exit 1
fi

echo
echo "Build complete!"
