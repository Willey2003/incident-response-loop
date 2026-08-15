# Autonomous Incident Response Control Loop

A production-grade, self-contained autonomous incident response system for Kubernetes on vSphere/ESXi. Implements a closed control loop: **Monitor → Analyze → Respond** with zero external dependencies.

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
│        │                       │                         │                  │
│        ▼                       ▼                         ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    LOCAL PRIVATE REGISTRY (Harbor)                    │  │
│  │  registry.local/incident-response/{telemetry-sensor,                 │  │
│  │   threat-contextualizer, reconciler-engine}:<tag>                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
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
- Go 1.22+, Python 3.11+, Docker 24+

### 1. Deploy Local Registry

```bash
# See docs/LOCAL_REGISTRY_BLUEPRINT.md for detailed steps
./scripts/registry-setup.sh
```

### 2. Build and Push Images

```bash
# Configure registry
export REGISTRY=registry.local

# Build all components
make build

# Push to local registry
make push
```

### 3. Deploy to Kubernetes

```bash
# Development
make deploy-dev

# Production (via Kustomize)
make deploy-prod

# Or via Helm
helm install incident-response ./deploy/helm/incident-response-loop \
  -n incident-response --create-namespace
```

### 4. Run Chaos Test

```bash
# Validate end-to-end control loop
cd test/chaos
pip install -r requirements.txt
python chaos_test.py --namespace incident-response --duration 300
```

## Configuration

Each component uses YAML configuration with environment variable overrides:

```yaml
# Example: telemetry-sensor config.yaml
burst_threshold_packets: 10000
burst_threshold_bytes: 10000000
spike_threshold_stddev: 3.0
alert_endpoint: "http://threat-contextualizer:8080/api/v1/alerts"
```

See `configs/` directory for templates and production configs.

## Security Model

### Network Policies
- Baseline: Default deny-all in incident-response namespace
- Allow: Metrics scraping, DNS, K8s API, inter-component communication
- Dynamic: Isolation policies created per-incident (auto-cleanup)

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

## Monitoring & Observability

### Prometheus Metrics
All components expose `/metrics` on port 9090:
- Collection latency, error rates
- Anomaly detection rates by type/severity
- Policy creation/deletion latency
- Replacement success/failure rates
- Queue depths, goroutine counts

### Health Endpoints
- `/api/v1/health` - Liveness/readiness
- `/api/v1/health` - Detailed component status

### Logging
Structured JSON logs with correlation IDs:
```json
{
  "level": "info",
  "ts": "2024-01-15T10:30:00Z",
  "logger": "reconciler.worker-0",
  "msg": "Created isolation NetworkPolicy",
  "policy": "irp-isolate-victim-pod-abc123",
  "namespace": "incident-response",
  "alert_id": "alert-xyz789"
}
```

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

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and data flows |
| [Networking Theory](docs/NETWORKING_THEORY.md) | Anomaly detection algorithms explained |
| [Security Model](docs/SECURITY_MODEL.md) | RBAC, NetworkPolicies, threat model |
| [Local Registry](docs/LOCAL_REGISTRY_BLUEPRINT.md) | Harbor/Registry deployment guide |
| [Operations Guide](docs/OPERATIONS_GUIDE.md) | Day-2 operations, troubleshooting |
| [GitHub Layout](docs/GITHUB_REPOSITORY_LAYOUT.md) | Repository structure & conventions |

## Project Structure

```
incident-response-loop/
├── cmd/                    # Component entry points
│   ├── telemetry-sensor/   # Phase 1 (Go)
│   ├── threat-contextualizer/  # Phase 2 (Python)
│   └── reconciler-engine/  # Phase 3 (Go)
├── pkg/                    # Shared libraries
├── deploy/                 # K8s manifests (Kustomize + Helm)
├── test/                   # Chaos, integration, load tests
├── scripts/                # Operational automation
├── docs/                   # Documentation
├── configs/                # Config templates
└── examples/               # Usage examples
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install tools
make dev-setup

# Install pre-commit hooks
pre-commit install

# Run all checks
make check
```

## License

Apache License 2.0 - see [LICENSE](LICENSE)

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policy.

---

**Built for air-gapped, high-security environments where automated response must be deterministic, auditable, and fully self-contained.**