# Kubernetes/OpenShift Deployment

This directory contains everything needed to deploy the agent to Kubernetes or OpenShift.

## Quick Start

```bash
make init             # Create .env template
# Edit ../.env with your cluster details

make build            # Build container image
make push             # Push to registry
make deploy           # Deploy via Helm
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make help` | Show all available targets |
| `make init` | Create `.env` template |
| `make build` | Build container image |
| `make push` | Push image to registry |
| `make deploy` | Deploy to cluster (Helm) |
| `make dry-run` | Preview manifests |
| `make undeploy` | Remove deployment |
| `make logs` | View pod logs |

## Configuration

Edit `../.env` with your cluster configuration:

```env
API_KEY=your-api-key-here
BASE_URL=https://your-llm-endpoint.com/v1
MODEL_ID=your-model-id
CONTAINER_IMAGE=quay.io/your-username/websearch-agent-demo:latest
```

## Helm Chart Structure

```
deployment/
├── Chart.yaml           # Helm chart metadata
├── values.yaml          # Default values
└── templates/
    ├── deployment.yaml  # Pod deployment
    ├── service.yaml     # ClusterIP service
    ├── secret.yaml      # API key storage
    ├── route.yaml       # OpenShift Route (TLS)
    └── ingress.yaml     # K8s Ingress (optional)
```

## Full Documentation

See [Kubernetes Quickstart](../docs/02-kubernetes-quickstart.md) for detailed instructions.
