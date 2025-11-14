@echo off
REM Build script for B3PersonalAssistant on Windows

echo ==========================================
echo   B3PersonalAssistant Build Script
echo ==========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements-desktop.txt --quiet

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with PyInstaller
echo.
echo Building executable with PyInstaller...
echo This may take 5-10 minutes...
echo.

pyinstaller B3PersonalAssistant.spec --clean --noconfirm

REM Check if build succeeded
if exist dist\B3PersonalAssistant (
    echo.
    echo ==========================================
    echo   Build Successful!
    echo ==========================================
    echo.
    echo Executable location: dist\B3PersonalAssistant\
    echo.
    echo To run: dist\B3PersonalAssistant\B3PersonalAssistant.exe
    echo.
    echo To create installer:
    echo   1. Install Inno Setup from https://jrsoftware.org/isdl.php
    echo   2. Open create_installer_windows.iss in Inno Setup
    echo   3. Click Build -^> Compile
    echo.
) else (
    echo.
    echo ==========================================
    echo   Build Failed!
    echo ==========================================
    echo.
    echo Check the error messages above.
    pause
    exit /b 1
)

pause
