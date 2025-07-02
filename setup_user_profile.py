#!/usr/bin/env python3
"""
Interactive script to set up a user profile for B3PersonalAssistant.
Stores profile in databases/user_profile.json.
"""
import os
import json
from pathlib import Path

def prompt_choice(prompt, choices):
    print(f"{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    while True:
        val = input("Enter number: ").strip()
        if val.isdigit() and 1 <= int(val) <= len(choices):
            return choices[int(val)-1]
        print("Invalid choice. Please try again.")

def prompt_list(prompt):
    print(f"{prompt} (comma-separated, e.g. AI, productivity, health)")
    val = input(": ").strip()
    return [v.strip() for v in val.split(",") if v.strip()]

def main():
    print("\n=== B3PersonalAssistant User Profile Setup ===\n")
    profile_path = Path("databases/user_profile.json")
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile = {}
    if profile_path.exists():
        with open(profile_path, 'r') as f:
            try:
                profile = json.load(f)
                print("Loaded existing profile. You can update any field. Leave blank to keep current value.\n")
            except Exception:
                profile = {}
    
    def get_input(field, prompt_text, default=None):
        val = input(f"{prompt_text} [{default if default else ''}]: ").strip()
        return val if val else default

    # User name
    profile['name'] = get_input('name', 'Your name', profile.get('name', ''))
    # Work style
    work_styles = ["Morning person", "Night owl", "Flexible", "Regular hours", "Other"]
    profile['work_style'] = prompt_choice("Your work style?", work_styles) if not profile.get('work_style') else get_input('work_style', 'Work style', profile['work_style'])
    # Areas of interest
    profile['interests'] = prompt_list("Your areas of interest") if not profile.get('interests') else get_input('interests', 'Areas of interest (comma-separated)', ', '.join(profile['interests'])).split(',')
    # Preferred communication style
    comm_styles = ["Concise", "Detailed", "Friendly", "Formal", "Casual", "Visual (diagrams)", "Voice (if supported)"]
    profile['communication_style'] = prompt_choice("Preferred communication style?", comm_styles) if not profile.get('communication_style') else get_input('communication_style', 'Communication style', profile['communication_style'])
    # Task management preferences
    task_prefs = ["Simple lists", "Kanban", "GTD (Getting Things Done)", "Eisenhower Matrix", "AI suggestions", "Other"]
    profile['task_management'] = prompt_choice("Task management preference?", task_prefs) if not profile.get('task_management') else get_input('task_management', 'Task management', profile['task_management'])
    # Knowledge organization preferences
    knowledge_prefs = ["Zettelkasten", "Folders", "Tags", "Mind maps", "AI summaries", "Other"]
    profile['knowledge_organization'] = prompt_choice("Knowledge organization preference?", knowledge_prefs) if not profile.get('knowledge_organization') else get_input('knowledge_organization', 'Knowledge organization', profile['knowledge_organization'])
    # Additional preferences
    profile['other_preferences'] = get_input('other_preferences', 'Other preferences (optional)', profile.get('other_preferences', ''))

    # Save profile
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    print(f"\n✅ Profile saved to {profile_path}\n")
    print(json.dumps(profile, indent=2))

if __name__ == "__main__":
    main() 