# Kubernetes Quickstart

Deploy the agent to Kubernetes/OpenShift in **10 minutes**.

## Prerequisites

- **Container tool:** Docker or Podman
- **Cluster access:** kubectl or oc (OpenShift CLI)
- **Helm:** Helm 3
- **Cluster:** Access to a Kubernetes or OpenShift cluster
- **LLM endpoint:** A remote LLM API endpoint (e.g., OpenShift AI, LiteLLM, OpenAI)

## Configuration

### 1. Initialize Configuration

```bash
cd deployment
make init
```

This creates `.env` from the template. You'll need to edit it with your cluster details.

### 2. Edit `.env`

```bash
# Open .env in your editor
vim ../.env  # or code ../.env
```

**Required values:**

```env
# API Configuration (remote LLM endpoint)
API_KEY=your-api-key-here
BASE_URL=https://your-llm-endpoint.com/v1
MODEL_ID=llama-3.1-8b-instruct

# Container Image
CONTAINER_IMAGE=quay.io/your-username/websearch-agent-demo:latest
```

**Example (OpenShift AI):**
```env
API_KEY=sk-abc123...
BASE_URL=https://litellm-litemaas.apps.prod.rhoai.rh-aiservices-bu.com/v1
MODEL_ID=Qwen3.6-35B-A3B
CONTAINER_IMAGE=quay.io/lkerriso/websearch-agent-demo:latest
```

**Example (OpenAI):**
```env
API_KEY=sk-proj-...
BASE_URL=https://api.openai.com/v1
MODEL_ID=gpt-4o
CONTAINER_IMAGE=quay.io/your-username/websearch-agent-demo:latest
```

## Build and Deploy

### Step 1: Build Container Image

```bash
make build
```

**Output:**
```
==> Building container image: quay.io/lkerriso/websearch-agent-demo:latest
STEP 1/16: FROM registry.access.redhat.com/ubi9/python-312...
...
Successfully tagged quay.io/lkerriso/websearch-agent-demo:latest
```

**What this does:**
- Builds a container image from the Dockerfile
- Packages: main.py, src/, playground/, images/
- Base image: Red Hat UBI9 with Python 3.12
- Non-root user (UID 1001)
- Build time: ~30 seconds

### Step 2: Push to Registry

```bash
# Login to your container registry first
podman login quay.io  # or docker login quay.io

# Push the image
make push
```

**Output:**
```
==> Pushing container image: quay.io/lkerriso/websearch-agent-demo:latest
Getting image source signatures
Copying blob...
Writing manifest to image destination
```

### Step 3: Deploy to Cluster

```bash
make deploy
```

**Output:**
```
==> Deploying llamaindex-websearch-agent to cluster...
Release "llamaindex-websearch-agent" does not exist. Installing it now.
NAME: llamaindex-websearch-agent
NAMESPACE: your-namespace
STATUS: deployed

Waiting for rollout to complete...
deployment "llamaindex-websearch-agent" successfully rolled out

==============================================
Agent is available at: https://llamaindex-websearch-agent-your-namespace.apps.cluster.example.com
==============================================
```

**What this does:**
- Installs Helm chart with your configuration
- Creates: Deployment, Service, Secret, Route/Ingress
- Waits for pod to be ready
- Prints the agent URL

## Verify Deployment

### 1. Check Pod Status

```bash
# Using kubectl
kubectl get pods

# Using oc (OpenShift)
oc get pods
```

**Expected output:**
```
NAME                                          READY   STATUS    RESTARTS   AGE
llamaindex-websearch-agent-7d8f9b8c6d-abc12   1/1     Running   0          2m
```

### 2. Check Logs

```bash
make logs
```

**Expected output:**
```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 3. Test Health Endpoint

Get your route URL from the deploy output, then:

```bash
# OpenShift
export ROUTE_URL=$(oc get route llamaindex-websearch-agent -o jsonpath='{.spec.host}')
curl https://$ROUTE_URL/health

# Expected response:
# {"status":"healthy","agent_initialized":true}
```

## Using the Deployed Agent

### Option 1: Web UI (Recommended)

Open your browser to the route URL (from the deploy output):

```
https://llamaindex-websearch-agent-your-namespace.apps.cluster.example.com
```

The same web UI from local development now runs on Kubernetes!

### Option 2: API

```bash
export ROUTE_URL=$(oc get route llamaindex-websearch-agent -o jsonpath='{.spec.host}')

# Chat completion
curl -X POST https://$ROUTE_URL/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Kubernetes?"}
    ],
    "stream": false
  }'
```

## Preview Before Deploying

Want to see what will be deployed first?

```bash
make dry-run
```

This renders the Helm templates without actually deploying them.

## Updating the Deployment

Made changes to your code? Rebuild and redeploy:

```bash
make build    # Build new image
make push     # Push to registry
make deploy   # Update deployment (Helm upgrade)
```

## Scaling

### Manual Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment llamaindex-websearch-agent --replicas=3

# Or with oc
oc scale deployment llamaindex-websearch-agent --replicas=3
```

### Edit Helm Values

In `deployment/values.yaml`:

```yaml
replicaCount: 3
```

Then redeploy:
```bash
make deploy
```

## Cleanup

Remove the deployment:

```bash
make undeploy
```

**Output:**
```
==> Removing llamaindex-websearch-agent from cluster...
release "llamaindex-websearch-agent" uninstalled
```

## Alternative: OpenShift In-Cluster Build

Don't have podman/docker locally? OpenShift can build the image for you.

**From the websearch-agent-local directory:**

```bash
make build-openshift
```

This uses OpenShift BuildConfig to build the image inside the cluster.

## Troubleshooting

### Pod not starting

```bash
# Check pod status
oc get pods

# View detailed events
oc describe pod llamaindex-websearch-agent-<pod-id>

# Check logs
make logs
```

Common issues:
- **ImagePullBackOff**: Image not found in registry (check CONTAINER_IMAGE)
- **CrashLoopBackOff**: Container starting then crashing (check logs)
- **Pending**: Insufficient resources (check resource requests/limits)

### Deployment fails with "field is immutable"

The labels changed. Undeploy first:

```bash
make undeploy
make deploy
```

### Can't access the route

```bash
# Check if route exists
oc get routes

# Check route details
oc describe route llamaindex-websearch-agent
```

For vanilla Kubernetes (not OpenShift), you may need to enable Ingress in `values.yaml`:

```yaml
ingress:
  enabled: true
  className: nginx
  host: agent.example.com
```

## What Got Deployed

| Resource | Purpose |
|----------|---------|
| **Deployment** | Runs your agent container |
| **Service** | ClusterIP service on port 8080 |
| **Secret** | Stores API_KEY |
| **Route** (OpenShift) | HTTPS endpoint with TLS termination |
| **Ingress** (K8s) | HTTPS endpoint (if enabled) |

## Next Steps

- **Compare environments:** [What's Different](04-whats-different.md)
- **Add observability:** [Optional: MLflow](05-optional-mlflow.md)
- **Understand the architecture:** [Overview](00-overview.md)
