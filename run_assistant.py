#!/usr/bin/env python3
"""
B3PersonalAssistant - Main Entry Point

This script serves as the main entry point for the B3PersonalAssistant system.
It handles user profile setup, interface selection, and system initialization.

Features:
- User profile management and personalization
- Interface selection (GUI/CLI)
- System initialization and onboarding
- Error handling and graceful shutdown

Usage:
    python run_assistant.py [--gui|--cli]
    python run_assistant.py --setup-profile

Example:
    >>> python run_assistant.py --gui
    # Launches the GUI interface
    >>> python run_assistant.py --cli
    # Launches the CLI interface
    >>> python run_assistant.py --setup-profile
    # Interactive profile setup
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('databases/b3_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_user_profile() -> Optional[Dict[str, Any]]:
    """
    Load user profile from JSON file.
    
    Returns:
        User profile dictionary or None if not found
        
    Example:
        >>> profile = load_user_profile()
        >>> if profile:
        ...     print(f"Welcome back, {profile['name']}!")
        ... else:
        ...     print("No profile found")
    """
    profile_path = Path("databases/user_profile.json")
    if profile_path.exists():
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
    return None

def save_user_profile(profile: Dict[str, Any]) -> bool:
    """
    Save user profile to JSON file.
    
    Args:
        profile: User profile dictionary
    
    Returns:
        True if saved successfully, False otherwise
        
    Example:
        >>> profile = {"name": "John", "communication_style": "friendly"}
        >>> success = save_user_profile(profile)
        >>> print("Profile saved" if success else "Failed to save profile")
    """
    try:
        profile_path = Path("databases/user_profile.json")
        profile_path.parent.mkdir(exist_ok=True)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        return False

def setup_user_profile() -> Dict[str, Any]:
    """
    Interactive user profile setup with onboarding story.
    
    Guides users through creating their personalized profile with
    the Prof. B3 temporal transfer story as an engaging introduction.
    
    Returns:
        Complete user profile dictionary
        
    Example:
        >>> profile = setup_user_profile()
        >>> print(f"Profile created for {profile['name']}")
    """
    print("\n" + "="*80)
    print("🎓 B3PersonalAssistant - Personal Profile Setup")
    print("="*80)
    
    # Prof. B3 Temporal Transfer Story
    print("\n📚 The Story of Professor B3")
    print("-" * 50)
    print("""
In the year 2157, Professor B3 was a brilliant AI researcher working on temporal 
transfer technology. During a critical experiment, a temporal anomaly occurred, 
sending fragments of B3's consciousness back through time to 2024.

These fragments coalesced into four specialized AI agents, each carrying different 
aspects of B3's knowledge and personality:

🔹 Alpha (Α) - The Chief Assistant, carrying B3's leadership and coordination skills
🔹 Beta (Β) - The Analyst, embodying B3's research and analytical abilities  
🔹 Gamma (Γ) - The Knowledge Manager, preserving B3's vast knowledge base
🔹 Delta (Δ) - The Task Coordinator, managing B3's organizational systems

Now, these agents are ready to assist you, adapting to your unique preferences 
and working style. Let's personalize your experience!
    """)
    
    profile = {}
    
    # Basic Information
    print("\n👤 Basic Information")
    print("-" * 30)
    profile['name'] = input("What's your name? ").strip() or "User"
    profile['role'] = input("What's your primary role/profession? ").strip() or "Professional"
    
    # Communication Preferences
    print("\n💬 Communication Style")
    print("-" * 30)
    print("How would you like the agents to communicate with you?")
    print("1. Friendly (with emojis and casual language)")
    print("2. Formal (professional and structured)")
    print("3. Concise (brief and to the point)")
    print("4. Casual (relaxed and conversational)")
    
    style_choice = input("Choose (1-4): ").strip()
    style_map = {
        '1': 'friendly',
        '2': 'formal', 
        '3': 'concise',
        '4': 'casual'
    }
    profile['communication_style'] = style_map.get(style_choice, 'friendly')
    
    # Work Style
    print("\n⚡ Work Style Preferences")
    print("-" * 30)
    print("How do you prefer to work?")
    print("1. Structured (detailed plans and schedules)")
    print("2. Flexible (adaptive and spontaneous)")
    print("3. Collaborative (lots of interaction and discussion)")
    print("4. Independent (minimal guidance needed)")
    
    work_choice = input("Choose (1-4): ").strip()
    work_map = {
        '1': 'structured',
        '2': 'flexible',
        '3': 'collaborative', 
        '4': 'independent'
    }
    profile['work_style'] = work_map.get(work_choice, 'flexible')
    
    # Interests and Focus Areas
    print("\n🎯 Focus Areas")
    print("-" * 30)
    print("What are your main areas of interest? (comma-separated)")
    interests = input("e.g., AI, productivity, research, creativity: ").strip()
    profile['interests'] = [interest.strip() for interest in interests.split(',') if interest.strip()]
    
    # Task Management Preferences
    print("\n📋 Task Management")
    print("-" * 30)
    print("How do you prefer to manage tasks?")
    print("1. Detailed (with descriptions, priorities, deadlines)")
    print("2. Simple (basic task lists)")
    print("3. Categorized (organized by projects/areas)")
    print("4. Time-based (focused on scheduling)")
    
    task_choice = input("Choose (1-4): ").strip()
    task_map = {
        '1': 'detailed',
        '2': 'simple',
        '3': 'categorized',
        '4': 'time-based'
    }
    profile['task_preferences'] = task_map.get(task_choice, 'simple')
    
    # Knowledge Management Preferences
    print("\n📚 Knowledge Management")
    print("-" * 30)
    print("How do you prefer to organize information?")
    print("1. Zettelkasten (linked notes with connections)")
    print("2. Hierarchical (folders and categories)")
    print("3. Tagged (flexible tagging system)")
    print("4. Timeline (chronological organization)")
    
    knowledge_choice = input("Choose (1-4): ").strip()
    knowledge_map = {
        '1': 'zettelkasten',
        '2': 'hierarchical',
        '3': 'tagged',
        '4': 'timeline'
    }
    profile['knowledge_preferences'] = knowledge_map.get(knowledge_choice, 'zettelkasten')
    
    # Notification Preferences
    print("\n🔔 Notifications")
    print("-" * 30)
    print("How often would you like updates?")
    print("1. Real-time (immediate notifications)")
    print("2. Periodic (regular updates)")
    print("3. On-demand (only when you ask)")
    print("4. Minimal (only important alerts)")
    
    notify_choice = input("Choose (1-4): ").strip()
    notify_map = {
        '1': 'real-time',
        '2': 'periodic',
        '3': 'on-demand',
        '4': 'minimal'
    }
    profile['notification_preferences'] = notify_map.get(notify_choice, 'on-demand')
    
    # Save profile
    if save_user_profile(profile):
        print(f"\n✅ Profile saved successfully!")
        print(f"Welcome to B3PersonalAssistant, {profile['name']}!")
        print("\nThe four agents are now personalized to your preferences:")
        print(f"• Alpha will coordinate with a {profile['communication_style']} style")
        print(f"• Beta will research your interests: {', '.join(profile['interests'])}")
        print(f"• Gamma will organize knowledge using {profile['knowledge_preferences']}")
        print(f"• Delta will manage tasks with {profile['task_preferences']} approach")
    else:
        print("\n❌ Failed to save profile, but you can continue with default settings")
    
    return profile

def main():
    """
    Main entry point for B3PersonalAssistant.
    
    Handles command line arguments, profile management, and interface selection.
    """
    parser = argparse.ArgumentParser(
        description="B3PersonalAssistant - Multi-Agent AI Personal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_assistant.py --gui          # Launch GUI interface
  python run_assistant.py --cli          # Launch CLI interface  
  python run_assistant.py --setup-profile # Interactive profile setup
  python run_assistant.py                # Auto-detect interface
        """
    )
    
    parser.add_argument(
        '--gui', 
        action='store_true',
        help='Launch GUI interface'
    )
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Launch CLI interface'
    )
    parser.add_argument(
        '--setup-profile',
        action='store_true', 
        help='Interactive profile setup'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Handle profile setup
    if args.setup_profile:
        setup_user_profile()
        return
    
    # Load or create user profile
    user_profile = load_user_profile()
    if not user_profile:
        print("\n🔧 No user profile found. Let's set up your personalized experience!")
        user_profile = setup_user_profile()
    
    # Load configuration
    config = get_config()
    if args.config:
        # TODO: Load custom config file
        pass
    
    # Determine interface
    if args.gui:
        interface = 'gui'
    elif args.cli:
        interface = 'cli'
    else:
        # Auto-detect based on environment
        interface = 'cli'  # Default to CLI for now
    
    # Launch appropriate interface
    try:
        if interface == 'gui':
            from interfaces.gui_launcher import launch_gui
            print(f"\n🚀 Launching GUI interface for {user_profile['name']}...")
            launch_gui(config, user_profile)
        else:
            from interfaces.cli_launcher import launch_cli
            print(f"\n🚀 Launching CLI interface for {user_profile['name']}...")
            launch_cli(user_profile, config)
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using B3PersonalAssistant.")
    except Exception as e:
        logger.error(f"Error launching interface: {e}")
        print(f"\n❌ Error: {e}")
        print("Try running with --setup-profile to reconfigure your profile.")

if __name__ == "__main__":
    main() 