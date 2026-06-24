SHELL          := bash
ROOT_DIR       := $(shell cd .. && pwd)
MODEL          ?= llama3.1:8b

.PHONY: init env ollama ogx-server run-app run-cli clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

init: ## Copy .env.local.example to .env
	@if [ ! -f $(ROOT_DIR)/.env ]; then \
	  cp .env.local.example $(ROOT_DIR)/.env && \
	  echo "Created .env from .env.local.example — edit it with your configuration"; \
	else \
	  echo ".env already exists — skipping"; \
	fi

env: ## Create venv and install dependencies
	@echo "==> Creating virtual environment and installing dependencies..." && \
	  cd $(ROOT_DIR) && rm -rf .venv && \
	  uv sync --python 3.12 && \
	  echo "" && \
	  echo "Done. Next steps:" && \
	  echo "  cd local && make ollama        # install Ollama and pull models" && \
	  echo "  cd local && make ogx-server    # start OGX server (in separate terminal)" && \
	  echo "  cd local && make run-app       # start agent app (in separate terminal)"

ollama: ## Install Ollama, start it, and pull models
	@cd $(ROOT_DIR) && source .venv/bin/activate && set -a && source .env && set +a && \
	if command -v ollama >/dev/null 2>&1; then \
	  echo "==> Ollama already installed, skipping..."; \
	else \
	  echo "==> Installing Ollama..." && \
	  curl -fsSL https://ollama.com/install.sh | sh; \
	fi && \
	  echo "==> Starting Ollama service..." && \
	  ollama serve &>/dev/null & \
	  OLLAMA_PID=$$! && \
	  echo "Waiting for Ollama to be ready (max 30s)..." && \
	  OLLAMA_WAIT=0 && \
	  until ollama list >/dev/null 2>&1; do \
	    OLLAMA_WAIT=$$((OLLAMA_WAIT + 1)); \
	    if [ $$OLLAMA_WAIT -ge 30 ]; then \
	      echo "ERROR: Ollama failed to start within 30 seconds." && \
	      kill $$OLLAMA_PID 2>/dev/null; \
	      exit 1; \
	    fi; \
	    sleep 1; \
	  done && \
	  echo "==> Pulling $(MODEL)..." && \
	  ollama pull $(MODEL) && \
	  echo "" && \
	  echo "Done. Run 'make ogx-server' in a separate terminal to start the OGX server."

ogx-server: ## Install OGX and start OGX server on port 8321
	@cd $(ROOT_DIR) && source .venv/bin/activate && set -a && source .env && set +a && \
	  echo "==> Installing OGX..." && \
	  uv pip install "ogx[starter]==1.1.0" "ogx-api==1.1.0" ollama "pymilvus==2.6.9" "milvus-lite>=2.5.1" "setuptools>=80.9.0,<82.0.0" && \
	  mkdir -p milvus_data && \
	  echo "==> Killing any existing process on port 8321..." && \
	  lsof -ti:8321 | xargs kill -9 2>/dev/null; true && \
	  echo "==> Starting OGX server on port 8321..." && \
	  echo "NOTE: Keep this terminal open - the server needs to keep running." && \
	  ogx run run_ogx_server.yaml

run-app: ## Run agent locally with web UI on port 8001 (requires OGX server)
	@cd $(ROOT_DIR) && source .venv/bin/activate && set -a && source .env && set +a && \
	  if lsof -ti:$${PORT:-8001} >/dev/null 2>&1; then \
	    echo "ERROR: Port $${PORT:-8001} is already in use." && \
	    echo "  Kill the process with: lsof -ti:$${PORT:-8001} | xargs kill -9" && \
	    exit 1; \
	  fi && \
	  echo "==> Starting agent app on http://localhost:$${PORT:-8001}" && \
	  echo "NOTE: Keep this terminal open - the app needs to keep running." && \
	  echo "Open browser to http://localhost:$${PORT:-8001} to use the web UI" && \
	  uv run $${MLFLOW_TRACKING_URI:+--extra tracing} uvicorn main:app --host 127.0.0.1 --port $${PORT:-8001} --reload --reload-exclude .venv

run-cli: ## Run interactive CLI chat (no web server)
	@cd $(ROOT_DIR)/examples && source ..//.venv/bin/activate && set -a && source ../.env && set +a && \
	  uv run $${MLFLOW_TRACKING_URI:+--extra tracing} python execute_ai_service_locally.py

clean: ## Remove .venv
	@cd $(ROOT_DIR) && rm -rf .venv && echo ".venv removed"
