SHELL          := bash
ROOT_DIR       := $(shell cd .. && pwd)
AGENT_NAME     := $(shell python3 -c "import re; print(re.search(r'^name:\s*(.+)', open('$(ROOT_DIR)/agent.yaml').read(), re.M).group(1).strip())")
CHART_DIR      := .
CONTAINER_CLI  := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)

.PHONY: init build push deploy dry-run undeploy logs help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

init: ## Copy .env.k8s.example to ../.env
	@if [ ! -f $(ROOT_DIR)/.env ]; then \
	  cp .env.k8s.example $(ROOT_DIR)/.env && \
	  echo "Created .env from .env.k8s.example — edit it with your configuration"; \
	  echo "Required: API_KEY, BASE_URL, MODEL_ID, CONTAINER_IMAGE"; \
	else \
	  echo ".env already exists — skipping"; \
	fi

build: ## Build container image locally (podman/docker)
	@[ -n "$(CONTAINER_CLI)" ] || { echo "ERROR: neither podman nor docker found in PATH"; exit 1; } && \
	  cd $(ROOT_DIR) && source .env && \
	  [ -n "$${CONTAINER_IMAGE}" ] || { echo "ERROR: CONTAINER_IMAGE is not set in .env"; exit 1; } && \
	  echo "==> Building container image: $${CONTAINER_IMAGE}" && \
	  $(CONTAINER_CLI) build --platform linux/amd64 -t "$${CONTAINER_IMAGE}" -f deployment/Dockerfile .

push: ## Push container image to registry
	@[ -n "$(CONTAINER_CLI)" ] || { echo "ERROR: neither podman nor docker found in PATH"; exit 1; } && \
	  cd $(ROOT_DIR) && source .env && \
	  [ -n "$${CONTAINER_IMAGE}" ] || { echo "ERROR: CONTAINER_IMAGE is not set in .env"; exit 1; } && \
	  echo "==> Pushing container image: $${CONTAINER_IMAGE}" && \
	  $(CONTAINER_CLI) push "$${CONTAINER_IMAGE}"

_check-env:
	@cd $(ROOT_DIR) && set -a && source .env 2>/dev/null && set +a; \
	  missing=""; \
	  for var in API_KEY BASE_URL MODEL_ID CONTAINER_IMAGE; do \
	    eval val="\$$$$var"; \
	    [ -n "$$val" ] || missing="$$missing $$var"; \
	  done; \
	  [ -z "$$missing" ] || { echo "ERROR: Missing required env vars:$$missing"; exit 1; }

deploy: _check-env ## Deploy to OpenShift/K8s via Helm
	@cd $(ROOT_DIR) && source .env && \
	  LAST_SEG="$${CONTAINER_IMAGE##*/}" && \
	  if [[ "$$LAST_SEG" == *:* ]]; then \
	    IMAGE_REPO="$${CONTAINER_IMAGE%:*}"; \
	    IMAGE_TAG="$${LAST_SEG##*:}"; \
	  else \
	    IMAGE_REPO="$${CONTAINER_IMAGE}"; \
	    IMAGE_TAG="latest"; \
	  fi && \
	  trap 'rm -f deployment/.helm-secrets.yaml' EXIT && \
	  umask 077 && \
	  { printf 'secrets:\n  apiKey: "%s"\n' "$${API_KEY}"; \
	    [ -z "$${MLFLOW_TRACKING_TOKEN}" ] || printf '  mlflowTrackingToken: "%s"\n' "$${MLFLOW_TRACKING_TOKEN}"; \
	  } > deployment/.helm-secrets.yaml && \
	  echo "==> Deploying $(AGENT_NAME) to cluster..." && \
	  helm upgrade --install $(AGENT_NAME) deployment/ \
	    -f deployment/values.yaml \
	    -f deployment/.helm-secrets.yaml \
	    --set image.repository="$${IMAGE_REPO}" \
	    --set image.tag="$${IMAGE_TAG}" \
	    --set env.BASE_URL="$${BASE_URL}" \
	    --set env.MODEL_ID="$${MODEL_ID}" \
	    $${MLFLOW_TRACKING_URI:+--set env.MLFLOW_TRACKING_URI="$${MLFLOW_TRACKING_URI}"} \
	    $${MLFLOW_EXPERIMENT_NAME:+--set env.MLFLOW_EXPERIMENT_NAME="$${MLFLOW_EXPERIMENT_NAME}"} \
	    $${MLFLOW_TRACKING_INSECURE_TLS:+--set env.MLFLOW_TRACKING_INSECURE_TLS="$${MLFLOW_TRACKING_INSECURE_TLS}"} \
	    $${MLFLOW_WORKSPACE:+--set env.MLFLOW_WORKSPACE="$${MLFLOW_WORKSPACE}"} && \
	  if command -v oc >/dev/null 2>&1; then \
	    echo "" && echo "Waiting for rollout to complete..." && \
	    if oc rollout status deployment/$(AGENT_NAME) --timeout=120s 2>/dev/null; then \
	      ROUTE=$$(oc get route $(AGENT_NAME) -o jsonpath='{.spec.host}' 2>/dev/null || true); \
	      if [ -n "$$ROUTE" ]; then \
	        echo "" && echo "=============================================="; \
	        echo "Agent is available at: https://$$ROUTE"; \
	        echo "=============================================="; \
	      fi; \
	    else \
	      echo "" && echo "WARNING: Rollout did not complete successfully. Check pod status."; \
	    fi; \
	  elif command -v kubectl >/dev/null 2>&1; then \
	    echo "" && echo "Waiting for rollout to complete..." && \
	    kubectl rollout status deployment/$(AGENT_NAME) --timeout=120s || true; \
	  fi

dry-run: _check-env ## Render Helm templates without deploying
	@cd $(ROOT_DIR) && source .env && \
	  LAST_SEG="$${CONTAINER_IMAGE##*/}" && \
	  if [[ "$$LAST_SEG" == *:* ]]; then \
	    IMAGE_REPO="$${CONTAINER_IMAGE%:*}"; \
	    IMAGE_TAG="$${LAST_SEG##*:}"; \
	  else \
	    IMAGE_REPO="$${CONTAINER_IMAGE}"; \
	    IMAGE_TAG="latest"; \
	  fi && \
	  helm template $(AGENT_NAME) deployment/ \
	    -f deployment/values.yaml \
	    --set secrets.apiKey="REDACTED" \
	    --set image.repository="$${IMAGE_REPO}" \
	    --set image.tag="$${IMAGE_TAG}" \
	    --set env.BASE_URL="$${BASE_URL}" \
	    --set env.MODEL_ID="$${MODEL_ID}" \
	    $${MLFLOW_TRACKING_URI:+--set env.MLFLOW_TRACKING_URI="$${MLFLOW_TRACKING_URI}"} \
	    $${MLFLOW_TRACKING_TOKEN:+--set secrets.mlflowTrackingToken="REDACTED"} \
	    $${MLFLOW_EXPERIMENT_NAME:+--set env.MLFLOW_EXPERIMENT_NAME="$${MLFLOW_EXPERIMENT_NAME}"} \
	    $${MLFLOW_TRACKING_INSECURE_TLS:+--set env.MLFLOW_TRACKING_INSECURE_TLS="$${MLFLOW_TRACKING_INSECURE_TLS}"} \
	    $${MLFLOW_WORKSPACE:+--set env.MLFLOW_WORKSPACE="$${MLFLOW_WORKSPACE}"}

undeploy: ## Remove deployment from cluster
	@echo "==> Removing $(AGENT_NAME) from cluster..." && \
	  helm uninstall $(AGENT_NAME)

logs: ## View pod logs
	@if command -v oc >/dev/null 2>&1; then \
	  oc logs deployment/$(AGENT_NAME) -f; \
	elif command -v kubectl >/dev/null 2>&1; then \
	  kubectl logs deployment/$(AGENT_NAME) -f; \
	else \
	  echo "ERROR: neither oc nor kubectl found in PATH"; \
	  exit 1; \
	fi
