# AegisForge Threat Model

## Methodology

This threat model follows the STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and is aligned with MITRE ATT&CK framework.

## System Assets

| Asset | Classification | Description |
|-------|----------------|-------------|
| Security Events | Confidential | Raw telemetry from simulators, Falco, OTel |
| Alerts & Incidents | Confidential | Detection results, correlations, evidence |
| Evidence Artifacts | Highly Confidential | Immutable logs, PCAPs, memory dumps in MinIO |
| Detection Rules | Internal | YAML rules with MITRE mappings |
| AI Knowledge Base | Confidential | Indexed alerts, runbooks, policies |
| Response Actions | Confidential | Approval records, audit logs, rollback plans |
| User Credentials | Highly Confidential | JWT tokens, OIDC secrets, API keys |
| Infrastructure Config | Internal | NetworkPolicies, RBAC, resource definitions |

## Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNET / EXTERNAL                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DMZ / INGRESS                               │
│  • API Gateway (TLS termination, rate limiting, WAF)           │
│  • Keycloak (OIDC provider)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM SERVICES ZONE                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │API Gateway│ │Detection │ │ Response │ │ AI       │          │
│  │          │ │ Engine   │ │ Orch.    │ │ Copilot  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │Emulation │ │ Simulators│ │ Analyst  │                        │
│  │Controller │ │          │ │ Console  │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER ZONE                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │PostgreSQL│ │ Redpanda │ │ Qdrant   │ │ MinIO    │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY ZONE                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Prometheus│ │ Grafana  │ │ Loki     │ │ Falco    │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## STRIDE Analysis

### Spoofing

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Impersonate API caller | API Gateway | Medium | High | JWT validation, mTLS, rate limiting, IP allowlist |
| Spoof simulator events | Redpanda | Low | Medium | Producer authentication, schema validation |
| Fake AI responses | AI Copilot | Low | High | Citation verification, confidence thresholds |
| Impersonate admin | Keycloak | Medium | Critical | MFA, short-lived tokens, session binding |
| Spoof approval request | Response Orchestrator | Medium | High | Signed approval requests, audit trail |

### Tampering

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Modify detection rules | Detection Engine | Medium | High | GitOps, signed rules, versioning, RBAC |
| Alter alert severity | Detection Engine/DB | Medium | High | Immutable audit logs, WORM storage |
| Modify evidence artifacts | MinIO | Low | Critical | Versioning, SHA256 hashes, signed URLs |
| Alter AI knowledge base | Qdrant/PostgreSQL | Medium | High | Immutable embeddings, checksums |
| Inject malicious prompts | AI Copilot | Medium | High | Input sanitization, prompt injection defense |
| Modify NetworkPolicies | K8s API | Medium | High | RBAC, admission controllers, dry-run |

### Repudiation

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Deny approval action | Response Orchestrator | Low | High | Immutable audit logs, digital signatures |
| Deny rule modification | Detection Engine | Low | Medium | Git commit signing, audit logs |
| Delete evidence | MinIO | Low | Critical | Versioning, lifecycle policies, legal hold |
| Deny simulator config | Emulation Controller | Low | Medium | Audit logs, approval workflow |

### Information Disclosure

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Event data exfiltration | Redpanda/PostgreSQL | Medium | High | TLS, encryption at rest, network policies |
| Evidence artifact leak | MinIO | Low | Critical | Signed URLs, short expiry, audit logs |
| PII in AI context | AI Copilot | Medium | High | Automatic redaction, no external calls |
| Credential leak in logs | All services | Medium | High | Structured logging, secret redaction |
| Rule/Incident data leak | API Gateway | Medium | High | RBAC, field-level permissions |
| Model extraction | AI Copilot | Low | Medium | Rate limiting, query logging |

### Denial of Service

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Event flood | Redpanda | Medium | High | Partitioning, retention, consumer groups |
| Alert storm | Detection Engine | Medium | High | Rate limiting, deduplication, suppression |
| AI inference overload | Ollama | Medium | High | Queue limits, model unloading, timeouts |
| DB connection exhaustion | PostgreSQL | Medium | High | PgBouncer, connection limits, timeouts |
| K8s API saturation | K8s API | Low | High | Rate limiting, priority classes |
| Resource exhaustion | All containers | Medium | High | Resource limits, OOM kill priority |

### Elevation of Privilege

| Threat | Target | Likelihood | Impact | Mitigation |
|--------|--------|------------|--------|------------|
| Container escape | All containers | Low | Critical | Non-root, read-only fs, dropped caps, seccomp |
| K8s RBAC escalation | K8s RBAC | Low | Critical | Least privilege, no cluster-admin, admission control |
| Service account theft | K8s SA tokens | Medium | High | Token rotation, bound tokens, workload identity |
| Network policy bypass | CNI | Low | High | Calico/Cilium, default deny, egress controls |
| AI policy bypass | AI Copilot | Medium | High | Fixed system prompts, input validation |
| Host access via volumes | All containers | Low | Critical | No hostPath, read-only mounts |

## Attack Trees

### Compromise Detection Engine
```
Root: Attacker modifies detection logic
├── Direct rule modification
│   ├── Git repo compromise → Signed commits, branch protection
│   ├── API endpoint abuse → RBAC, input validation
│   └── ConfigMap tampering → Immutable ConfigMaps, admission control
├── Event injection
│   ├── Redpanda producer spoofing → SASL/SCRAM auth
│   ├── Schema bypass → Schema registry validation
│   └── Consumer group hijack → Consumer group authorization
└── Model poisoning
    ├── Training data injection → Immutable embeddings
    ├── Prompt injection → Input sanitization, fixed prompts
    └── Adversarial examples → Confidence thresholds
```

### Compromise Response Orchestrator
```
Root: Attacker executes unauthorized containment
├── Approval bypass
│   ├── API abuse → RBAC, approval workflow
│   ├── Approval forgery → Digital signatures
│   └── Dry-run confusion → Explicit dry-run flag, separate endpoints
├── Action injection
│   ├── K8s API abuse → RBAC, impersonation prevention
│   ├── NetworkPolicy injection → Admission validation
│   └── Scale/SA manipulation → Allowlist enforcement
└── Audit tampering
    ├── Log deletion → Immutable audit logs, WORM
    ├── Log modification → Append-only, hash chaining
    └── Timestamp manipulation → NTP, trusted time source
```

### AI Copilot Compromise
```
Root: Attacker extracts sensitive data or injects malicious behavior
├── Data extraction
│   ├── Prompt injection → Input sanitization, delimiters
│   ├── Context stuffing → Token limits, chunking
│   └── Training data extraction → No training on prod data
├── Behavior manipulation
│   ├── Prompt injection → Fixed system prompt, instruction hierarchy
│   ├── Retrieval poisoning → Source verification, checksums
│   └── Jailbreak attempts → Safety filters, refusal patterns
└── Infrastructure
    ├── Model theft → No model weights exposure
    ├── Resource exhaustion → Rate limits, timeouts
    └── Side channels → Constant-time operations
```

## Residual Risks

| Risk | Likelihood | Impact | Acceptance | Monitoring |
|------|------------|--------|------------|------------|
| Zero-day in Ollama | Low | Medium | Accepted | CVE scanning, version pinning |
| Prompt injection bypass | Medium | High | Mitigated | Continuous testing, red teaming |
| Supply chain attack | Low | Critical | Mitigated | SBOM, signing, scanning |
| Insider threat | Low | High | Accepted | Audit logs, separation of duties |
| K8s zero-day | Low | Critical | Accepted | Cluster hardening, updates |
| Data remanence | Low | Medium | Accepted | Encrypted volumes, secure deletion |

## Compliance Mapping

| Control | Standard | Implementation |
|---------|----------|----------------|
| AC-2 | NIST 800-53 | RBAC, least privilege |
| AC-3 | NIST 800-53 | Attribute-based access |
| AC-6 | NIST 800-53 | Least privilege enforcement |
| AU-2 | NIST 800-53 | Comprehensive audit logging |
| AU-6 | NIST 800-53 | Audit log review |
| AU-9 | NIST 800-53 | Audit log protection |
| CM-7 | NIST 800-53 | Least functionality |
| IA-2 | NIST 800-53 | Multi-factor authentication |
| IA-5 | NIST 800-53 | Authenticator management |
| SC-8 | NIST 800-53 | TLS 1.3 everywhere |
| SC-13 | NIST 800-53 | Cryptographic protection |
| SI-3 | NIST 800-53 | Malware protection (Falco) |
| SI-4 | NIST 800-53 | System monitoring |
| SI-7 | NIST 800-53 | Software integrity |

## Residual Risk Acceptance

The following risks are formally accepted with management approval:

1. **Zero-day vulnerabilities in base images** - Mitigated by daily Trivy scanning, automated rebuilds, distroless images
2. **Advanced persistent threats targeting AI** - Accepted with continuous red teaming, prompt injection testing
3. **Insider threat with admin access** - Accepted with separation of duties, dual-control approvals, comprehensive audit
4. **Kubernetes zero-day** - Accepted with cluster hardening, CIS benchmarks, rapid patching SLA

---

*Document Version: 1.0*
*Last Updated: 2024*
*Classification: Internal - Security Sensitive*