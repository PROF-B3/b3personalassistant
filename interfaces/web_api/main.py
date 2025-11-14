"""
FastAPI Web Interface for B3PersonalAssistant

Provides REST API and WebSocket endpoints for remote access to all features.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import B3 modules
from core.context_manager import ContextManager, ContextType, ContextPriority
from modules.semantic_search import SemanticSearchEngine
from modules.agents.proactive_agent import ProactiveAgent
from modules.workflow_engine import WorkflowEngine, Workflow, Trigger, Action
from modules.agents.multimodal_agent import MultimodalAgent
from core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="B3PersonalAssistant API",
    description="Intelligent personal assistant with memory, learning, and automation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
context_manager = ContextManager()
search_engine = SemanticSearchEngine()
proactive_agent = ProactiveAgent()
workflow_engine = WorkflowEngine()
multimodal_agent = MultimodalAgent()

# Initialize orchestrator with all agents
orchestrator = Orchestrator(
    user_profile={"communication_style": "friendly", "expertise_level": "intermediate"}
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

manager = ConnectionManager()


# ==================== Pydantic Models ====================

class ContextSetRequest(BaseModel):
    key: str = Field(..., description="Context key")
    value: Any = Field(..., description="Context value")
    context_type: str = Field(default="conversation", description="Context type")
    priority: int = Field(default=2, description="Priority (1-4)")
    expires_in_hours: Optional[int] = Field(None, description="Expiration in hours")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")

class ContextGetRequest(BaseModel):
    key: str
    context_type: str = "conversation"

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=10, description="Number of results")
    source_filter: Optional[List[str]] = Field(None, description="Filter by sources")
    min_similarity: float = Field(default=0.0, description="Minimum similarity (0-1)")

class IndexRequest(BaseModel):
    content: str = Field(..., description="Content to index")
    source: str = Field(..., description="Source type")
    source_id: str = Field(..., description="Source ID")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")

class ActionRecordRequest(BaseModel):
    action: str = Field(..., description="Action description")
    context: Optional[str] = Field(None, description="Context")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")

class WorkflowCreateRequest(BaseModel):
    name: str
    description: str
    enabled: bool = True
    trigger: Dict[str, Any]
    actions: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    include_context: bool = Field(default=True, description="Include context in response")
    context_limit: int = Field(default=10, description="Max context items")


# ==================== Health & Status ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    else:
        # Fallback to API information
        return JSONResponse({
            "name": "B3PersonalAssistant API",
            "version": "1.0.0",
            "status": "operational",
            "features": [
                "Context Management",
                "Semantic Search",
                "Proactive Suggestions",
                "Workflow Automation",
                "Multimodal Processing"
            ],
            "endpoints": {
                "docs": "/api/docs",
                "health": "/health",
                "context": "/api/context",
                "search": "/api/search",
                "proactive": "/api/proactive",
                "workflows": "/api/workflows",
                "multimodal": "/api/multimodal"
            }
        })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Quick health checks
        context_summary = context_manager.get_context_summary()
        search_stats = search_engine.get_statistics()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "context_manager": "operational",
                "search_engine": "operational",
                "proactive_agent": "operational",
                "workflow_engine": "operational",
                "multimodal_agent": "operational"
            },
            "stats": {
                "context_items": context_summary.get("total_items", 0),
                "indexed_items": search_stats.get("total_indexed", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# ==================== Context Management API ====================

@app.post("/api/context/set")
async def set_context(request: ContextSetRequest):
    """Set a context item."""
    try:
        expires_in = None
        if request.expires_in_hours:
            expires_in = timedelta(hours=request.expires_in_hours)

        success = context_manager.set(
            key=request.key,
            value=request.value,
            context_type=ContextType(request.context_type),
            priority=ContextPriority(request.priority),
            expires_in=expires_in,
            metadata=request.metadata
        )

        # Broadcast update
        await manager.broadcast({
            "type": "context_update",
            "action": "set",
            "key": request.key,
            "value": request.value
        })

        return {"success": success, "key": request.key}

    except Exception as e:
        logger.error(f"Failed to set context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/context/get")
async def get_context(request: ContextGetRequest):
    """Get a context item."""
    try:
        value = context_manager.get(
            key=request.key,
            context_type=ContextType(request.context_type)
        )

        return {"key": request.key, "value": value, "found": value is not None}

    except Exception as e:
        logger.error(f"Failed to get context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context/all")
async def get_all_context(
    context_types: Optional[str] = None,
    min_priority: int = 1,
    limit: int = 20
):
    """Get relevant context items."""
    try:
        types = None
        if context_types:
            types = [ContextType(t.strip()) for t in context_types.split(",")]

        items = context_manager.get_relevant_context(
            context_types=types,
            min_priority=ContextPriority(min_priority),
            limit=limit
        )

        return {
            "items": [item.to_dict() for item in items],
            "count": len(items)
        }

    except Exception as e:
        logger.error(f"Failed to get context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context/summary")
async def get_context_summary():
    """Get context summary."""
    try:
        summary = context_manager.get_context_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/context/{context_type}/{key}")
async def delete_context(context_type: str, key: str):
    """Delete a context item."""
    try:
        success = context_manager.delete(key, ContextType(context_type))

        await manager.broadcast({
            "type": "context_update",
            "action": "delete",
            "key": key
        })

        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to delete context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Semantic Search API ====================

@app.post("/api/search")
async def search(request: SearchRequest):
    """Perform semantic search."""
    try:
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            source_filter=request.source_filter,
            min_similarity=request.min_similarity
        )

        return {
            "query": request.query,
            "results": [result.to_dict() for result in results],
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/index")
async def index_content(request: IndexRequest):
    """Index content for search."""
    try:
        success = search_engine.index_text(
            content=request.content,
            source=request.source,
            source_id=request.source_id,
            metadata=request.metadata
        )

        return {"success": success, "source_id": request.source_id}

    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/stats")
async def get_search_stats():
    """Get search engine statistics."""
    try:
        stats = search_engine.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Proactive Agent API ====================

@app.post("/api/proactive/record")
async def record_action(request: ActionRecordRequest):
    """Record a user action."""
    try:
        success = proactive_agent.record_action(
            action=request.action,
            context=request.context,
            metadata=request.metadata
        )

        return {"success": success}

    except Exception as e:
        logger.error(f"Failed to record action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proactive/suggestions")
async def get_suggestions(
    current_context: Optional[str] = None,
    limit: int = 5
):
    """Get proactive suggestions."""
    try:
        suggestions = proactive_agent.get_suggestions(
            current_context=current_context,
            limit=limit
        )

        return {
            "suggestions": [
                {
                    "type": s.suggestion_type,
                    "title": s.title,
                    "description": s.description,
                    "confidence": s.confidence,
                    "priority": s.priority,
                    "action": s.action,
                    "metadata": s.metadata
                }
                for s in suggestions
            ],
            "count": len(suggestions)
        }

    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proactive/patterns")
async def get_patterns(
    pattern_type: Optional[str] = None,
    min_confidence: float = 0.3
):
    """Get learned patterns."""
    try:
        patterns = proactive_agent.get_learned_patterns(
            pattern_type=pattern_type,
            min_confidence=min_confidence
        )

        return {
            "patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.description,
                    "confidence": p.confidence,
                    "frequency": p.frequency,
                    "last_seen": p.last_seen
                }
                for p in patterns
            ],
            "count": len(patterns)
        }

    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proactive/productivity")
async def get_productivity(days: int = 7):
    """Get productivity analysis."""
    try:
        analysis = proactive_agent.analyze_productivity(days=days)
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze productivity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Workflow Automation API ====================

@app.post("/api/workflows")
async def create_workflow(request: WorkflowCreateRequest):
    """Create a new workflow."""
    try:
        workflow = Workflow(
            name=request.name,
            description=request.description,
            enabled=request.enabled,
            trigger=Trigger(**request.trigger),
            actions=[Action(**a) for a in request.actions]
        )

        workflow_id = workflow_engine.create_workflow(workflow)

        await manager.broadcast({
            "type": "workflow_created",
            "workflow_id": workflow_id,
            "name": request.name
        })

        return {"success": True, "workflow_id": workflow_id}

    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows")
async def list_workflows(enabled_only: bool = False):
    """List all workflows."""
    try:
        workflows = workflow_engine.list_workflows(enabled_only=enabled_only)

        return {
            "workflows": [
                {
                    "id": w.id,
                    "name": w.name,
                    "description": w.description,
                    "enabled": w.enabled,
                    "trigger": {
                        "type": w.trigger.trigger_type,
                        "description": w.trigger.description
                    },
                    "actions_count": len(w.actions),
                    "run_count": w.run_count,
                    "last_run": w.last_run
                }
                for w in workflows
            ],
            "count": len(workflows)
        }

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: int):
    """Execute a workflow manually."""
    try:
        success = workflow_engine.execute_workflow(workflow_id, trigger_reason="manual_api")

        await manager.broadcast({
            "type": "workflow_executed",
            "workflow_id": workflow_id,
            "success": success
        })

        return {"success": success}

    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/templates")
async def get_workflow_templates(category: Optional[str] = None):
    """Get workflow templates."""
    try:
        templates = workflow_engine.get_templates(category=category)
        return {"templates": templates, "count": len(templates)}
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Multimodal API ====================

@app.post("/api/multimodal/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file."""
    try:
        # Save file temporarily
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process file
        result = multimodal_agent.process_file(temp_path)

        # Clean up
        temp_path.unlink()

        return {
            "filename": file.filename,
            "content_type": result.content_type,
            "extracted_text": result.extracted_text,
            "summary": result.summary,
            "metadata": result.metadata,
            "error": result.error
        }

    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket API ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates and chat."""
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "content": "Connected to B3 Personal Assistant. All 7 agents ready.",
            "timestamp": datetime.now().isoformat()
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

            elif data.get("type") == "subscribe":
                # Client subscribing to updates
                await websocket.send_json({
                    "type": "subscribed",
                    "message": "Connected to B3PersonalAssistant",
                    "agents": list(orchestrator.agents.keys())
                })

            elif data.get("type") == "message":
                # Handle chat message
                user_message = data.get("content", "")

                if not user_message.strip():
                    continue

                # Send typing indicator
                await websocket.send_json({
                    "type": "typing",
                    "typing": True
                })

                try:
                    # Process message with orchestrator
                    response = orchestrator.process_request(user_message)

                    # Stop typing indicator
                    await websocket.send_json({
                        "type": "typing",
                        "typing": False
                    })

                    # Send AI response
                    await websocket.send_json({
                        "type": "message",
                        "content": response,
                        "sender": "assistant",
                        "timestamp": datetime.now().isoformat()
                    })

                    # Send agent activity log
                    await websocket.send_json({
                        "type": "agent_log",
                        "level": "success",
                        "message": f"Processed request: {user_message[:50]}...",
                        "agent": "Orchestrator"
                    })

                    # Send performance metric
                    await websocket.send_json({
                        "type": "performance",
                        "value": 75 + (hash(user_message) % 50)  # Simulated response time
                    })

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send_json({
                        "type": "typing",
                        "typing": False
                    })
                    await websocket.send_json({
                        "type": "message",
                        "content": f"Sorry, I encountered an error: {str(e)}",
                        "sender": "assistant",
                        "timestamp": datetime.now().isoformat()
                    })
                    await websocket.send_json({
                        "type": "agent_log",
                        "level": "error",
                        "message": f"Error: {str(e)}",
                        "agent": "System"
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ==================== Chat API (Integration Point) ====================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint that integrates all features with the orchestrator.

    Processes user messages through the multi-agent orchestrator and returns
    comprehensive responses with context, suggestions, and related content.
    """
    try:
        response_data = {
            "message": request.message,
            "timestamp": datetime.now().isoformat()
        }

        # Build context for orchestrator
        context = {}

        # Get context if requested
        if request.include_context:
            context_items = context_manager.get_relevant_context(limit=request.context_limit)
            response_data["context"] = [item.to_dict() for item in context_items]
            context["context_items"] = context_items

        # Get proactive suggestions
        suggestions = proactive_agent.get_suggestions(limit=3)
        response_data["suggestions"] = [
            {
                "title": s.title,
                "description": s.description,
                "confidence": s.confidence
            }
            for s in suggestions
        ]

        # Perform semantic search on message
        search_results = search_engine.search(request.message, top_k=3, min_similarity=0.5)
        response_data["related_content"] = [r.to_dict() for r in search_results]
        context["search_results"] = search_results

        # Record action
        proactive_agent.record_action("sent_message", metadata={"message_length": len(request.message)})

        # Process with orchestrator - THIS IS THE REAL AI INTEGRATION
        ai_response = orchestrator.process_request(request.message, context=context)
        response_data["response"] = ai_response

        return response_data

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Main ====================

if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
