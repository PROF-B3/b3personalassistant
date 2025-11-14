"""
Comprehensive test suite for B3 Personal Assistant Web API

Tests cover:
- API endpoints
- WebSocket connections
- Chat functionality
- Context management
- Search functionality
- Orchestrator integration
"""

import pytest
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.web_api.main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self):
        """Test the root endpoint serves HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestContextAPI:
    """Test context management endpoints"""

    def test_set_context(self):
        """Test setting context"""
        response = client.post(
            "/api/context/set",
            json={
                "key": "test_key",
                "value": "test_value",
                "context_type": "conversation",
                "priority": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_get_context(self):
        """Test retrieving context"""
        # First set a context
        client.post(
            "/api/context/set",
            json={
                "key": "retrieve_test",
                "value": "retrieve_value",
                "context_type": "conversation"
            }
        )

        # Then retrieve it
        response = client.post(
            "/api/context/get",
            json={
                "key": "retrieve_test",
                "context_type": "conversation"
            }
        )
        assert response.status_code == 200

    def test_get_all_context(self):
        """Test getting all context items"""
        response = client.get("/api/context/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)

    def test_delete_context(self):
        """Test deleting context"""
        # Set a context
        client.post(
            "/api/context/set",
            json={
                "key": "delete_test",
                "value": "value_to_delete",
                "context_type": "conversation"
            }
        )

        # Delete it
        response = client.delete("/api/context/conversation/delete_test")
        assert response.status_code == 200


class TestSearchAPI:
    """Test semantic search endpoints"""

    def test_index_content(self):
        """Test indexing content for search"""
        response = client.post(
            "/api/search/index",
            json={
                "content": "This is test content for searching",
                "metadata": {"test": True}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"

    def test_search(self):
        """Test semantic search"""
        # Index some content first
        client.post(
            "/api/search/index",
            json={
                "content": "Python programming language tutorial",
                "metadata": {"category": "programming"}
            }
        )

        # Search for it
        response = client.post(
            "/api/search",
            json={
                "query": "python tutorial",
                "top_k": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)

    def test_search_stats(self):
        """Test search statistics endpoint"""
        response = client.get("/api/search/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data


class TestProactiveAgent:
    """Test proactive agent endpoints"""

    def test_record_action(self):
        """Test recording user actions"""
        response = client.post(
            "/api/proactive/record",
            json={
                "action": "test_action",
                "metadata": {"test": True}
            }
        )
        assert response.status_code == 200

    def test_get_suggestions(self):
        """Test getting proactive suggestions"""
        response = client.get("/api/proactive/suggestions?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_get_patterns(self):
        """Test pattern detection"""
        response = client.get("/api/proactive/patterns")
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data


class TestWorkflowAPI:
    """Test workflow engine endpoints"""

    def test_create_workflow(self):
        """Test creating a workflow"""
        response = client.post(
            "/api/workflows",
            json={
                "name": "test_workflow",
                "description": "Test workflow description",
                "trigger": {
                    "type": "keyword",
                    "config": {"keywords": ["test"]}
                },
                "actions": [
                    {
                        "type": "log",
                        "config": {"message": "Test action"}
                    }
                ]
            }
        )
        assert response.status_code == 200

    def test_list_workflows(self):
        """Test listing all workflows"""
        response = client.get("/api/workflows")
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data


class TestChatAPI:
    """Test chat and orchestrator integration"""

    def test_chat_basic(self):
        """Test basic chat endpoint"""
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello, how are you?",
                "include_context": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "timestamp" in data

    def test_chat_with_context(self):
        """Test chat with context"""
        # Set some context first
        client.post(
            "/api/context/set",
            json={
                "key": "chat_test_context",
                "value": "test context value",
                "context_type": "conversation"
            }
        )

        # Chat with context
        response = client.post(
            "/api/chat",
            json={
                "message": "Tell me about the context",
                "include_context": True,
                "context_limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "context" in data
        assert "suggestions" in data
        assert "related_content" in data

    def test_chat_research_intent(self):
        """Test chat with research intent"""
        response = client.post(
            "/api/chat",
            json={
                "message": "Research quantum computing for me",
                "include_context": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_chat_task_intent(self):
        """Test chat with task creation intent"""
        response = client.post(
            "/api/chat",
            json={
                "message": "Create a task to review code",
                "include_context": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


class TestWebSocket:
    """Test WebSocket functionality"""

    def test_websocket_connection(self):
        """Test basic WebSocket connection"""
        with client.websocket_connect("/ws") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "system"
            assert "Connected" in data["content"]

    def test_websocket_ping(self):
        """Test WebSocket ping/pong"""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send ping
            websocket.send_json({"type": "ping"})

            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_subscribe(self):
        """Test WebSocket subscription"""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Subscribe
            websocket.send_json({"type": "subscribe"})

            # Receive subscription confirmation
            response = websocket.receive_json()
            assert response["type"] == "subscribed"
            assert "agents" in response

    def test_websocket_chat(self):
        """Test WebSocket chat messaging"""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send a message
            websocket.send_json({
                "type": "message",
                "content": "Hello B3!"
            })

            # Receive typing indicator
            typing_msg = websocket.receive_json()
            assert typing_msg["type"] == "typing"
            assert typing_msg["typing"] == True

            # Receive stop typing
            stop_typing = websocket.receive_json()
            assert stop_typing["type"] == "typing"
            assert stop_typing["typing"] == False

            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert "content" in response
            assert response["sender"] == "assistant"

            # Receive agent log
            log = websocket.receive_json()
            assert log["type"] == "agent_log"

            # Receive performance metric
            perf = websocket.receive_json()
            assert perf["type"] == "performance"


# Integration Tests
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_workflow(self):
        """Test a complete workflow from indexing to chat"""
        # 1. Index some content
        client.post(
            "/api/search/index",
            json={
                "content": "FastAPI is a modern web framework for Python",
                "metadata": {"topic": "web"}
            }
        )

        # 2. Set some context
        client.post(
            "/api/context/set",
            json={
                "key": "current_topic",
                "value": "web development",
                "context_type": "conversation"
            }
        )

        # 3. Record an action
        client.post(
            "/api/proactive/record",
            json={
                "action": "learning",
                "metadata": {"topic": "FastAPI"}
            }
        )

        # 4. Chat about it
        response = client.post(
            "/api/chat",
            json={
                "message": "Tell me about FastAPI",
                "include_context": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "suggestions" in data
        assert "related_content" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
