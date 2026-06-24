# Local Development

This directory contains everything needed to run the agent locally.

## Quick Start

```bash
make init      # Create .env
make env       # Install dependencies
make ollama    # Install Ollama + pull models

# Terminal 1:
make ogx-server

# Terminal 2:
make run-app

# Browser:
open http://localhost:8001
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make help` | Show all available targets |
| `make init` | Create `.env` from template |
| `make env` | Create venv, install dependencies |
| `make ollama` | Install Ollama, pull models |
| `make ogx-server` | Start OGX server (port 8321) |
| `make run-app` | Start agent app (port 8001) |
| `make run-cli` | Interactive CLI mode |
| `make clean` | Remove .venv |

## Configuration

The `.env` file (created by `make init`) configures the agent:

```env
API_KEY=not-needed-for-local-development
BASE_URL=http://localhost:11434/v1
MODEL_ID=llama3.1:8b
PORT=8001
```

## Full Documentation

See [Local Quickstart](../docs/01-local-quickstart.md) for detailed instructions.
