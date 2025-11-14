# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for B3PersonalAssistant Desktop App
Builds standalone executable with all dependencies bundled
"""

import os
import sys

block_cipher = None

# Determine icon path based on platform
icon_path = None
if sys.platform == 'win32' and os.path.exists('icon.ico'):
    icon_path = 'icon.ico'
elif sys.platform == 'darwin' and os.path.exists('icon.icns'):
    icon_path = 'icon.icns'
elif os.path.exists('resources/icons/b3personalassistant.png'):
    icon_path = 'resources/icons/b3personalassistant.png'

# Analysis: Find all Python files and dependencies
a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include all module files
        ('modules/*.py', 'modules'),
        ('interfaces/desktop_app/*.py', 'interfaces/desktop_app'),
        ('interfaces/desktop_app/panels/*.py', 'interfaces/desktop_app/panels'),
        ('interfaces/desktop_app/dialogs/*.py', 'interfaces/desktop_app/dialogs'),

        # Include documentation
        ('README.md', '.'),
        ('ONBOARDING_GUIDE.md', '.'),
        ('VIDEO_EDITING_GUIDE.md', '.'),

        # Include any resource files if needed
        # ('resources/*', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtPrintSupport',
        'moviepy.editor',
        'moviepy.video.io.VideoFileClip',
        'moviepy.video.fx.all',
        'moviepy.audio.fx.all',
        'PIL.Image',
        'markdown',
        'pygments',
        'docx',
        'scenedetect',
        'cv2',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude tkinter if not needed
        'matplotlib',  # Exclude if not used
        'scipy',  # Exclude if not used
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ: Create Python zip archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='B3PersonalAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Use detected icon path
)

# COLLECT: Collect all files into distribution directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='B3PersonalAssistant',
)

# For macOS: Create app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='B3PersonalAssistant.app',
        icon=icon_path if icon_path and icon_path.endswith('.icns') else None,
        bundle_identifier='com.profb3.b3personalassistant',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleShortVersionString': '0.1.0-alpha',
            'CFBundleVersion': '0.1.0',
            'CFBundleDisplayName': 'B3 Personal Assistant',
            'CFBundleName': 'B3PersonalAssistant',
        },
    )
