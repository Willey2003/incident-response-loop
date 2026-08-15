# GitHub Repository Layout for Incident Response Control Loop

This document describes the production-ready directory structure for committing this multi-module project to a local or private GitHub repository.

## Complete Directory Structure

```
incident-response-loop/
├── .github/
│   ├── workflows/
│   │   ├── build-and-test.yaml        # CI pipeline
│   │   ├── security-scan.yaml         # Security scanning (Trivy, gosec, bandit)
│   │   ├── release.yaml               # Release automation
│   │   └── dependency-update.yaml     # Dependabot/Renovate config
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── security_vulnerability.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml
├── .gitignore                          # Comprehensive ignore rules
├── .golangci.yml                       # Go linter configuration
├── .pre-commit-config.yaml             # Pre-commit hooks
├── .yamllint.yml                       # YAML linter configuration
├── LICENSE                             # Apache 2.0
├── README.md                           # Project overview
├── CONTRIBUTING.md                     # Contribution guidelines
├── SECURITY.md                         # Security policy
├── Makefile                            # Build automation
├── docker-compose.yml                  # Local development stack
├── docker-compose.override.yml.example # Local override template
├── go.work                             # Go workspace (for multi-module)
│
├── cmd/                                # Application entry points (one per component)
│   ├── telemetry-sensor/               # Phase 1: Monitoring Layer
│   │   ├── main.go                     # Entry point
│   │   ├── go.mod                      # Go module definition
│   │   ├── go.sum                      # Go checksums
│   │   ├── config.yaml                 # Default configuration
│   │   ├── Dockerfile                  # Multi-stage build
│   │   ├── .dockerignore
│   │   ├── pkg/
│   │   │   ├── sensor/                 # Sensor implementation
│   │   │   │   ├── sensor.go           # Main sensor logic
│   │   │   │   ├── anomaly.go          # Anomaly detection algorithms
│   │   │   │   └── collectors/         # Metric collectors
│   │   │   │       ├── cgroup.go       # cgroup v2 collector
│   │   │   │       ├── ebpf.go         # eBPF collector (optional)
│   │   │   │       ├── kubelet.go      # Kubelet summary API collector
│   │   │   │       └── cadvisor.go     # cAdvisor collector
│   │   │   └── shared/                 # Shared utilities
│   │   │       ├── config.go           # Configuration management
│   │   │       ├── http.go             # HTTP client with pooling
│   │   │       └── metrics.go          # Prometheus metrics
│   │   └── test/
│   │       ├── integration_test.go
│   │       └── benchmarks_test.go
│   │
│   ├── threat-contextualizer/          # Phase 2: Parsing Layer
│   │   ├── src/
│   │   │   └── contextualizer/
│   │   │       ├── __init__.py
│   │   │       ├── main.py             # FastAPI application
│   │   │       ├── config.py           # Pydantic settings
│   │   │       ├── models.py           # Pydantic data models
│   │   │       ├── threat_intel.py     # Threat intelligence engine
│   │   │       ├── pipeline.py         # Processing pipeline
│   │   │       ├── client.py           # Reconciler HTTP client
│   │   │       └── metrics.py          # Prometheus metrics
│   │   ├── data/
│   │   │   └── threat_intel.json       # Mock threat intelligence DB
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_threat_intel.py
│   │   │   ├── test_pipeline.py
│   │   │   ├── test_models.py
│   │   │   └── conftest.py
│   │   ├── pyproject.toml              # Python project config
│   │   ├── uv.lock                     # Locked dependencies
│   │   ├── Dockerfile                  # Multi-stage build
│   │   ├── .dockerignore
│   │   ├── .python-version             # Python version pin
│   │   └── requirements-dev.txt        # Dev dependencies
│   │
│   └── reconciler-engine/              # Phase 3: Defense Layer
│       ├── main.go                     # Entry point
│       ├── go.mod                      # Go module definition
│       ├── go.sum                      # Go checksums
│       ├── config.yaml                 # Default configuration
│       ├── Dockerfile                  # Multi-stage build
│       ├── .dockerignore
│       ├── pkg/
│       │   ├── reconciler/             # Reconciler implementation
│       │   │   ├── reconciler.go       # Main reconciler logic
│       │   │   ├── networkpolicy.go    # NetworkPolicy management
│       │   │   ├── workload.go         # Workload replacement logic
│       │   │   ├── alert_handler.go    # HTTP alert endpoint
│       │   │   └── safety.go           # Safety controls & validation
│       │   └── shared/                 # Shared utilities
│       │       ├── config.go           # Configuration management
│       │       ├── metrics.go          # Prometheus metrics
│       │       └── k8s.go              # Kubernetes client helpers
│       └── test/
│           ├── integration_test.go
│           └── mocks/
│
├── pkg/                                # Shared libraries (cross-component)
│   ├── common/                         # Common utilities
│   │   ├── logging/                    # Structured logging setup
│   │   ├── metrics/                    # Shared Prometheus metrics
│   │   ├── health/                     # Health check utilities
│   │   ├── version/                    # Version information
│   │   └── signals/                    # Signal handling
│   ├── k8s/                            # Kubernetes utilities
│   │   ├── client/                     # Client builders
│   │   ├── informers/                  # Informer factories
│   │   └── labels/                     # Label/annotation constants
│   └── net/                            # Network utilities
│       ├── cidr/                       # CIDR parsing
│       └── entropy/                    # Entropy calculation
│
├── deploy/                             # Deployment manifests
│   ├── manifests/                      # Kustomize base
│   │   ├── kustomization.yaml
│   │   ├── 00-namespace.yaml
│   │   ├── 01-rbac.yaml
│   │   ├── 02-telemetry-sensor.yaml
│   │   ├── 03-threat-contextualizer.yaml
│   │   ├── 04-reconciler-engine.yaml
│   │   ├── 05-network-policies.yaml
│   │   └── overlays/
│   │       ├── development/
│   │       │   ├── kustomization.yaml
│   │       │   └── patches/
│   │       ├── staging/
│   │       │   ├── kustomization.yaml
│   │       │   └── patches/
│   │       └── production/
│   │           ├── kustomization.yaml
│   │           └── patches/
│   ├── helm/                           # Helm charts (alternative)
│   │   └── incident-response-loop/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-dev.yaml
│   │       ├── values-prod.yaml
│   │       ├── templates/
│   │       │   ├── namespace.yaml
│   │       │   ├── rbac.yaml
│   │       │   ├── telemetry-sensor.yaml
│   │       │   ├── threat-contextualizer.yaml
│   │       │   ├── reconciler-engine.yaml
│   │       │   ├── network-policies.yaml
│   │       │   ├── servicemonitor.yaml
│   │       │   └── _helpers.tpl
│   │       └── charts/
│   └── registry/                       # Registry deployment
│       ├── harbor/
│       │   ├── harbor.yml.template
│       │   └── docker-compose.yml
│       └── basic-registry/
│           ├── config.yml
│           └── docker-compose.yml
│
├── test/                               # Integration and chaos tests
│   ├── chaos/
│   │   ├── chaos_test.py               # Main chaos test script
│   │   ├── scenarios/
│   │   │   ├── __init__.py
│   │   │   ├── burst_traffic.py
│   │   │   ├── payload_spike.py
│   │   │   ├── c2_beaconing.py
│   │   │   ├── port_scan.py
│   │   │   ├── crypto_miner.py
│   │   │   ├── reverse_shell.py
│   │   │   ├── log4shell.py
│   │   │   └── mimikatz.py
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── policy_validator.py
│   │   │   ├── replacement_validator.py
│   │   │   └── availability_validator.py
│   │   └── requirements.txt
│   ├── integration/
│   │   ├── test_e2e.go
│   │   ├── test_sensor_to_contextualizer.go
│   │   ├── test_contextualizer_to_reconciler.go
│   │   └── fixtures/
│   └── load/
│       ├── k6/
│       │   ├── sensor_load.js
│       │   └── contextualizer_load.js
│       └── vegeta/
│           └── attack_rate.txt
│
├── scripts/                            # Operational scripts
│   ├── build-all.sh                    # Build all components
│   ├── push-images.sh                  # Push to local registry
│   ├── deploy.sh                       # Deploy via kustomize
│   ├── undeploy.sh                     # Cleanup deployment
│   ├── cert-gen.sh                     # Generate TLS certificates
│   ├── registry-setup.sh               # Local registry setup
│   ├── backup.sh                       # Backup configs/secrets
│   ├── restore.sh                      # Restore from backup
│   └── migrate.sh                      # Data migration utilities
│
├── docs/                               # Documentation
│   ├── ARCHITECTURE.md                 # System architecture
│   ├── DESIGN_DECISIONS.md             # ADRs (Architecture Decision Records)
│   ├── LOCAL_REGISTRY_BLUEPRINT.md     # Registry deployment guide
│   ├── GITHUB_REPOSITORY_LAYOUT.md     # This file
│   ├── API_REFERENCE.md                # API documentation
│   ├── OPERATIONS_GUIDE.md             # Day-2 operations
│   ├── TROUBLESHOOTING.md              # Common issues
│   ├── SECURITY_MODEL.md               # Security architecture
│   ├── NETWORKING_THEORY.md            # Anomaly detection theory
│   ├── RBAC_GUIDE.md                   # Least-privilege RBAC
│   ├── UPGRADE_GUIDE.md                # Version upgrades
│   └── diagrams/
│       ├── architecture.mmd            # Mermaid diagrams
│       ├── data_flow.mmd
│       ├── deployment.mmd
│       └── rbac.mmd
│
├── configs/                            # Configuration templates
│   ├── telemetry-sensor/
│   │   ├── config.yaml.template
│   │   └── config.prod.yaml
│   ├── threat-contextualizer/
│   │   ├── config.yaml.template
│   │   └── config.prod.yaml
│   └── reconciler-engine/
│       ├── config.yaml.template
│       └── config.prod.yaml
│
└── examples/                           # Usage examples
    ├── custom-threat-intel/
    │   ├── threat_intel.json
    │   └── README.md
    ├── custom-network-policies/
    │   ├── deny-all.yaml
    │   ├── allow-monitoring.yaml
    │   └── README.md
    └── chaos-scenarios/
        ├── scenario-1-burst.yaml
        └── scenario-2-c2.yaml
```

## Key Design Principles

### 1. Component Isolation (`cmd/`)
Each microservice is a self-contained module with its own:
- Entry point (`main.go` / `main.py`)
- Dependencies (`go.mod` / `pyproject.toml`)
- Configuration (`config.yaml`)
- Dockerfile
- Internal packages (`pkg/`)
- Tests

### 2. Shared Code (`pkg/`)
Cross-cutting concerns live in `pkg/` to avoid duplication:
- Common utilities (logging, metrics, health)
- Kubernetes client helpers
- Network utilities

### 3. Deployment Separation (`deploy/`)
- **Kustomize** for Kubernetes-native deployments with overlays
- **Helm** as alternative for teams preferring Helm
- **Registry** deployment configs included

### 4. Testing Strategy (`test/`)
- **Chaos tests** validate end-to-end control loop
- **Integration tests** verify component interactions
- **Load tests** ensure performance under stress

### 5. Configuration Management (`configs/`)
- Template files with `.template` extension
- Environment-specific overrides (`.prod.yaml`)
- Never commit actual secrets

## Gitignore Rules (Complete)

See `.gitignore` in root for comprehensive rules covering:

```
# Binaries
*.exe, *.out, *.test, *.bin
telemetry-sensor, threat-contextualizer, reconciler-engine

# Go
go.sum (in vendor/), go.work

# Python
__pycache__/, *.pyc, .venv/, venv/, *.egg-info/

# IDE
.vscode/, .idea/, *.swp, .DS_Store

# Kubernetes Secrets
*.kubeconfig, *.pem, *.key, *.crt, *.csr

# Local Registry
.docker/, registry/, *.tar

# Terraform
*.tfstate, *.tfvars, .terraform/

# Logs & Temp
*.log, *.tmp, /tmp/, /var/log/

# Environment
.env, .env.local, .env.*.local

# Build Artifacts
dist/, build/, coverage.out, test-results/
```

## CI/CD Pipeline (`.github/workflows/`)

### build-and-test.yaml
```yaml
# On every push/PR:
# 1. Lint (golangci-lint, ruff, yamllint)
# 2. Unit tests (go test, pytest)
# 3. Build Docker images
# 4. Security scan (Trivy, gosec, bandit)
# 5. Integration tests (kind cluster)
# 6. Push to registry on main branch
```

### security-scan.yaml
```yaml
# Scheduled daily:
# 1. Dependency vulnerability scan
# 2. Container image scan
# 3. SAST analysis
# 4. License compliance check
```

### release.yaml
```yaml
# On tag push:
# 1. Build release binaries
# 2. Generate SBOM (Syft)
# 3. Sign artifacts (Cosign)
# 4. Create GitHub Release
# 5. Update Helm chart repo
```

## Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: detect-private-key

- repo: https://github.com/golangci/golangci-lint
  hooks:
  - id: golangci-lint

- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
  - id: ruff
    args: [--fix]
  - id: ruff-format

- repo: https://github.com/bridgecrewio/checkov
  hooks:
  - id: checkov
    args: [-d, deploy/]
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone <repo-url> incident-response-loop
cd incident-response-loop

# Install pre-commit hooks
pre-commit install

# Install development tools
make dev-setup
```

### 2. Local Development
```bash
# Start local stack (registry + k8s kind cluster)
docker-compose up -d

# Build all components
make build

# Run tests
make test

# Deploy to local cluster
make deploy-local
```

### 3. Making Changes
```bash
# Create feature branch
git checkout -b feature/new-detection-rule

# Make changes
# ... edit code ...

# Run pre-commit checks
pre-commit run --all-files

# Run tests
make test

# Commit with conventional commits
git commit -m "feat(sensor): add new entropy-based detection"

# Push and create PR
git push origin feature/new-detection-rule
```

### 4. Release Process
```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# CI/CD handles rest automatically
```

## Security Practices

### 1. Secret Management
- **Never commit secrets** - enforced by pre-commit hooks
- Use **SealedSecrets** or **External Secrets Operator** in cluster
- Local development uses `.env` files (gitignored)

### 2. Dependency Security
- **Go**: `go vet`, `gosec`, `govulncheck` in CI
- **Python**: `bandit`, `safety`, `pip-audit` in CI
- **Container**: `trivy` scans on every build

### 3. Supply Chain
- **SBOM generation** (Syft) on release
- **Artifact signing** (Cosign) on release
- **Pin dependencies** with lock files (`go.sum`, `uv.lock`)
- **Renovate/Dependabot** for automated updates

### 4. Code Review Requirements
- **CODEOWNERS** defines required reviewers per component
- **Security team** must approve RBAC/NetworkPolicy changes
- **Minimum 2 approvals** for merge

## Branch Strategy

```
main (protected)
  ├── release/v1.0.x (maintenance branches)
  ├── feature/* (feature branches)
  ├── fix/* (bug fixes)
  ├── security/* (security patches)
  └── docs/* (documentation updates)
```

### Protection Rules for `main`
- Require PR reviews (2 minimum)
- Require status checks (CI pass)
- Require linear history
- No force pushes
- Signed commits required

## Monitoring Repository Health

### Metrics to Track
- **Build success rate** (>95%)
- **Test coverage** (>80% per component)
- **Vulnerability count** (0 critical/high)
- **Dependency freshness** (<30 days behind)
- **Release frequency** (monthly minimum)

### Automated Alerts
- Dependabot PRs for vulnerabilities
- CI failure notifications
- License compliance violations
- Stale branch cleanup

---

This layout ensures:
✅ Clear separation of concerns
✅ Scalable for team growth
✅ Security-first defaults
✅ Automated quality gates
✅ Production-ready deployment
✅ Comprehensive testing
✅ Operational excellence