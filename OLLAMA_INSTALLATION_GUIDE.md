# How to Install and Configure Real Ollama for B3 Personal Assistant

## Current Status

**Network Restriction Detected**: The environment has limited external network access, preventing direct download of Ollama binaries from ollama.ai and GitHub.

**Current Setup**: Using Mock Ollama Server (fully functional for testing)

---

## Option 1: Install Ollama When Network Access Available

### Quick Install (Recommended)

When you have full network access, run:

```bash
# Stop the mock Ollama server first
pkill -f mock_ollama_server

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve
```

### Manual Installation

If the install script doesn't work:

```bash
# Download binary directly (Linux AMD64)
curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama
chmod +x /usr/local/bin/ollama

# Verify installation
ollama --version

# Start the service
ollama serve
```

### Docker Installation (Alternative)

```bash
# Pull Ollama Docker image
docker pull ollama/ollama:latest

# Run Ollama in Docker
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# Test connection
curl http://localhost:11434/api/tags
```

---

## Option 2: Pull Required AI Models

After installing Ollama, pull the models B3 uses:

### Essential Models

```bash
# Fast model for quick responses (recommended first)
ollama pull llama3.2:3b
# Download size: ~2 GB

# Alternative: Larger, more capable model
ollama pull llama3.2
# Download size: ~4.7 GB

# Complex analysis model (optional)
ollama pull mixtral
# Download size: ~26 GB

# Embeddings model for semantic search
ollama pull nomic-embed-text
# Download size: ~274 MB

# Vision model for image processing (optional)
ollama pull llava
# Download size: ~4.5 GB
```

### Recommended Minimal Setup

For basic functionality, you only need:

```bash
ollama pull llama3.2:3b      # Main chat model
ollama pull nomic-embed-text  # For semantic search
```

Total download: ~2.3 GB

### Verify Models

```bash
# List installed models
ollama list

# Test a model
ollama run llama3.2:3b "Hello! Can you help me?"
```

---

## Option 3: Configure B3 to Use Real Ollama

### Step 1: Stop Mock Server

```bash
# Find and kill the mock Ollama process
pkill -f mock_ollama_server

# Verify it's stopped
curl http://localhost:11434/api/tags
# Should fail or return different response
```

### Step 2: Start Real Ollama

```bash
# Start Ollama service (will run on port 11434)
ollama serve

# Or if using systemd:
sudo systemctl start ollama
sudo systemctl enable ollama  # Auto-start on boot
```

### Step 3: Verify Connection

```bash
# Check Ollama is responding
curl http://localhost:11434/api/tags

# Should show real models like:
# {"models":[{"name":"llama3.2:3b",...}]}
```

### Step 4: Restart B3 Server

```bash
# The B3 server will automatically detect real Ollama
# No code changes needed!

# Restart B3 (if needed)
pkill -f "uvicorn.*main:app"
cd /home/user/b3personalassistant
nohup python -m uvicorn interfaces.web_api.main:app --host 0.0.0.0 --port 8000 &
```

### Step 5: Test Integration

```bash
# Test chat with real AI
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain quantum computing in simple terms","include_context":false}'

# You should get real AI-generated responses now!
```

---

## Option 4: Use Mock Ollama (Current Setup)

### Advantages of Mock Ollama

✅ **No downloads required** - Works in restricted environments
✅ **Instant responses** - No model loading time
✅ **Fully compatible** - Same API as real Ollama
✅ **Good for testing** - UI, database, WebSocket functionality
✅ **Resource efficient** - No GPU/RAM requirements

### Limitations

❌ Simulated responses - Not real AI reasoning
❌ Generic answers - Can't do complex analysis
❌ No learning - Responses are template-based

### When to Use Mock

- Development and testing
- Network-restricted environments
- Resource-constrained systems
- UI/UX testing
- Integration testing

### Mock Server Details

**File**: `mock_ollama_server.py`
**Port**: 11434
**Models**: llama3.2:3b, mixtral, nomic-embed-text, llava
**Status**: ✅ Currently running

**To restart mock server**:
```bash
pkill -f mock_ollama_server
nohup python /home/user/b3personalassistant/mock_ollama_server.py >> /tmp/ollama_mock.log 2>&1 &
```

---

## Comparison: Real vs Mock Ollama

| Feature | Real Ollama | Mock Ollama |
|---------|-------------|-------------|
| **AI Quality** | ✅ Real reasoning | ❌ Simulated |
| **Response Time** | 2-10 seconds | <0.5 seconds |
| **Download Size** | 2+ GB | 0 GB |
| **RAM Usage** | 4-16 GB | <100 MB |
| **GPU Support** | ✅ Yes | ❌ No |
| **Offline Work** | ✅ Yes | ✅ Yes |
| **API Compatible** | ✅ Official | ✅ Compatible |
| **Complex Tasks** | ✅ Excellent | ❌ Limited |
| **Best For** | Production | Testing |

---

## Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
ps aux | grep ollama

# Check Ollama logs
journalctl -u ollama -f

# Check port availability
netstat -tulpn | grep 11434
```

### Port Already in Use

```bash
# Find what's using port 11434
lsof -i :11434

# Kill mock server
pkill -f mock_ollama_server

# Or use different port for Ollama
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

### Model Download Fails

```bash
# Check disk space
df -h

# Check internet connection
curl -I https://ollama.ai

# Try pulling smaller model first
ollama pull llama3.2:1b  # Only 1.3 GB
```

### B3 Can't Connect to Ollama

```bash
# Check .env configuration
cat /home/user/b3personalassistant/.env | grep OLLAMA

# Should show:
# OLLAMA_HOST=http://localhost:11434

# Test Ollama directly
curl http://localhost:11434/api/tags

# Test B3 health endpoint
curl http://localhost:8000/health
```

---

## Environment Variables

Add to `/home/user/b3personalassistant/.env`:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_NUM_PARALLEL=1          # Number of parallel requests
OLLAMA_MAX_LOADED_MODELS=1     # Keep 1 model in memory
OLLAMA_KEEP_ALIVE=5m           # Keep model loaded for 5 minutes

# Model Selection
B3_PRIMARY_MODEL=llama3.2:3b   # Fast responses
B3_COMPLEX_MODEL=mixtral       # Deep analysis
B3_EMBED_MODEL=nomic-embed-text # Embeddings
```

---

## Performance Tuning

### For Limited Resources

```bash
# Use smallest model
ollama pull llama3.2:1b

# Limit memory usage
OLLAMA_MAX_VRAM=4GB ollama serve

# Unload model after use
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:3b","keep_alive":0}'
```

### For Best Performance

```bash
# Use GPU acceleration (if available)
OLLAMA_GPU_LAYERS=999 ollama serve

# Keep model loaded
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:3b","keep_alive":-1}'

# Use faster model
ollama pull llama3.2:3b  # Faster than llama3.2
```

---

## Quick Reference

### Essential Commands

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start service
ollama serve

# Pull model
ollama pull llama3.2:3b

# Test model
ollama run llama3.2:3b "Hello!"

# List models
ollama list

# Remove model
ollama rm llama3.2:3b

# Check status
curl http://localhost:11434/api/tags
```

### B3 Integration Commands

```bash
# Stop mock Ollama
pkill -f mock_ollama_server

# Start real Ollama
ollama serve &

# Restart B3
pkill -f "uvicorn.*main:app"
cd /home/user/b3personalassistant
python -m uvicorn interfaces.web_api.main:app --host 0.0.0.0 --port 8000 &

# Test integration
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message"}'
```

---

## Next Steps

1. **With Network Access**:
   - Run: `curl -fsSL https://ollama.com/install.sh | sh`
   - Pull: `ollama pull llama3.2:3b`
   - Start: `ollama serve`

2. **Without Network Access**:
   - Continue using mock Ollama
   - All B3 features work except real AI
   - Perfect for development and testing

3. **Switching Later**:
   - Stop mock server
   - Start real Ollama
   - B3 automatically detects and uses real Ollama
   - No code changes required!

---

**Current Status**: Mock Ollama running and functional ✅

The system is ready for testing. When network access is available, follow the steps above to switch to real Ollama for production-quality AI responses.
