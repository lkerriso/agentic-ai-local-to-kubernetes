# Local Quickstart

Get the agent running locally in **5 minutes**.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- make
- Ollama (will be installed automatically if missing)

## Installation

### 1. Setup Environment

```bash
cd local
make init   # Creates .env from template
make env    # Creates .venv, installs dependencies (~30 seconds)
```

**What this does:**
- Creates `.env` with local defaults (port 8001, Ollama endpoint)
- Installs 102 Python packages via `uv` (FastAPI, LlamaIndex, OpenAI SDK)

### 2. Install Ollama and Pull Models

```bash
make ollama   # Installs Ollama, pulls llama3.1:8b (~5GB download)
```

**What this does:**
- Installs Ollama if not already installed
- Starts Ollama service
- Pulls the `llama3.1:8b` model

**Already have Ollama?** Skip this step—`make ollama` detects existing installations.

## Running the Agent

You'll need **two terminals**:

### Terminal 1: Start OGX Server

```bash
make ogx-server
```

**Output:**
```
==> Installing OGX...
==> Starting OGX server on port 8321...
NOTE: Keep this terminal open - the server needs to keep running.
```

**What this is:**
OGX is a RAG/embedding orchestration server that sits between your agent and Ollama.

### Terminal 2: Start Agent App

```bash
make run-app
```

**Output:**
```
==> Starting agent app on http://localhost:8001
NOTE: Keep this terminal open - the app needs to keep running.
Open browser to http://localhost:8001 to use the web UI

INFO:     Uvicorn running on http://127.0.0.1:8001
```

## Using the Agent

### Option 1: Web UI (Recommended)

Open your browser to: **http://localhost:8001**

1. Type a question in the chat box (e.g., "What is Red Hat OpenShift?")
2. Click Send or press Enter
3. Watch the agent use the web search tool and generate a response

### Option 2: API (curl)

```bash
# Health check
curl http://localhost:8001/health

# Chat completion
curl -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Kubernetes?"}
    ],
    "stream": false
  }'
```

### Option 3: Interactive CLI

```bash
make run-cli
```

Text-based chat interface without the web UI.

## What's Running

| Service | Port | Purpose |
|---------|------|---------|
| Ollama | 11434 | Local LLM inference |
| OGX Server | 8321 | RAG/embedding orchestration |
| Agent App | 8001 | FastAPI server + Web UI |

## Configuration

The `.env` file configures the agent:

```env
# API Configuration (local Ollama)
API_KEY=not-needed-for-local-development
BASE_URL=http://localhost:11434/v1
MODEL_ID=llama3.1:8b

# Server Configuration
PORT=8001
```

**To use a different model:**
```bash
# In .env, change:
MODEL_ID=llama3.2:3b
# Then restart the agent
```

## Troubleshooting

### Port already in use

```bash
# Kill existing process on port 8001
lsof -ti:8001 | xargs kill -9

# Or change the port in .env
PORT=8002
```

### Ollama not starting

```bash
# Check if Ollama is running
ollama list

# Start manually
ollama serve &
```

### Dependencies not installing

```bash
# Clean and rebuild
make clean
make env
```

## Clean Up

When you're done:

```bash
# Stop servers (Ctrl+C in each terminal)
# Or kill processes:
lsof -ti:8001 | xargs kill -9  # Agent
lsof -ti:8321 | xargs kill -9  # OGX

# Remove virtual environment
make clean
```

## Next Steps

- **Deploy to Kubernetes:** [Kubernetes Quickstart](02-kubernetes-quickstart.md)
- **Understand the architecture:** [Overview](00-overview.md)
- **See what changes for K8s:** [What's Different](04-whats-different.md)
