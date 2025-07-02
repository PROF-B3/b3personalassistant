#!/usr/bin/env python3
"""
Database initialization script for B3PersonalAssistant.

This script sets up the database and creates initial data.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
import json
from datetime import datetime
from databases.manager import DatabaseManager


def init_database():
    """Initialize the database with tables and sample data."""
    print("🚀 Initializing B3PersonalAssistant Database...")
    
    # Create database manager
    db_manager = DatabaseManager()
    
    # Create sample user profile
    print("📝 Creating sample user profile...")
    user = db_manager.create_user_profile(
        name="Prof. B3",
        email="prof.b3@temporal-research.org",
        communication_style="friendly",
        work_style="structured",
        interests=["AI", "productivity", "research", "temporal physics"],
        task_management="detailed"
    )
    
    # Create sample tasks
    print("📋 Creating sample tasks...")
    sample_tasks = [
        {
            "title": "Set up B3PersonalAssistant",
            "description": "Initialize and configure the multi-agent system",
            "priority": "high",
            "tags": ["setup", "configuration"]
        },
        {
            "title": "Test video processing workflow",
            "description": "Verify the collaborative video editing capabilities",
            "priority": "medium",
            "tags": ["testing", "video", "workflow"]
        },
        {
            "title": "Document system architecture",
            "description": "Create comprehensive documentation for the 7-agent system",
            "priority": "medium",
            "tags": ["documentation", "architecture"]
        }
    ]
    
    for task_data in sample_tasks:
        db_manager.create_task(
            user_id=user.id,
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            tags=task_data["tags"]
        )
    
    # Create sample knowledge notes
    print("📚 Creating sample knowledge notes...")
    sample_notes = [
        {
            "title": "Multi-Agent AI Systems",
            "content": "Multi-agent systems consist of multiple intelligent agents that work together to solve complex problems. Each agent has specialized capabilities and can communicate with others.",
            "tags": ["ai", "multi-agent", "systems"],
            "note_type": "reference"
        },
        {
            "title": "Zettelkasten Method",
            "content": "The Zettelkasten method is a note-taking and knowledge management system that emphasizes connections between ideas through linking and tagging.",
            "tags": ["knowledge-management", "zettelkasten", "productivity"],
            "note_type": "note"
        },
        {
            "title": "Video Processing Workflow",
            "content": "The B3 video processing workflow involves scene detection, AI image generation, text overlay creation, and multi-agent collaboration for creative projects.",
            "tags": ["video", "workflow", "ai-generation", "creative"],
            "note_type": "project"
        }
    ]
    
    for note_data in sample_notes:
        db_manager.create_knowledge_note(
            user_id=user.id,
            title=note_data["title"],
            content=note_data["content"],
            tags=note_data["tags"],
            note_type=note_data["note_type"]
        )
    
    # Create sample conversations
    print("💬 Creating sample conversations...")
    sample_conversations = [
        {
            "agent": "alpha",
            "user_input": "Hello, can you help me set up the system?",
            "agent_response": "Hello! I'm Alpha, your Chief Assistant. I'd be happy to help you set up the B3PersonalAssistant system. Let me coordinate with the other agents to get everything configured properly."
        },
        {
            "agent": "beta",
            "user_input": "Research the latest AI trends",
            "agent_response": "I've researched the latest AI trends. Key developments include: 1) Large Language Models becoming more efficient, 2) Multimodal AI systems, 3) AI agents and automation, 4) Edge AI deployment. Would you like me to dive deeper into any specific area?"
        },
        {
            "agent": "gamma",
            "user_input": "Save this information about Zettelkasten",
            "agent_response": "I've saved the information about Zettelkasten to your knowledge base. I've tagged it appropriately and created connections to related topics like knowledge management and productivity systems."
        }
    ]
    
    for conv_data in sample_conversations:
        db_manager.store_conversation(
            user_id=user.id,
            agent=conv_data["agent"],
            user_input=conv_data["user_input"],
            agent_response=conv_data["agent_response"]
        )
    
    # Get database statistics
    stats = db_manager.get_database_stats()
    
    print("\n✅ Database initialization complete!")
    print(f"📊 Database Statistics:")
    print(f"   - User profiles: {stats['user_profiles']}")
    print(f"   - Conversations: {stats['conversations']}")
    print(f"   - Tasks: {stats['tasks']}")
    print(f"   - Knowledge notes: {stats['knowledge_notes']}")
    print(f"   - Database size: {stats['database_size_mb']:.2f} MB")
    
    print(f"\n👤 Sample user created:")
    print(f"   - Name: {user.name}")
    print(f"   - Email: {user.email}")
    print(f"   - ID: {user.id}")
    
    print("\n🎯 Next steps:")
    print("   1. Run the assistant: python run_assistant.py")
    print("   2. Test the CLI: python -m interfaces.cli_launcher")
    print("   3. Check the GUI: python -m interfaces.gui_launcher")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1) 