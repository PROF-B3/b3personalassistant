"""
Setup script for B3PersonalAssistant

A multi-agent AI personal assistant system using local Ollama models.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="B3PersonalAssistant",
    version="1.0.0",
    author="B3PersonalAssistant Team",
    author_email="contact@b3personalassistant.com",
    description="A multi-agent AI personal assistant system using local Ollama models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/B3PersonalAssistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "tkinter",  # Usually included with Python
        ],
        "optional": [
            "requests>=2.28.0",
            "numpy>=1.21.0",
            "pandas>=1.5.0",
            "matplotlib>=3.5.0",
            "networkx>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "b3pa=B3PersonalAssistant.interfaces.cli_launcher:main",
            "b3pa-gui=B3PersonalAssistant.interfaces.gui_launcher:main",
        ],
    },
    include_package_data=True,
    package_data={
        "B3PersonalAssistant": [
            "config.json",
            "*.md",
        ],
    },
    keywords="ai assistant personal ollama multi-agent zettelkasten",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/B3PersonalAssistant/issues",
        "Source": "https://github.com/yourusername/B3PersonalAssistant",
        "Documentation": "https://github.com/yourusername/B3PersonalAssistant/wiki",
    },
) 