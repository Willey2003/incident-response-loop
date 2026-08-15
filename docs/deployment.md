# AegisForge Deployment Guide

## Prerequisites

### Development (Docker Compose)
- Docker 24+ with Compose v2
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space
- Linux/macOS/Windows (WSL2)

### Kubernetes (Production)
- Kubernetes 1.29+
- Helm 3.12+
- kubectl configured
- CNI with NetworkPolicy support (Calico, Cilium, Antrea)
- StorageClass for persistent volumes
- Ingress controller (nginx, traefik)
- Cert-manager for TLS (optional)

## Quick Start - Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/aegisforge.git
cd aegisforge

# Configure environment
cp .env.example .env
# Edit .env with secure passwords

# Start stack
make dev-up

# Verify all services healthy
make dev-ps

# Access services
# Analyst Console: http://localhost:3000
# API Gateway: http://localhost:8000
# Grafana: http://localhost:3001 (admin/admin)
# MinIO: http://localhost:9001 (minioadmin/minioadmin)
```

### Service Endpoints (Docker Compose)

| Service | URL | Credentials |
|---------|-----|-------------|
| Analyst Console | http://localhost:3000 | OIDC / dev mode |
| API Gateway | http://localhost:8000 | JWT / dev mode |
| API Docs | http://localhost:8000/docs | - |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Qdrant | http://localhost:6333 | - |
| Ollama API | http://localhost:11434 | - |
| Keycloak | http://localhost:8080 | admin / admin |

## Kubernetes Deployment

### 1. Create Kind Cluster (Development)

```bash
# Create cluster with Calico CNI
make kind-up

# Verify cluster
kubectl get nodes
kubectl get pods -A
```

**kind-config.yaml** includes:
- 3 worker nodes
- Extra port mappings for ingress
- Calico CNI disabled (installed separately)
- Feature gates for sidecar containers

### 2. Deploy with Helm

```bash
# Development deployment
make deploy-dev

# Production deployment
make deploy-prod

# Verify deployment
make deploy-status
```

### Helm Values Structure

```
deploy/helm/aegisforge/
├── Chart.yaml
├── values.yaml              # Default values
├── values-dev.yaml          # Development overrides
├── values-prod.yaml         # Production overrides
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── rbac.yaml
│   ├── network-policies.yaml
│   ├── postgres.yaml
│   ├── redpanda.yaml
│   ├── qdrant.yaml
│   ├── minio.yaml
│   ├── ollama.yaml
│   ├── prometheus.yaml
│   ├── grafana.yaml
│   ├── loki.yaml
│   ├── falco.yaml
│   ├── api-gateway.yaml
│   ├── detection-engine.yaml
│   ├── response-orchestrator.yaml
│   ├── ai-copilot.yaml
│   ├── emulation-controller.yaml
│   ├── target-api.yaml
│   ├── auth-simulator.yaml
│   ├── workload-simulator.yaml
│   ├── dns-simulator.yaml
│   ├── traffic-simulator.yaml
│   ├── analyst-console.yaml
│   ├── keycloak.yaml
│   ├── redis.yaml
│   ├── servicemonitor.yaml
│   ├── poddisruptionbudget.yaml
│   └── horizontalpodautoscaler.yaml
└── charts/                  # Subcharts (optional)
```

### Key Configuration

#### Image Registry
```yaml
global:
  imageRegistry: docker.io
  imageTag: "latest"
  imagePullPolicy: IfNotPresent
  imagePullSecrets:
    - name: registry-credentials
```

#### Resource Management
```yaml
resources:
  limits:
    cpu: "2000m"
    memory: "2Gi"
  requests:
    cpu: "500m"
    memory: "512Mi"
```

#### Network Policies
```yaml
networkPolicies:
  enabled: true
  defaultDeny: true
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: monitoring
      ports:
      - protocol: TCP
        port: 8000
```

#### Persistence
```yaml
persistence:
  postgres:
    enabled: true
    size: 50Gi
    storageClass: fast-ssd
  redpanda:
    enabled: true
    size: 20Gi
  qdrant:
    enabled: true
    size: 20Gi
  minio:
    enabled: true
    size: 100Gi
```

#### AI Configuration
```yaml
ai:
  ollama:
    model: "llama3.2:1b"
    embeddingModel: "all-MiniLM-L6-v2"
    resources:
      limits:
        memory: "8Gi"
        cpu: "4000m"
  qdrant:
    resources:
      limits:
        memory: "4Gi"
  embeddings:
    model: "all-MiniLM-L6-v2"
    batchSize: 32
```

## Configuration Management

### Environment Variables
All services read from environment variables. See `.env.example` for full list.

Key variables:
```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=secure_password

# Kafka/Redpanda
REDPANDA_BROKERS=redpanda:9092

# AI
OLLAMA_MODEL=llama3.2:1b
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security
JWT_SECRET_KEY=your-secure-random-key
AI_REDACT_SECRETS=true
RESPONSE_DRY_RUN=true
RESPONSE_REQUIRE_APPROVAL=true
```

### Secrets Management

**Development**: `.env` file (gitignored)

**Production**: External Secrets Operator
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: aegisforge-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: aegisforge-secrets
    creationPolicy: Owner
  data:
    - secretKey: postgres-password
      remoteRef:
        key: aegisforge/postgres-password
    - secretKey: jwt-secret
      remoteRef:
        key: aegisforge/jwt-secret
```

## TLS Configuration

### Cert-Manager Integration
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: aegisforge-tls
  namespace: aegisforge
spec:
  secretName: aegisforge-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - aegisforge.example.com
    - api.aegisforge.example.com
    - console.aegisforge.example.com
```

### mTLS (Optional - with Istio/Linkerd)
```yaml
# PeerAuthentication for strict mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: aegisforge
spec:
  mtls:
    mode: STRICT
```

## Upgrading

### Helm Upgrade
```bash
# Upgrade to new version
helm upgrade aegisforge deploy/helm/aegisforge \
  -n aegisforge \
  -f deploy/helm/aegisforge/values-prod.yaml \
  --set global.imageTag=v1.2.0 \
  --wait --timeout=10m

# Rollback if needed
helm rollback aegisforge -n aegisforge
```

### Database Migrations
```bash
# Run migrations
kubectl exec -n aegisforge deploy/api-gateway -- alembic upgrade head

# Check migration status
kubectl exec -n aegisforge deploy/api-gateway -- alembic current
```

### Blue-Green Deployment
```bash
# Deploy to new namespace
helm upgrade --install aegisforge-green deploy/helm/aegisforge \
  -n aegisforge-green --create-namespace \
  -f deploy/helm/aegisforge/values-prod.yaml

# Switch traffic (update Ingress)
kubectl patch ingress aegisforge -n aegisforge \
  -p '{"spec":{"rules":[{"host":"aegisforge.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"api-gateway-green","port":{"number":8000}}}}]}}]}}'
```

## Monitoring & Validation

### Health Checks
```bash
# Check all pods
kubectl get pods -n aegisforge -o wide

# Check service endpoints
kubectl get endpoints -n aegisforge

# Check ingress
kubectl get ingress -n aegisforge
```

### Smoke Test
```bash
make smoke-test
```

This runs:
1. Deploys test scenario
2. Generates events
2. Verifies detection
3. Creates incident
4. Requests approval
5. Performs dry-run
6. Verifies audit log

### Health Endpoints
| Service | Endpoint |
|---------|----------|
| API Gateway | GET /health |
| Detection Engine | GET /health |
| Response Orchestrator | GET /health |
| AI Copilot | GET /health |
| Emulation Controller | GET /health |

## Troubleshooting

### Common Issues

**Pods stuck in Pending**
```bash
kubectl describe pod <pod-name> -n aegisforge
# Check: resource requests, node selectors, PVC binding
```

**ImagePullBackOff**
```bash
# Check image name, registry credentials
kubectl describe pod <pod-name> -n aegisforge
# Verify registry credentials secret exists
```

**CrashLoopBackOff**
```bash
kubectl logs <pod-name> -n aegisforge --previous
# Check application logs, config, dependencies
```

**NetworkPolicy blocking traffic**
```bash
# Check NetworkPolicy rules
kubectl get netpol -n aegisforge -o yaml
# Test connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot -- nslookup <service>
```

### Logs
```bash
# All services
kubectl logs -l app.kubernetes.io/part-of=aegisforge -n aegisforge --tail=100 -f

# Specific service
kubectl logs -l app.kubernetes.io/name=detection-engine -n aegisforge -f

# Infrastructure
kubectl logs -l app=postgres -n aegisforge -f
```

### Database Access
```bash
# Port forward
kubectl port-forward -n aegisforge svc/postgres 5432:5432

# Connect
psql -h localhost -U aegisforge -d aegisforge
```

## Backup & Restore

### PostgreSQL Backup
```bash
# Backup
kubectl exec -n aegisforge postgres-0 -- pg_dump -U aegisforge aegisforge > backup.sql

# Restore
kubectl exec -i -n aegisforge postgres-0 -- psql -U aegisforge aegisforge < backup.sql
```

### MinIO Backup
```bash
# Using mc (MinIO client)
mc mirror --overwrite minio/aegisforge-evidence ./backup/evidence
mc mirror --overwrite minio/aegisforge-artifacts ./backup/artifacts
```

### Redpanda Backup
```bash
# Topic replication is primary HA
# For disaster recovery, use rpk topic export/import
```

## Security Hardening Checklist

- [ ] Change all default passwords in `.env`
- [ ] Use External Secrets Operator for production
- [ ] Enable NetworkPolicies (default deny)
- [ ] Configure PodSecurity Standards (restricted)
- [ ] Enable admission controllers (OPA/Gatekeeper)
- [ ] Configure mTLS (Istio/Linkerd)
- [ ] Set up cert-manager for TLS
- [ ] Configure external-dns for DNS
- [ ] Enable audit logging on K8s API
- [ ] Set up Falco with custom rules
- [ ] Configure image signing verification (cosign)
- [ ] Enable SBOM generation in CI/CD
- [ ] Set up vulnerability scanning (Trivy)
- [ ] Configure backup schedules
- [ ] Test disaster recovery procedures
- [ ] Document incident response procedures