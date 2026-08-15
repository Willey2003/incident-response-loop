# AegisForge Architecture

## Overview

AegisForge is a CPU-only cyber-defense and resilient cloud-orchestration platform designed for authorized enterprise security validation. The platform collects defensive telemetry, detects suspicious behavior, executes safe pre-approved validation simulations, orchestrates approval-gated containment workflows, and creates evidence-rich incident reports.

## System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AEGISFORGE PLATFORM BOUNDARY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐     ┌─────────────────────┐     ┌────────────────┐  │
│  │  EXTERNAL        │     │   INFRASTRUCTURE    │     │   CORE         │  │
│  │  INTEGRATIONS    │     │   LAYER             │     │   SERVICES     │  │
│  │                  │     │                     │     │                │  │
│  │ • SIEM           │     │ • PostgreSQL        │     │ • API Gateway  │  │
│  │ • SOAR           │     │ • Redpanda/Kafka    │     │ • Detection    │  │
│  │ • Ticketing      │     │ • Qdrant            │     │ • Response     │  │
│  │ • Threat Intel   │     │ • MinIO             │     │ • AI Copilot   │  │
│  │ • Identity       │     │ • Ollama            │     │ • Emulation    │  │
│  │   Providers      │     │ • Prometheus        │     │   Controller   │  │
│  └────────┬─────────┘     │ • Grafana           │     └───────┬────────┘  │
│           │               │ • Loki              │             │           │
│           │               │ • Falco             │             ▼           │
│           │               │ • OTel Collector    │    ┌────────────────┐  │
│           │               └─────────┬───────────┘    │   SIMULATORS   │  │
│           │                         │                │                │  │
│           ▼                         ▼                │ • Auth Sim     │  │
│  ┌──────────────────┐     ┌─────────────────────┐   │ • Workload Sim │  │
│  │  ANALYST         │     │   OBSERVABILITY     │   │ • DNS Sim      │  │
│  │  CONSOLE         │     │                     │   │ • Traffic Sim  │  │
│  │                  │     │ • Metrics           │   │ • Target API   │  │
│  │ • Dashboard      │     │ • Logs              │   └────────────────┘  │
│  │ • Alert Queue    │     │ • Traces            │                       │
│  │ • Incidents      │     │ • Alerts            │                       │
│  │ • Approvals      │     │ • Health            │                       │
│  │ • Lab Control    │     └─────────────────────┘                       │
│  └──────────────────┘                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Telemetry & Event Pipeline

**OpenTelemetry Collector** - Normalizes and routes telemetry:
- Receives: OTLP (gRPC/HTTP), Prometheus, Jaeger, Zipkin
- Processes: Batch, Memory Limiter, Tail Sampling, Transform
- Exports: Prometheus, Loki, Tempo, Redpanda/Kafka

**Fluent Bit** - Container and Kubernetes log collection:
- Tail input from container log files
- Kubernetes metadata enrichment
- Parse: JSON, Regex, CRI
- Output: Loki, Redpanda

**Falco** - Runtime security events:
- Kernel-level syscall monitoring
- Custom rules for Kubernetes
- Output: Redpanda, gRPC, WebSocket

**Prometheus** - Metrics collection:
- Service metrics, Node exporter, kube-state-metrics
- AlertManager for alert routing
- Remote write for long-term storage

**Loki** - Log aggregation:
- Label-based indexing
- LogQL query language
- Grafana integration

**Redpanda** - Event backbone:
- Kafka-compatible API
- Persistent, replicated topics
- Schema registry support
- Low latency, high throughput

### 2. Detection & Correlation Engine

**Detection Engine** (`services/detection-engine`):
- Consumes normalized events from Redpanda
- Evaluates versioned YAML detection rules
- MITRE ATT&CK mapping for each rule
- Correlation engine for multi-event patterns:
  - Repeated failed authentication
  - Anomalous privileged container events
  - Service account token access anomalies
  - Synthetic DNS volume anomalies
  - East-west traffic anomalies
  - Container image policy violations
- Outputs: Alerts with severity, confidence, evidence, MITRE mapping
- Stores: Alerts, incidents, timelines in PostgreSQL

**Rule Format** (YAML):
```yaml
id: "DET-001"
name: "Repeated Failed Authentication"
description: "Multiple failed login attempts from same source"
severity: high
confidence: 0.85
mitre:
  - T1110.001
  - T1110.003
correlation:
  window: 300s
  threshold: 5
  group_by: ["source_ip", "user"]
condition: |
  count(event.type == "auth_failed") by source_ip, user > 5
```

### 3. CPU-Only AI Security Copilot

**AI Copilot** (`services/ai-copilot`):
- Ollama for local CPU-only LLM inference
- Compact models: `llama3.2:1b`, `phi3:mini`, `qwen2:0.5b`
- Sentence transformers for embeddings: `all-MiniLM-L6-v2` (384-dim)
- Qdrant vector database for RAG
- Safety controls:
  - PII/secret/IP/token redaction before inference
  - Prompt injection defense (untrusted document handling)
  - Fixed system policy boundaries
  - Citation requirement for all responses
  - "Insufficient evidence" fallback

**Indexed Knowledge Base**:
- Generated alerts and incidents
- Evidence artifacts
- Runbooks and policies
- Lab scenario definitions
- Platform documentation

**Features**:
- Incident timeline summarization
- Alert triage with citations
- Containment runbook recommendation
- Natural language search over security events
- Post-incident report generation

### 4. Response Orchestration

**Response Orchestrator** (`services/response-orchestrator`):
- PostgreSQL-backed durable workflow state machine
- Approval-gated response playbooks:
  1. Quarantine lab workload (NetworkPolicy)
  2. Scale suspected deployment to zero
  3. Revoke test service account binding
  3. Create incident ticket with evidence
- All actions:
  - Operate only in `aegisforge-lab` namespace by default
  - Enforce allowlist
  - Support dry-run mode
  - Require explicit approval
  - Create immutable audit logs
  - Support rollback
  - Include approver identity and timestamp
- Reliability: Idempotency keys, exponential backoff, circuit breakers, DLQ, failure alerting

### 5. Safe Threat Emulation Lab

**Simulators** (namespace-local, benign only):
- `target-api`: Demo API with no secrets
- `auth-simulator`: Controlled failed/abnormal login patterns
- `workload-simulator`: Process execution, policy violations
- `dns-simulator`: Synthetic DNS anomaly events
- `traffic-simulator`: Namespace-local HTTP patterns
- `emulation-controller`: Schedules scenarios after admin approval

**Prohibited Activities**:
- Internet targeting
- Host escape
- Credential collection
- Exploit execution
- Payload delivery
- Persistence
- Destructive operations
- Actual privilege escalation

### 6. Analyst Console

**Frontend** (`web/analyst-console`):
- React 18 + TypeScript + Vite + Tailwind CSS
- FastAPI gateway with OIDC auth
- Role-based access: Viewer, Analyst, Incident Commander, Administrator
- Pages:
  1. Executive Dashboard (MTTD, MTTR, open incidents, alert volume, response success rate)
  2. Alert Queue (severity, confidence, MITRE mapping, assets, evidence)
  3. Incident Timeline (correlated events, cited AI summaries)
  4. Response Approval Queue (dry-run results, rollback plan, audit data)
  4. Lab Scenario Launcher (admin only)
  5. Detection Rule Management (versioned)
  6. Platform Health Dashboard

## Data Flow

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  SIMULATORS  │────▶│  REDPANDA   │────▶│  DETECTION   │────▶│  POSTGRES   │
│  + FALCO     │     │  (EVENTS)   │     │  ENGINE      │     │  (ALERTS/   │
│  + OTel      │     │             │     │              │     │   INCIDENTS)│
└──────────────┘     └─────────────┘     └──────┬───────┘     └─────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  ANALYST     │◀───│  API GATEWAY │◀───│  AI COPILOT  │◀───│  QDRANT     │
│  CONSOLE     │     │              │     │  (RAG)       │     │  (VECTORS)  │
└──────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
       │                  │                    │
       ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE ORCHESTRATOR                        │
│  • Approval Queue  • Dry-Run  • Rollback  • Audit Logs         │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│              KUBERNETES API (NetworkPolicy, Scale, SA)          │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Docker Compose (Development)
- All services as containers on single host
- Shared Docker network
- Named volumes for persistence
- Resource limits per service

### Kubernetes (Production)
- Helm chart with values overlays (dev/prod)
- Namespace isolation: `aegisforge`, `aegisforge-lab`, `monitoring`
- RBAC: Least-privilege ServiceAccounts
- NetworkPolicies: Default deny, explicit allow
- Resource quotas, limits, requests
- PodDisruptionBudgets, HPA
- External Secrets Operator for secrets
- Prometheus Operator for monitoring

## Security Boundaries

| Boundary | Controls |
|----------|----------|
| Network | Default deny NetworkPolicies, mTLS via Istio/Linkerd (optional) |
| Identity | OIDC/OAuth2 via Keycloak, JWT with short expiry, refresh tokens |
| Runtime | Non-root containers, read-only rootfs, dropped capabilities, seccomp |
| Data | Encryption at rest (PostgreSQL, MinIO), TLS in transit, PII redaction |
| Supply Chain | SBOM (Syft), Image signing (Cosign), Trivy scanning, Admission control |
| AI Safety | Redaction, citation enforcement, prompt injection defense, no external calls |

## Scaling Strategy

| Component | Scaling Approach |
|-----------|------------------|
| API Gateway | HPA (CPU > 70%, RPS > 1000) |
| Detection Engine | Partition by topic partition, max replicas = partitions |
| Response Orchestrator | Single leader, passive replicas |
| AI Copilot | Vertical scaling (CPU/RAM), model sharding |
| Simulators | Fixed replicas, controlled by emulation-controller |
| Redpanda | Add brokers, increase partitions |
| PostgreSQL | Read replicas, connection pooling (PgBouncer) |
| Qdrant | Horizontal sharding, replica sets |

## Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Redpanda broker down | Prometheus alert, ISR shrink | ISR replication, min.insync.replicas=2 |
| PostgreSQL primary down | Patroni/HAProxy, health checks | Automatic failover, read replicas |
| Qdrant node down | Health check, cluster status | Replica sets, shard replication |
| Ollama OOM | Memory metrics, container restart | Model unloading, swap, smaller models |
| Network partition | Kubernetes readiness, network policies | PodDisruptionBudgets, multi-AZ |
| AI hallucination | Citation validation, confidence threshold | Human-in-the-loop, evidence verification |

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| Language | Python 3.12, TypeScript, Go 1.22 |
| API | FastAPI, Pydantic v2 |
| Database | PostgreSQL 16, SQLAlchemy 2, Alembic |
| Messaging | Redpanda (Kafka API) |
| Vector DB | Qdrant |
| Object Storage | MinIO (S3-compatible) |
| AI Inference | Ollama (CPU) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Search | Qdrant HNSW |
| Frontend | React 18, TypeScript, Vite, Tailwind |
| Auth | Keycloak (OIDC), JWT |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, Tempo |
| Runtime Security | Falco |
| CI/CD | GitHub Actions |
| Packaging | Docker, Helm |
| Infrastructure | Kind (dev), EKS/GKE/AKS (prod) |