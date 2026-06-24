# Agentic AI: From Local to Kubernetes

> Companion repository for the talk "Agentic AI: Going from Local to Kubernetes"

This repository demonstrates how to build an AI agent locally and deploy it to Kubernetes/OpenShift **without rewriting your application code**.

**Upstream Source:**
- Based on [agentic-starter-kits](https://github.com/redhat-et/agentic-starter-kits)
- Template: `agents/llamaindex/templates/websearch_agent`
- Adapted for teaching local→K8s progression

---

## What You'll Learn

- ✅ Build an AI agent with LlamaIndex + FastAPI
- ✅ Run it locally with Ollama + web UI
- ✅ Deploy to Kubernetes/OpenShift
- ✅ What stays the same (your code)
- ✅ What gets added (infrastructure)

---

## Quick Start

### Run Locally (5 minutes)
[→ Local Quickstart](docs/01-local-quickstart.md)

**TL;DR:**
```bash
cd local
make init && make env && make ollama
# Terminal 1: make ogx-server
# Terminal 2: make run-app
# Browser: http://localhost:8001
```

### Deploy to Kubernetes (10 minutes)
[→ Kubernetes Quickstart](docs/02-kubernetes-quickstart.md)

**TL;DR:**
```bash
cd deployment
make init  # Edit .env with your cluster details
make build && make push && make deploy
# Browser: <route-url>
```

---

## Repository Structure

```
.
├── main.py                  # FastAPI Application
├── src/websearch_agent/     # Agent code (LlamaIndex workflow)
├── playground/              # Web UI
├── local/                   # ← Local development
│   ├── Makefile
│   └── .env.local.example
├── deployment/              # ← Kubernetes deployment
│   ├── Dockerfile
│   ├── Makefile
│   ├── .env.k8s.example
│   └── templates/           # Helm chart
└── docs/                    # Detailed guides
```

---

## Key Insight

**The agent code (`main.py`, `src/`, `playground/`) is identical for both deployments.**

You're not rewriting your agent for production. You're adding operational infrastructure around it.

[See what's the same →](docs/03-whats-the-same.md)  
[See what's different →](docs/04-whats-different.md)

---

## Architecture

### Local Development
```
Developer Laptop
├── Ollama (localhost:11434)   ← Local LLM inference
├── OGX Server (port 8321)     ← RAG/embedding server
└── Agent (port 8001)          ← FastAPI + Web UI
    └── Web Search Tool
```

### Kubernetes/OpenShift
```
Internet
└── Route/Ingress (HTTPS + TLS)
    └── Service (ClusterIP)
        └── Pod: Agent Container
            ├── FastAPI + Web UI
            └── Remote LLM Endpoint
```

---

## Prerequisites

**Local:**
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- make
- Ollama (auto-installed by `make ollama`)

**Kubernetes:**
- Docker or Podman
- kubectl or oc (OpenShift CLI)
- Helm 3
- Access to a Kubernetes/OpenShift cluster

---

## Documentation

- [00 - Overview](docs/00-overview.md) - Architecture and concepts
- [01 - Local Quickstart](docs/01-local-quickstart.md) - Run locally in 5 minutes
- [02 - Kubernetes Quickstart](docs/02-kubernetes-quickstart.md) - Deploy to K8s in 10 minutes
- [03 - What's the Same](docs/03-whats-the-same.md) - Code that doesn't change
- [04 - What's Different](docs/04-whats-different.md) - Infrastructure additions
- [05 - Optional: MLflow](docs/05-optional-mlflow.md) - Observability (advanced)
- [06 - Resources](docs/06-resources.md) - Links and further reading

---

## Resources

- [Upstream: agentic-starter-kits](https://github.com/redhat-et/agentic-starter-kits)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Kubernetes Documentation](https://kubernetes.io/)
- [Helm Documentation](https://helm.sh/docs/)

---

## License

Apache 2.0 (matching upstream)
