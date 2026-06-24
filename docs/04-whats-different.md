# What's Different

While the application code stays the same, Kubernetes deployments add **operational infrastructure** for production use.

## Summary Table

| Aspect | Local | Kubernetes | What Was Added |
|--------|-------|------------|----------------|
| **Packaging** | Python venv | Container image | Dockerfile |
| **Dependencies** | `uv sync` | Baked into image | Multi-stage build |
| **Configuration** | `.env` file | Kubernetes Secret | Secret resource |
| **Networking** | localhost:8001 | Service + Route/Ingress | Service, Route YAML |
| **TLS** | HTTP only | HTTPS with TLS | Route with edge termination |
| **Port** | 8001 (configurable) | 8080 (internal) | PORT env var in Deployment |
| **Security** | Runs as your user | Non-root container | securityContext in Deployment |
| **Health Checks** | None | Liveness + Readiness | Probe configuration |
| **Scaling** | Manual restart | Replicas, HPA | Deployment spec |
| **Resource Limits** | Unlimited | CPU/memory limits | resources in Deployment |
| **Logs** | stdout to terminal | Pod logs (kubectl/oc) | Container runtime |
| **Updates** | `git pull && restart` | Rolling updates | Deployment strategy |
| **Deployment** | `make run-app` | Helm chart | Chart.yaml + templates/ |

## 1. Containerization

### Local: Python Virtual Environment

```bash
# Create venv
uv sync --python 3.12

# Run application
source .venv/bin/activate
uvicorn main:app --port 8001
```

**Pros:**
- Fast iteration (no build step)
- Direct access to code
- Easy debugging

**Cons:**
- Environment drift between machines
- "Works on my machine"
- Manual dependency management

### Kubernetes: Container Image

```dockerfile
# deployment/Dockerfile
FROM registry.access.redhat.com/ubi9/python-312

WORKDIR /opt/app-root/src

# Install dependencies
COPY pyproject.toml .
RUN uv pip install --no-cache ".[tracing]"

# Copy application code
COPY main.py .
COPY src/ ./src/
COPY playground/ ./playground/
COPY images/ ./images/

# Security: non-root user
RUN chown -R 1001:0 /opt/app-root/src
USER 1001

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**What was added:**
- `Dockerfile` - Defines how to build the container
- Base image: Red Hat UBI9 (Universal Base Image)
- Non-root user (UID 1001)
- Immutable artifact (same image everywhere)

**Pros:**
- Identical environment everywhere
- Security hardening baked in
- Version control for entire stack

**Build command:**
```bash
podman build -t websearch-agent:latest -f deployment/Dockerfile .
```

## 2. Configuration Management

### Local: .env File

```bash
# .env (in repository root, git-ignored)
API_KEY=not-needed-for-local-development
BASE_URL=http://localhost:11434/v1
MODEL_ID=llama3.1:8b
PORT=8001
```

**How it's loaded:**
```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("API_KEY")
```

**Pros:**
- Simple to edit
- Version control (via .env.example)

**Cons:**
- Can commit secrets accidentally
- No encryption at rest
- Manual distribution to team

### Kubernetes: Secret + ConfigMap

```yaml
# deployment/templates/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: websearch-agent-secret
type: Opaque
data:
  api-key: c2stdFd2UWxDVFpDLXE1TmhVTDFjajVvUQ==  # base64 encoded
```

```yaml
# deployment/templates/deployment.yaml
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: websearch-agent-secret
        key: api-key
  - name: BASE_URL
    value: "https://litellm.example.com/v1"
  - name: MODEL_ID
    value: "Qwen3.6-35B-A3B"
```

**What was added:**
- `Secret` resource for sensitive data (API keys)
- Environment variable injection via `valueFrom`
- Helm templating for values

**Pros:**
- Secrets encrypted at rest (if configured)
- RBAC controls who can read secrets
- Centralized configuration
- No secrets in git

**How it's created:**
```bash
# Via Helm (in Makefile)
helm upgrade --install websearch-agent deployment/ \
  --set secrets.apiKey="$API_KEY"
```

## 3. Networking

### Local: Direct Port Binding

```bash
# Application binds to localhost:8001
uvicorn main:app --host 127.0.0.1 --port 8001
```

**Access:**
```bash
curl http://localhost:8001/health
```

**Pros:**
- Simple, direct access
- No proxy overhead

**Cons:**
- Only accessible from same machine
- No load balancing
- No TLS

### Kubernetes: Service + Route/Ingress

```yaml
# deployment/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: websearch-agent
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 8080
  selector:
    app: websearch-agent
```

```yaml
# deployment/templates/route.yaml (OpenShift)
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: websearch-agent
spec:
  to:
    kind: Service
    name: websearch-agent
  port:
    targetPort: 8080
  tls:
    termination: edge                    # TLS termination at the router
    insecureEdgeTerminationPolicy: Redirect  # HTTP -> HTTPS redirect
```

**What was added:**
- `Service` - Stable internal endpoint
- `Route` (OpenShift) or `Ingress` (K8s) - External HTTPS endpoint
- TLS certificate (auto-provisioned by OpenShift)

**Access:**
```bash
curl https://websearch-agent-namespace.apps.cluster.example.com/health
```

**Pros:**
- Accessible from anywhere
- Load balancing across replicas
- TLS encryption
- Automatic DNS

## 4. Health Checks

### Local: None

The application runs until you kill it. No automatic recovery.

```bash
# If it crashes:
ps aux | grep uvicorn  # Process is gone
# Manual restart required
make run-app
```

### Kubernetes: Liveness + Readiness Probes

```yaml
# deployment/templates/deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 120
  timeoutSeconds: 5

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 30
  timeoutSeconds: 3
```

**What was added:**
- **Liveness probe**: Restarts container if it becomes unresponsive
- **Readiness probe**: Removes pod from service if it can't handle traffic

**How it works:**
1. Kubernetes calls `/health` every 30 seconds
2. If it returns 200 OK, pod is "ready" and receives traffic
3. If it fails, pod is removed from load balancer
4. If liveness fails repeatedly, pod is restarted

**In practice:**
```bash
# Pod becomes unhealthy
kubectl describe pod websearch-agent-abc123
# Events:
#   Liveness probe failed: Get "http://10.1.2.3:8080/health": dial tcp: i/o timeout
#   Container websearch-agent failed liveness probe, will be restarted

# Kubernetes automatically restarts it
kubectl get pods
# NAME                         READY   STATUS    RESTARTS   AGE
# websearch-agent-abc123       1/1     Running   1          5m
```

## 5. Security

### Local: Default User Permissions

```bash
# Runs as your user (e.g., lkerriso)
whoami  # lkerriso
ps aux | grep uvicorn
# lkerriso  12345  0.2  0.5  ...  uvicorn main:app
```

**Capabilities:**
- Full access to your files
- Can bind to privileged ports (<1024) with sudo
- No restrictions

### Kubernetes: Non-Root Container with Dropped Capabilities

```yaml
# deployment/templates/deployment.yaml
securityContext:
  runAsNonRoot: true

containers:
  - name: agent
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
          - ALL
```

**What was added:**
- `runAsNonRoot`: Container must run as UID > 0
- `allowPrivilegeEscalation: false`: Can't gain more privileges
- Dropped `ALL` capabilities: Minimal permissions

**In the Dockerfile:**
```dockerfile
# Create non-root user
RUN chown -R 1001:0 /opt/app-root/src
USER 1001  # Switch to non-root user
```

**Why it matters:**
- Limits blast radius of container escape
- Compliance with security policies (PodSecurityStandards)
- Best practice for production workloads

## 6. Scaling

### Local: Single Process

```bash
# One process on one machine
make run-app

# Want more capacity?
# Option 1: Bigger machine (vertical scaling)
# Option 2: Run multiple instances manually (horizontal scaling)
```

### Kubernetes: Replicas + Horizontal Pod Autoscaler

```yaml
# deployment/values.yaml
replicaCount: 3  # Run 3 copies
```

```bash
# Scale manually
kubectl scale deployment websearch-agent --replicas=5

# Or enable autoscaling
kubectl autoscale deployment websearch-agent \
  --min=2 --max=10 --cpu-percent=80
```

**What was added:**
- `replicas` field in Deployment
- Load balancing via Service
- Automatic pod distribution across nodes
- Optional HPA for automatic scaling

**How it works:**
```
User Request
     │
     ▼
  Service (load balancer)
     │
     ├─────> Pod 1 (replica 1)
     ├─────> Pod 2 (replica 2)
     └─────> Pod 3 (replica 3)
```

## 7. Resource Management

### Local: Unlimited

```bash
# Uses as much CPU/memory as it wants
# Can starve other processes
# No enforcement
```

### Kubernetes: Requests + Limits

```yaml
# deployment/values.yaml
resources:
  requests:
    memory: "256Mi"  # Guaranteed allocation
    cpu: "100m"      # 0.1 CPU cores
  limits:
    memory: "512Mi"  # Maximum allowed
    cpu: "500m"      # 0.5 CPU cores
```

**What was added:**
- **Requests**: Minimum guaranteed resources
- **Limits**: Maximum allowed resources
- OOM (Out-of-Memory) protection
- CPU throttling (not OOM kill)

**Why it matters:**
- Prevents one pod from starving others
- Enables efficient node packing
- Predictable performance

**What happens when limits are exceeded:**
```
Memory > 512Mi: Pod is OOM-killed and restarted
CPU > 500m: Pod is throttled (not killed)
```

## 8. Deployment Process

### Local: Manual

```bash
# Update code
git pull

# Restart manually
pkill -f uvicorn
make run-app
```

**Cons:**
- Downtime during restart
- Manual process (error-prone)
- No rollback mechanism

### Kubernetes: Rolling Updates

```bash
# Update image
make build
make push

# Deploy new version
make deploy
```

**Helm performs a rolling update:**
```yaml
# deployment/templates/deployment.yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0  # Never take all pods down
    maxSurge: 1        # Can create 1 extra pod during update
```

**How it works:**
1. Create new pod with new image
2. Wait for it to pass readiness probe
3. Add it to service (receives traffic)
4. Remove old pod
5. Repeat until all pods updated

**Zero-downtime update:**
```
Before:  [Pod v1] [Pod v1] [Pod v1]
Step 1:  [Pod v1] [Pod v1] [Pod v1] [Pod v2]  ← New pod created
Step 2:  [Pod v1] [Pod v1] [Pod v2]           ← Old pod removed
Step 3:  [Pod v1] [Pod v1] [Pod v2] [Pod v2]
Step 4:  [Pod v1] [Pod v2] [Pod v2]
Step 5:  [Pod v2] [Pod v2] [Pod v2]           ← Update complete
```

**Rollback if needed:**
```bash
helm rollback websearch-agent
```

## What You Didn't Have to Change

Despite all these differences, **zero lines of Python code changed**.

The application code reads environment variables and serves HTTP requests. It doesn't care:
- If those env vars come from .env or Kubernetes Secret
- If requests come from localhost or a Kubernetes Service
- If it's running in a venv or a container

## Key Insight

**Infrastructure is additive, not invasive.**

You're not rewriting your agent for Kubernetes. You're adding operational infrastructure around it:
- Dockerfile (packaging)
- Helm chart (deployment)
- Health probes (reliability)
- Security context (hardening)

The application code remains blissfully unaware.

## Next Steps

- [What's the Same](03-whats-the-same.md) - Application code that doesn't change
- [Optional: MLflow](05-optional-mlflow.md) - Add observability
- [Overview](00-overview.md) - Architecture comparison
