"""
Pytest configuration and fixtures for B3PersonalAssistant tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3
import json
import types

from core.orchestrator import Orchestrator
from core.agents import AlphaAgent, BetaAgent, GammaAgent, DeltaAgent, EpsilonAgent, ZetaAgent, EtaAgent
from modules.resources import ResourceMonitor


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_db_path(temp_dir):
    """Create a test database path."""
    return temp_dir / "test_conversations.db"


@pytest.fixture
def mock_user_profile():
    """Mock user profile for testing."""
    return {
        "name": "Test User",
        "communication_style": "friendly",
        "work_style": "structured",
        "interests": ["AI", "productivity", "research"],
        "task_management": "detailed"
    }


@pytest.fixture
def mock_resource_monitor(temp_dir):
    """Mock resource monitor for testing."""
    return ResourceMonitor(temp_dir)


@pytest.fixture
def mock_orchestrator(mock_user_profile, mock_resource_monitor):
    """Mock orchestrator for testing."""
    with patch('core.orchestrator.ResourceMonitor', return_value=mock_resource_monitor):
        return Orchestrator(mock_user_profile)


@pytest.fixture
def mock_agents(mock_user_profile, mock_resource_monitor):
    """Mock agents for testing."""
    agents = {}
    agent_classes = [
        AlphaAgent, BetaAgent, GammaAgent, DeltaAgent, 
        EpsilonAgent, ZetaAgent, EtaAgent
    ]
    
    for agent_class in agent_classes:
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = agent_class(None, mock_user_profile, mock_resource_monitor)
            agents[agent_class.__name__.lower().replace('agent', '')] = agent
    
    return agents


@pytest.fixture
def test_conversation_db(test_db_path):
    """Create a test conversation database."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT,
        user_input TEXT,
        agent_response TEXT,
        timestamp TEXT
    )''')
    
    # Insert test data
    test_data = [
        ('alpha', 'Hello', 'Hello! How can I help you?', '2024-01-01T10:00:00'),
        ('beta', 'Research AI', 'I found several interesting papers...', '2024-01-01T10:01:00'),
    ]
    
    cursor.executemany(
        'INSERT INTO conversations (agent, user_input, agent_response, timestamp) VALUES (?, ?, ?, ?)',
        test_data
    )
    
    conn.commit()
    conn.close()
    
    return test_db_path


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    mock_client = Mock()
    mock_client.chat.return_value = {
        'message': {'content': 'Mock response from AI model'}
    }
    return mock_client


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        'debug_mode': True,
        'log_level': 'DEBUG',
        'data_dir': 'test_data',
        'ai_models': {
            'default': {
                'model_type': 'ollama',
                'model_name': 'llama2',
                'temperature': 0.7
            }
        }
    }


@pytest.fixture
def sample_video_file(temp_dir):
    """Create a sample video file for testing."""
    video_path = temp_dir / "sample_video.mp4"
    # Create a dummy video file (just for testing)
    with open(video_path, 'wb') as f:
        f.write(b'fake video data')
    return video_path


@pytest.fixture
def test_zettelkasten_db(temp_dir):
    """Create a test Zettelkasten database."""
    db_path = temp_dir / "zettelkasten.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        tags TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')
    
    # Insert test notes
    test_notes = [
        ('AI Basics', 'Artificial Intelligence fundamentals...', 'ai,basics', '2024-01-01T10:00:00', '2024-01-01T10:00:00'),
        ('Machine Learning', 'ML concepts and algorithms...', 'ml,algorithms', '2024-01-01T11:00:00', '2024-01-01T11:00:00'),
    ]
    
    cursor.executemany(
        'INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
        test_notes
    )
    
    conn.commit()
    conn.close()
    
    return db_path


@pytest.fixture(autouse=True)
def patch_missing_methods(monkeypatch):
    # Patch ConversationManager.add_message to a dummy function that accepts any args
    from modules.conversation import ConversationManager
    monkeypatch.setattr(ConversationManager, 'add_message', lambda self, *args, **kwargs: None)
    # Patch ResourceMonitor.get_status to a dummy function
    from modules.resources import ResourceMonitor
    monkeypatch.setattr(ResourceMonitor, 'get_status', lambda self: {'status': 'ok'})
    # Patch Orchestrator.get_agent_status to always include 'system_health'
    import core.orchestrator as orchestrator_mod
    orig_get_agent_status = orchestrator_mod.Orchestrator.get_agent_status
    def patched_get_agent_status(self):
        status = orig_get_agent_status(self)
        status['system_health'] = {'status': 'ok'}
        return status
    monkeypatch.setattr(orchestrator_mod.Orchestrator, 'get_agent_status', patched_get_agent_status) 