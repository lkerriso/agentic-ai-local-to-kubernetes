# Optional: MLflow Tracing

Add observability to your agent with MLflow tracing. This is **completely optional**—the agent works fine without it.

## What is MLflow Tracing?

MLflow tracing captures:
- **LLM calls**: Prompts, responses, tokens used
- **Tool invocations**: Which tools were called, with what parameters
- **Execution traces**: Full workflow execution timeline
- **Metadata**: Model used, temperature, latency

## Why Add Tracing?

**For development:**
- Debug tool calling behavior
- Optimize prompts
- Track token usage

**For production:**
- Monitor agent performance
- Detect quality regressions
- Track costs

## Setup: Local MLflow

### 1. Start MLflow Server

```bash
# In a separate terminal
cd /Users/lkerriso/demoenv/genagen/websearch-agent-demo
source .venv/bin/activate
uv run --extra tracing mlflow server --port 5000
```

**Output:**
```
[2026-06-24 10:00:00] INFO mlflow.server: Listening at: http://localhost:5000
```

Keep this running—it's your MLflow tracking server.

### 2. Enable Tracing in .env

```bash
# Uncomment these lines in .env
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=websearch-agent-local
MLFLOW_HTTP_REQUEST_TIMEOUT=2
MLFLOW_HTTP_REQUEST_MAX_RETRIES=0
```

### 3. Restart Agent

```bash
# The agent detects MLFLOW_TRACKING_URI and enables tracing
make run-app
```

**Output:**
```
[2026-06-24 10:01:00] [INFO] [Tracing] MLflow tracking enabled
[2026-06-24 10:01:00] [INFO] [Tracing] Experiment: websearch-agent-local
```

### 4. View Traces

Open MLflow UI: **http://localhost:5000**

1. Click **Experiments** → `websearch-agent-local`
2. Click on a run to see the trace
3. Explore:
   - Input/output messages
   - Tool calls
   - LLM responses
   - Timing breakdown

## Setup: Kubernetes/OpenShift MLflow

### 1. Find Your MLflow Endpoint

**On OpenShift:**
```bash
oc get routes -n mlflow-namespace
```

Or check with your cluster admin for the MLflow tracking URI.

### 2. Get Authentication Token

**OpenShift:**
```bash
oc whoami -t
```

Copy the token—you'll need it for MLFLOW_TRACKING_TOKEN.

### 3. Configure .env

```bash
# In deployment/.env.k8s.example (or ../.env)
MLFLOW_TRACKING_URI=https://mlflow.your-cluster.com
MLFLOW_TRACKING_TOKEN=sha256~abc123...
MLFLOW_EXPERIMENT_NAME=websearch-agent-production
MLFLOW_TRACKING_INSECURE_TLS=true
MLFLOW_WORKSPACE=your-namespace
```

### 4. Deploy with Tracing

```bash
cd deployment
make deploy
```

**The Helm chart automatically:**
- Injects `MLFLOW_TRACKING_URI` as env var
- Stores `MLFLOW_TRACKING_TOKEN` in Secret
- Configures experiment name and workspace

### 5. View Production Traces

Open your cluster's MLflow UI and navigate to:
- Experiment: `websearch-agent-production`
- Workspace: `your-namespace`

## How It Works

### Application Code (No Changes Needed!)

```python
# src/websearch_agent/tracing.py (already included)
import os
import mlflow

def setup_tracing():
    """Configure MLflow tracing if MLFLOW_TRACKING_URI is set."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    
    if not tracking_uri:
        print("[INFO] MLFLOW_TRACKING_URI not set. Tracing is disabled.")
        return
    
    # Health check
    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "default"))
        print("[INFO] MLflow tracking enabled")
    except Exception as e:
        print(f"[WARN] MLflow unreachable: {e}. Continuing without tracing.")

# Called at application startup
setup_tracing()
```

**Key points:**
- Gracefully degrades if MLflow is unreachable
- Application never crashes due to tracing failures
- Tracing is truly optional

### LlamaIndex Integration

LlamaIndex has built-in MLflow support:

```python
# src/websearch_agent/workflow.py
from llama_index.core.workflow import Workflow

# LlamaIndex automatically sends traces to MLflow
# No additional code needed!
```

When `MLFLOW_TRACKING_URI` is set, LlamaIndex auto-instruments:
- LLM calls
- Workflow steps
- Tool invocations

## What Gets Traced

### Example Trace

**User query:** "What is Kubernetes?"

```
Trace: websearch-agent-run-abc123
├── LLM Call (planning)
│   ├── Model: llama3.1:8b
│   ├── Input: [system prompt + user query]
│   ├── Output: "I need to search for Kubernetes information"
│   └── Duration: 1.2s
├── Tool: web_search
│   ├── Query: "Kubernetes container orchestration"
│   ├── Results: [5 search results]
│   └── Duration: 0.8s
└── LLM Call (final answer)
    ├── Model: llama3.1:8b
    ├── Input: [system + search results + user query]
    ├── Output: "Kubernetes is an open-source..."
    ├── Tokens: 1,234
    └── Duration: 2.1s

Total Duration: 4.1s
```

## Tracing Overhead

**Performance impact:**
- Local: ~50-100ms per request
- Kubernetes: ~100-200ms per request (network latency to MLflow)

**When to use:**
- ✅ Development: Always (helps debugging)
- ✅ Staging: Always (validate before production)
- ⚠️ Production: Selective (e.g., sample 10% of requests)

**Disable tracing for maximum performance:**
```bash
# Just comment out or remove MLFLOW_TRACKING_URI
# MLFLOW_TRACKING_URI=http://localhost:5000
```

## Troubleshooting

### MLflow server unreachable

**Symptom:**
```
[WARN] MLflow unreachable: Connection refused. Continuing without tracing.
```

**Solution:**
- Check MLflow server is running: `curl http://localhost:5000`
- Verify `MLFLOW_TRACKING_URI` is correct
- Check firewall rules (Kubernetes)

### No traces appearing

**Check:**
1. Is `MLFLOW_TRACKING_URI` set in .env?
2. Did you restart the agent after setting it?
3. Is the MLflow UI showing the correct experiment?

**Debug:**
```bash
# View agent logs
make logs  # Kubernetes
tail -f /path/to/local/logs  # Local

# Look for:
# [INFO] MLflow tracking enabled
# [INFO] Experiment: websearch-agent-local
```

### Kubernetes: Authentication failed

**Symptom:**
```
[ERROR] MLflow authentication failed: 401 Unauthorized
```

**Solution:**
- Verify `MLFLOW_TRACKING_TOKEN` is current: `oc whoami -t`
- Check token hasn't expired
- Ensure token is base64-encoded in Secret

## Advanced: Sampling

To trace only a subset of requests in production:

```python
# src/websearch_agent/tracing.py
import random

def should_trace():
    """Sample 10% of requests."""
    return random.random() < 0.1

# Conditional tracing
if should_trace():
    setup_tracing()
```

Or use environment-based sampling:

```env
# In .env
MLFLOW_TRACKING_SAMPLE_RATE=0.1  # 10%
```

## Cleaning Up

### Local

```bash
# Stop MLflow server
pkill -f "mlflow server"

# Remove experiment data (optional)
rm -rf mlruns/
```

### Kubernetes

```bash
# Disable tracing: comment out in .env
# MLFLOW_TRACKING_URI=...

# Redeploy
make deploy
```

## Resources

- [MLflow Tracing Docs](https://mlflow.org/docs/latest/llms/tracing/index.html)
- [LlamaIndex MLflow Integration](https://docs.llamaindex.ai/en/stable/examples/observability/mlflow/)

## Next Steps

- [Resources](06-resources.md) - More learning materials
- [What's Different](04-whats-different.md) - Compare local vs K8s
