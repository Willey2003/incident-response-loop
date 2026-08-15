# AegisForge - Autonomous Cyber Defense Platform

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.22+-blue.svg)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![Node Version](https://img.shields.io/badge/Node-20+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.29+-blue.svg)](https://kubernetes.io/)

A production-grade, CPU-only cyber-defense and resilient cloud-orchestration platform for authorized enterprise security validation. The platform implements a closed control loop: **Monitor → Analyze → Respond** with zero external dependencies.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INCIDENT RESPONSE CONTROL LOOP                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐     ┌──────────────────┐     ┌────────────────────────┐  │
│  │  PHASE 1     │     │    PHASE 2       │     │      PHASE 3           │  │
│  │  MONITORING  │────▶│   PARSING        │────▶│     DEFENSE            │  │
│  │  LAYER       │     │   LAYER          │     │     LAYER              │  │
│  │              │     │                  │     │                        │  │
│  │ Telemetry    │     │ Threat           │     │ Reconciler             │  │
│  │ Sensor       │     │ Contextualizer   │     │ Engine                 │  │
│  │ (Go)         │     │ (Python)         │     │ (Go)                   │  │
│  └──────────────┘     └──────────────────┘     └────────────────────────┘  │
│        │                       │                       │                  │
│        ▼                       ▼                       ▼                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    LOCAL PRIVATE REGISTRY (Harbor)                    │  │
│  │  registry.local/incident-response/{telemetry-sensor,                 │  │
│  │   threat-contextualizer, reconciler-engine}:<tag>                   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Language | Purpose | Port |
|-----------|----------|---------|------|
| **Telemetry Sensor** | Go | DaemonSet monitoring pod metrics & network anomalies | 9090 (metrics) |
| **Threat Contextualizer** | Python (FastAPI) | Enriches alerts with mock CVE/MITRE/IoC intelligence | 8080 (HTTP), 9090 (metrics) |
| **Reconciler Engine** | Go | Creates isolation NetworkPolicies & triggers pod replacement | 8080 (HTTP), 9090 (metrics) |

## Key Features

- **Fully Offline**: No external API dependencies; runs entirely on-premises
- **Zero-Trust Isolation**: Dynamic NetworkPolicies with deny-all ingress/egress
- **Automated Replacement**: Rolling restart/recreate/scale of clean workloads
- **Least-Privilege RBAC**: Namespace-scoped Roles (not ClusterRoles)
- **High Performance**: Connection pooling, async processing, eBPF support
- **Observable**: Prometheus metrics, structured logging, distributed tracing ready
- **Secure Supply Chain**: Distroless images, SBOM, signed artifacts

## Quick Start

### Prerequisites

- vSphere 7.0+ / ESXi 7.0+
- Kubernetes 1.27+ (kubeadm, RKE2, or Tanzu)
- CNI with NetworkPolicy support (Calico, Antrea, Cilium)
- Local Docker registry (Harbor recommended)
- Go 1.22+, Python 3.11+, Node.js 20+, Docker 24+

### 1. Deploy Local Registry

```bash
# See docs/LOCAL_REGISTRY_BLUEPRINT.md for detailed steps
./scripts/registry-setup.sh
```

### 2. Build & Push Images

```bash
cd /home/gaganpreet/aegisforge
make docker-build
REGISTRY=your-registry.example.com make push
```

### 3. Deploy to Kubernetes

```bash
# Development
make deploy-dev

# Production (via Kustomize)
make deploy-prod

# Or via Helm
helm install aegisforge ./deploy/helm/aegisforge \
  -n incident-response --create-namespace
```

### 4. Run Chaos Test

```bash
cd test/chaos
pip install -r requirements.txt
python chaos_test.py --namespace incident-response --duration 300
```

## Project Structure

```
aegisforge/
├── cmd/                          # Application entry points
│   ├── telemetry-sensor/         # Phase 1: Monitoring (Go)
│   ├── threat-contextualizer/    # Phase 2: Parsing (Python/FastAPI)
│   └── reconciler-engine/        # Phase 3: Defense (Go)
├── pkg/                          # Shared libraries
│   ├── common/                   # Common utilities
│   ├── k8s/                      # Kubernetes utilities
│   └── net/                      # Network utilities
├── deploy/                       # Deployment manifests
│   ├── manifests/                # Kustomize base + overlays
│   ├── helm/                     # Helm charts
│   └── registry/                 # Registry deployment
├── test/                         # Test suites
│   ├── chaos/                    # Chaos testing
│   ├── integration/              # Integration tests
│   └── load/                     # Load testing
├── scripts/                      # Operational scripts
├── docs/                         # Documentation
├── web/                          # Web frontend (React + TypeScript)
├── Makefile                      # Build automation
├── docker-compose.dev.yml        # Local development stack
└── .github/workflows/            # CI/CD pipelines
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and data flows |
| [Networking Theory](docs/NETWORKING_THEORY.md) | Anomaly detection algorithms explained |
| [Security Model](docs/SECURITY_MODEL.md) | RBAC, NetworkPolicies, threat model |
| [Local Registry](docs/LOCAL_REGISTRY_BLUEPRINT.md) | Harbor/Registry deployment guide |
| [Operations Guide](docs/OPERATIONS_GUIDE.md) | Day-2 operations, troubleshooting |
| [CPU-only AI](docs/CPU_ONLY_AI.md) | CPU-only AI implementation guide |
| [Incident Response](docs/INCIDENT_RESPONSE_RUNBOOKS.md) | Runbook procedures |
| [Benchmark Plan](docs/BENCHMARK_PLAN.md) | Performance benchmarking methodology |

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yaml`) includes:

- **Lint**: golangci-lint, Ruff, yamllint, hadolint
- **Security**: gosec, govulncheck, bandit, Trivy, pip-audit
- **Test**: Go unit tests, Python pytest, integration tests (Kind)
- **Build**: Multi-arch Docker images with SBOM/provenance
- **Release**: Cosign signing + SBOM attestation + GitHub Release
- **Dependabot**: Weekly dependency updates

## Security Model

### Network Policies
- Default deny-all in incident-response namespace
- Allow: Metrics scraping, DNS, K8s API, inter-component communication
- Dynamic: Isolation policies created per-incident

### RBAC (Least Privilege)
```
ServiceAccount: telemetry-sensor
  Role: pods/nodes read, metrics.k8s.io read

ServiceAccount: threat-contextualizer
  Role: configmaps read (optional)

ServiceAccount: reconciler-engine
  Role: networkpolicies CRUD, pods read/delete, workloads patch
```
*No ClusterRoles. All Roles namespace-scoped to incident-response.*

### Container Security
- Distroless/base images (no shell, no package manager)
- Non-root users (UID 65532 / 1000)
- Read-only root filesystem
- Dropped all capabilities
- Seccomp/AppArmor profiles recommended

## Testing

```bash
# Unit tests
make test

# Integration tests (requires kind)
make test-integration

# Chaos tests (requires deployed stack)
make test-chaos

# Load tests
make test-load
```

## License

Apache License 2.0 - see [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policy.

---

**Built for air-gapped, high-security environments where automated response must be deterministic, auditable, and fully self-contained.**