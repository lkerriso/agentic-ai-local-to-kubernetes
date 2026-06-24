# What's the Same

The core value proposition: **Your agent code is identical in both local and Kubernetes deployments.**

## Unchanged Files

These files are exactly the same whether running locally or on Kubernetes:

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `main.py` | FastAPI application with OpenAI-compatible API | 540 |
| `src/websearch_agent/agent.py` | Agent factory, OpenAIlike client setup | 45 |
| `src/websearch_agent/workflow.py` | LlamaIndex FunctionCallingAgent workflow | 85 |
| `src/websearch_agent/tools.py` | Web search tool definition | 35 |
| `src/websearch_agent/tracing.py` | MLflow integration (optional) | 40 |
| `playground/` | Web UI (Flask app + HTML/CSS/JS) | 250 |
| `pyproject.toml` | Python dependencies | 30 |

**Total: ~1,025 lines of application code that never changes.**

## Side-by-Side: main.py

### Local Environment
```python
# main.py (same file in both environments)
from fastapi import FastAPI
from src.websearch_agent.agent import get_workflow_closure
import os

app = FastAPI()
workflow = get_workflow_closure()

@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    # ... implementation ...
    pass

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_initialized": True}
```

### Kubernetes Environment
```python
# main.py (IDENTICAL file - no changes!)
from fastapi import FastAPI
from src.websearch_agent.agent import get_workflow_closure
import os

app = FastAPI()
workflow = get_workflow_closure()

@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    # ... implementation ...
    pass

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_initialized": True}
```

**Result: Zero changes needed.**

## Side-by-Side: agent.py

### Local Configuration Reading
```python
# src/websearch_agent/agent.py
import os

def get_workflow_closure():
    api_key = os.getenv("API_KEY")           # Reads from .env file
    base_url = os.getenv("BASE_URL")         # http://localhost:11434/v1
    model_id = os.getenv("MODEL_ID")         # llama3.1:8b
    
    # Local detection: skip API key validation for localhost
    is_local = any(host in base_url for host in ["localhost", "127.0.0.1"])
    if not is_local and not api_key:
        raise ValueError("API_KEY is required")
    
    # ... rest of setup ...
```

### Kubernetes Configuration Reading
```python
# src/websearch_agent/agent.py (SAME FILE!)
import os

def get_workflow_closure():
    api_key = os.getenv("API_KEY")           # Reads from K8s Secret
    base_url = os.getenv("BASE_URL")         # https://llm-endpoint.com/v1
    model_id = os.getenv("MODEL_ID")         # Qwen3.6-35B-A3B
    
    # Local detection: skip API key validation for localhost
    is_local = any(host in base_url for host in ["localhost", "127.0.0.1"])
    if not is_local and not api_key:
        raise ValueError("API_KEY is required")
    
    # ... rest of setup ...
```

**Result: Same code adapts automatically based on BASE_URL.**

## Web UI: Identical in Both Environments

The `playground/` directory contains a complete web UI that works in both environments:

```
playground/
├── app.py                  # Flask server for serving static files
├── templates/
│   └── index.html         # Chat interface
```

### Local: http://localhost:8001
![Web UI running locally]

### Kubernetes: https://route-url
![Same web UI running on Kubernetes]

**Result: Same HTML, CSS, JavaScript in both environments.**

## Dependencies: pyproject.toml

```toml
# pyproject.toml (same file everywhere)
[project]
name = "websearch-agent"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.136.0",
    "uvicorn>=0.46.0",
    "llama-index>=0.14.21",
    "llama-index-llms-openai-like>=0.7.2",
    "openai>=2.36.0",
    "python-dotenv>=1.2.2",
    # ... more dependencies ...
]

[project.optional-dependencies]
tracing = [
    "mlflow-tracing>=3.14.0",
]
```

**Local:** `uv sync` installs these dependencies  
**Kubernetes:** Dockerfile runs `uv pip install` with same dependencies

**Result: Identical Python environment.**

## What Enables This?

### 1. Environment Variables

Both environments use environment variables for configuration:

**Local (`.env` file):**
```env
API_KEY=not-needed-for-local-development
BASE_URL=http://localhost:11434/v1
MODEL_ID=llama3.1:8b
PORT=8001
```

**Kubernetes (Secret + Deployment):**
```yaml
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: websearch-agent-secret
        key: api-key
  - name: BASE_URL
    value: "https://llm-endpoint.com/v1"
  - name: MODEL_ID
    value: "Qwen3.6-35B-A3B"
  - name: PORT
    value: "8080"
```

Your Python code just calls `os.getenv("API_KEY")` in both cases.

### 2. OpenAI-Compatible API

The LlamaIndex OpenAIlike client works with any OpenAI-compatible endpoint:

```python
from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model=model_id,           # Works with Ollama, LiteLLM, OpenAI, etc.
    api_base=base_url,        # Configurable endpoint
    api_key=api_key,          # Optional for localhost
)
```

Works with:
- **Local:** Ollama (localhost:11434)
- **Kubernetes:** Any OpenAI-compatible API (LiteLLM, vLLM, OpenAI, etc.)

### 3. Port Flexibility

The app reads the port from an environment variable:

```python
# main.py
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Local:** PORT=8001 (from `.env`)  
**Kubernetes:** PORT=8080 (from Deployment)

### 4. Static File Serving

The web UI uses relative paths that work anywhere:

```html
<!-- playground/templates/index.html -->
<script>
    // Submits to the same host/port serving this HTML
    fetch('/chat/completions', {
        method: 'POST',
        // ...
    })
</script>
```

**Local:** Fetches from `http://localhost:8001/chat/completions`  
**Kubernetes:** Fetches from `https://route-url/chat/completions`

## Key Insight

**You write your agent once. The code doesn't know or care if it's running on your laptop or in a Kubernetes pod.**

The only thing that changes is **how** the environment variables get set:
- Local: `.env` file
- Kubernetes: ConfigMap and Secret resources

## Verification

Want to prove the code is identical?

```bash
# Compare main.py from local vs what's in the container
docker run --rm --entrypoint cat \
    quay.io/lkerriso/websearch-agent-demo:latest \
    /opt/app-root/src/main.py > /tmp/k8s-main.py

diff main.py /tmp/k8s-main.py
# Output: (nothing - files are identical)
```

## Benefits

1. **No code duplication** - One codebase to maintain
2. **Consistent behavior** - Same logic in dev and prod
3. **Easy testing** - Test locally, deploy with confidence
4. **Fast iteration** - Change code once, works everywhere
5. **No "works on my machine"** - Same container everywhere

## Next Steps

- [What's Different](04-whats-different.md) - Infrastructure that gets added for Kubernetes
- [Overview](00-overview.md) - Architecture diagrams
