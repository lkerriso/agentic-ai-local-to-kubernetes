# Overview: Agentic AI from Local to Kubernetes

## What This Repository Demonstrates

This repository shows how to build an AI agent locally and deploy it to Kubernetes/OpenShift **without rewriting your application code**. The same Python code that runs on your laptop runs in production—you just add operational infrastructure around it.

## The Agent

This is a **web search agent** built with:
- **LlamaIndex** - Agentic framework
- **FastAPI** - OpenAI-compatible API server
- **Web UI** - Interactive playground for testing
- **Tool calling** - Uses web search to answer questions

## Architecture

### Local Development

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Your Browser                                   │
│  localhost:8001                                 │
│                                                 │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────────────────┐
│  Runtime Environment                            │
│  ┌───────────────────────────────────────────┐ │
│  │  Agent Process                            │ │
│  │  (same code local & in-cluster)           │ │
│  │                                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  FastAPI Application                │ │ │
│  │  │  (main.py)                          │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  │               │                           │ │
│  │               ▼                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  LlamaIndex Workflow                │ │ │
│  │  │  (workflow.py)                      │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  │               │                           │ │
│  │               ▼                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  OpenAIlike Client                  │ │ │
│  │  │  (agent.py)                         │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  └───────────────┼───────────────────────────┘ │
└──────────────────┼─────────────────────────────┘
                   │ Configuration (.env)
                   ▼
┌─────────────────────────────────────────────────┐
│  LLM                                            │
│  ┌───────────────────────────────────────────┐ │
│  │  LLM Inference Provider                   │ │
│  │  Ollama (localhost:11434)                 │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Kubernetes/OpenShift

```
┌─────────────────────────────────────────────────┐
│  Internet                                       │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────┐
│  Route/Ingress (TLS edge termination)           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Service (ClusterIP)                            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Pod: Agent Container                           │
│  ┌───────────────────────────────────────────┐ │
│  │  Agent Process                            │ │
│  │  (same code local & in-cluster)           │ │
│  │                                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  FastAPI Application                │ │ │
│  │  │  (main.py)                          │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  │               │                           │ │
│  │               ▼                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  LlamaIndex Workflow                │ │ │
│  │  │  (workflow.py)                      │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  │               │                           │ │
│  │               ▼                           │ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │  OpenAIlike Client                  │ │ │
│  │  │  (agent.py)                         │ │ │
│  │  └────────────┬────────────────────────┘ │ │
│  └───────────────┼───────────────────────────┘ │
└──────────────────┼─────────────────────────────┘
                   │ Configuration (K8s Secret)
                   ▼
┌─────────────────────────────────────────────────┐
│  LLM                                            │
│  ┌───────────────────────────────────────────┐ │
│  │  LLM Inference Provider                   │ │
│  │  Remote endpoint (HTTPS)                  │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Key Files (Same in Both Environments)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with OpenAI-compatible `/chat/completions` endpoint |
| `src/websearch_agent/agent.py` | OpenAIlike client initialization |
| `src/websearch_agent/workflow.py` | LlamaIndex FunctionCallingAgent workflow |
| `src/websearch_agent/tools.py` | Web search tool definition |
| `playground/` | Web UI for interactive testing |

**These files are identical in local and Kubernetes deployments.**

## What Changes Between Environments

| Aspect | Local | Kubernetes |
|--------|-------|------------|
| **Runtime** | Python venv | Container (UBI9 + Python) |
| **Port** | 8001 | 8080 (internal), HTTPS (external) |
| **LLM Backend** | Ollama (localhost:11434) | Remote endpoint (HTTPS) |
| **Configuration** | `.env` file | Kubernetes Secret |
| **Networking** | localhost | Service + Route/Ingress + TLS |
| **Security** | None | Non-root container, dropped capabilities |
| **Health Checks** | None | Liveness + Readiness probes |
| **Scaling** | Manual restart | `kubectl scale` or HPA |

## Core Concepts

### 1. Same Code, Different Runtime

Your agent code doesn't know or care where it's running. It reads environment variables and makes HTTP calls—whether those come from a `.env` file or a Kubernetes Secret doesn't matter to your Python code.

### 2. Configuration is Key

The only difference between environments is **configuration**:
- Local: Points to Ollama on localhost
- Kubernetes: Points to a remote LLM endpoint

### 3. Infrastructure is Additive

You don't rewrite your agent for production. You **add** infrastructure:
- Dockerfile (packaging)
- Helm chart (deployment)
- Health probes (reliability)
- TLS termination (security)

### 4. Progressive Enhancement

Start simple locally, add production features as needed:
1. **Local development**: Ollama + Python venv
2. **Containerization**: Add Dockerfile
3. **Kubernetes deployment**: Add Helm chart
4. **Observability**: Add MLflow tracing (optional)
5. **Scaling**: Add HPA, resource limits

## Next Steps

- [Local Quickstart](01-local-quickstart.md) - Run the agent in 5 minutes
- [Kubernetes Quickstart](02-kubernetes-quickstart.md) - Deploy to K8s in 10 minutes
- [What's the Same](03-whats-the-same.md) - Code that doesn't change
- [What's Different](04-whats-different.md) - Infrastructure additions
