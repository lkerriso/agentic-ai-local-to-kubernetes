# Resources

## Upstream Project

**This repository is adapted from:**
- **Source:** [agentic-starter-kits](https://github.com/redhat-et/agentic-starter-kits)
- **Template:** `agents/llamaindex/templates/websearch_agent`
- **License:** MIT

The upstream project contains additional agent templates and advanced examples.

## Technologies Used

### Agent Framework
- **LlamaIndex**
  - [Official Documentation](https://docs.llamaindex.ai/)
  - [Workflows Guide](https://docs.llamaindex.ai/en/stable/module_guides/workflow/)
  - [Tool Calling](https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/)
  - [OpenAILike LLM](https://docs.llamaindex.ai/en/stable/examples/llm/openai_like/)

### API Framework
- **FastAPI**
  - [Official Documentation](https://fastapi.tiangolo.com/)
  - [OpenAPI Specification](https://swagger.io/specification/)
  - [Uvicorn](https://www.uvicorn.org/) (ASGI server)

### LLM Backends

**Local:**
- **Ollama**
  - [Official Documentation](https://ollama.com/docs)
  - [Model Library](https://ollama.com/library)
  - [API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

**Kubernetes/Production:**
- **LiteLLM** (OpenAI-compatible proxy)
  - [Documentation](https://docs.litellm.ai/)
  - [Supported Models](https://docs.litellm.ai/docs/providers)
- **OpenShift AI / RHOAI**
  - [Product Documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed)
  - [Model Serving](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.14/html/serving_models)
- **OpenAI API**
  - [API Reference](https://platform.openai.com/docs/api-reference)
  - [Models](https://platform.openai.com/docs/models)

### Container & Orchestration

**Containerization:**
- **Podman**
  - [Official Documentation](https://podman.io/docs)
  - [Podman vs Docker](https://podman.io/whatis.html)
- **Docker**
  - [Official Documentation](https://docs.docker.com/)
  - [Dockerfile Reference](https://docs.docker.com/reference/dockerfile/)

**Kubernetes:**
- **Kubernetes**
  - [Official Documentation](https://kubernetes.io/docs/)
  - [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
  - [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
  - [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- **OpenShift**
  - [Official Documentation](https://docs.openshift.com/)
  - [Routes](https://docs.openshift.com/container-platform/latest/networking/routes/route-configuration.html)
  - [Security Context Constraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)

**Helm:**
- **Helm 3**
  - [Official Documentation](https://helm.sh/docs/)
  - [Charts Guide](https://helm.sh/docs/topics/charts/)
  - [Template Functions](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/)

### Observability

**MLflow:**
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Tracing](https://mlflow.org/docs/latest/llms/tracing/index.html)
- [LlamaIndex Integration](https://docs.llamaindex.ai/en/stable/examples/observability/mlflow/)

### Python Tooling

**uv (Package Manager):**
- [Official Documentation](https://docs.astral.sh/uv/)
- [Installation](https://docs.astral.sh/uv/getting-started/installation/)
- [Commands](https://docs.astral.sh/uv/reference/cli/)

## Architecture Patterns

### 12-Factor App
- [12factor.net](https://12factor.net/)
  - III. Config (Environment variables)
  - VII. Port binding
  - VIII. Concurrency
  - IX. Disposability

### Cloud Native Patterns
- [CNCF Cloud Native Definition](https://github.com/cncf/toc/blob/main/DEFINITION.md)
- [Container Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)
- [Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

### AI Agent Patterns
- [LangChain Agent Types](https://python.langchain.com/docs/modules/agents/agent_types/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

## Security

**Container Security:**
- [Red Hat Container Security Guide](https://www.redhat.com/en/resources/container-security-openshift-cloud-devops-whitepaper)
- [NIST Application Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

**Kubernetes Security:**
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Secrets Management Best Practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Related Projects

**AI Agent Frameworks:**
- [LangChain](https://www.langchain.com/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)

**Model Serving:**
- [vLLM](https://github.com/vllm-project/vllm)
- [Text Generation Inference](https://github.com/huggingface/text-generation-inference)
- [Triton Inference Server](https://github.com/triton-inference-server/server)

**OpenShift AI Ecosystem:**
- [RHOAI Documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed)
- [Model Mesh](https://github.com/kserve/modelmesh-serving)
- [Kubeflow](https://www.kubeflow.org/)

## Community & Support

**GitHub Discussions:**
- [Upstream agentic-starter-kits](https://github.com/redhat-et/agentic-starter-kits/discussions)
- [LlamaIndex Discord](https://discord.gg/dGcwcsnxhU)

**Stack Overflow Tags:**
- [kubernetes](https://stackoverflow.com/questions/tagged/kubernetes)
- [openshift](https://stackoverflow.com/questions/tagged/openshift)
- [llamaindex](https://stackoverflow.com/questions/tagged/llamaindex)
- [fastapi](https://stackoverflow.com/questions/tagged/fastapi)

**Red Hat Community:**
- [OpenShift Commons](https://commons.openshift.org/)
- [Red Hat Developer](https://developers.redhat.com/)

## Tutorials & Guides

**Getting Started with Agents:**
- [LlamaIndex Quick Start](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/)
- [Building Production Agents](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/)

**Kubernetes Deployment:**
- [Kubernetes Basics Tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Deploy a Stateless Application](https://kubernetes.io/docs/tasks/run-application/run-stateless-application-deployment/)

**Helm Charts:**
- [Helm Quick Start](https://helm.sh/docs/intro/quickstart/)
- [Chart Development Tips](https://helm.sh/docs/howto/charts_tips_and_tricks/)

## Books

**Kubernetes:**
- *Kubernetes: Up and Running* by Brendan Burns et al.
- *Cloud Native DevOps with Kubernetes* by John Arundel & Justin Domingus

**AI Agents:**
- *Building LLM-Powered Applications* (coming soon from O'Reilly)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/) (comprehensive online resource)

**Container Development:**
- *Docker Deep Dive* by Nigel Poulton
- *Podman in Action* by Daniel Walsh

## Talks & Videos

**Agent Development:**
- [LlamaIndex Webinars](https://www.llamaindex.ai/webinars)
- [OpenAI DevDay](https://devday.openai.com/)

**Kubernetes:**
- [KubeCon + CloudNativeCon](https://www.cncf.io/kubecon-cloudnativecon-events/)
- [Kubernetes Podcast](https://kubernetespodcast.com/)

**Red Hat:**
- [Red Hat Summit](https://www.redhat.com/en/summit)
- [OpenShift Commons Briefings](https://commons.openshift.org/briefings.html)

## Example Repositories

**Similar Projects:**
- [LlamaIndex Examples](https://github.com/run-llama/llama_index/tree/main/docs/docs/examples)
- [FastAPI Examples](https://github.com/tiangolo/fastapi/tree/master/docs_src)
- [Helm Chart Examples](https://github.com/helm/charts)

**Production Deployments:**
- [OpenShift AI Examples](https://github.com/opendatahub-io/odh-manifests)
- [Kubeflow Examples](https://github.com/kubeflow/examples)

## Contributing

Found an issue or want to contribute?

- **Upstream:** [agentic-starter-kits](https://github.com/redhat-et/agentic-starter-kits)
- **This Talk Repo:** File issues or PRs for documentation improvements

## License

This repository is licensed under the **MIT License**, matching the upstream project.

See [LICENSE](../LICENSE) for full text.

---

## Next Steps

- **Start Local:** [Local Quickstart](01-local-quickstart.md)
- **Deploy to K8s:** [Kubernetes Quickstart](02-kubernetes-quickstart.md)
- **Understand Architecture:** [Overview](00-overview.md)
