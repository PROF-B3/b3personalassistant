#!/usr/bin/env python3
"""
Mock Ollama Server for B3 Personal Assistant

This provides a minimal Ollama-compatible API server for testing and development
when the real Ollama service is not available. It responds to Ollama API calls
with simulated AI responses.

Usage:
    python mock_ollama_server.py

The server will start on http://localhost:11434 (Ollama's default port)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import random
import time
import asyncio

app = FastAPI(title="Mock Ollama Server", version="0.1.0")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    options: Optional[Dict[str, Any]] = None

class EmbeddingRequest(BaseModel):
    model: str
    prompt: str

# Simulated model responses
RESPONSES = [
    "I understand your question. Let me help you with that.",
    "Based on your request, here's what I suggest: {content}",
    "That's an interesting point. Here's my perspective on {content}",
    "I can help with that. The answer to your question about {content} is...",
    "Let me analyze that for you: {content}",
]

@app.get("/")
async def root():
    """Root endpoint - confirms server is running"""
    return {"message": "Mock Ollama Server Running", "version": "0.1.0"}

@app.get("/api/tags")
async def list_models():
    """List available models (mocked)"""
    return {
        "models": [
            {
                "name": "llama3.2:3b",
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 2000000000,
                "digest": "mock123",
                "details": {
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": "3B",
                    "quantization_level": "Q4_0"
                }
            },
            {
                "name": "mixtral",
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 5000000000,
                "digest": "mock456",
                "details": {
                    "format": "gguf",
                    "family": "mixtral",
                    "families": ["mixtral"],
                    "parameter_size": "8x7B",
                    "quantization_level": "Q4_0"
                }
            },
            {
                "name": "nomic-embed-text",
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 274000000,
                "digest": "mock789",
                "details": {
                    "format": "gguf",
                    "family": "nomic-embed",
                    "families": ["nomic"],
                    "parameter_size": "137M"
                }
            },
            {
                "name": "llava",
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 4500000000,
                "digest": "mock101",
                "details": {
                    "format": "gguf",
                    "family": "llava",
                    "families": ["llava"],
                    "parameter_size": "7B"
                }
            }
        ]
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat requests"""
    # Simulate processing delay
    await asyncio.sleep(0.5)

    # Extract user message
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    last_message = user_messages[-1].content

    # Generate mock response
    template = random.choice(RESPONSES)
    response_content = template.format(content=last_message[:50] + "..." if len(last_message) > 50 else last_message)

    # Add context-aware responses
    if "hello" in last_message.lower() or "hi" in last_message.lower():
        response_content = f"Hello! I'm {request.model} (mock mode). How can I assist you today?"
    elif "help" in last_message.lower():
        response_content = "I'm a mock AI assistant running in simulation mode. I can help answer questions, though my responses are simulated. How can I help you?"
    elif "?" in last_message:
        response_content = f"That's a great question about '{last_message[:100]}'. In a real setup, I would provide a detailed answer here."

    return {
        "model": request.model,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "message": {
            "role": "assistant",
            "content": response_content
        },
        "done": True,
        "total_duration": 500000000,
        "load_duration": 100000000,
        "prompt_eval_count": len(last_message.split()),
        "eval_count": len(response_content.split()),
        "eval_duration": 400000000
    }

@app.post("/api/embeddings")
async def embeddings(request: EmbeddingRequest):
    """Generate mock embeddings"""
    # Generate a random embedding vector (768 dimensions for nomic-embed-text)
    embedding = [random.uniform(-1, 1) for _ in range(768)]

    return {
        "embedding": embedding
    }

@app.get("/api/version")
async def version():
    """Return mock version info"""
    return {
        "version": "0.1.0-mock"
    }

if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🚀 Starting Mock Ollama Server")
    print("=" * 70)
    print()
    print("📡 Server Address: http://localhost:11434")
    print("🤖 Mock Models Available:")
    print("   - llama3.2:3b (fast responses)")
    print("   - mixtral (complex analysis)")
    print("   - nomic-embed-text (embeddings)")
    print("   - llava (vision model)")
    print()
    print("⚠️  NOTE: This is a MOCK server for testing.")
    print("   Responses are simulated and not real AI.")
    print()
    print("=" * 70)
    print()

    uvicorn.run(app, host="0.0.0.0", port=11434, log_level="info")
