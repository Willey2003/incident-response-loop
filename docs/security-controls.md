# AegisForge Security Controls

## Overview

This document describes the security controls implemented across the AegisForge platform to ensure defense-in-depth, least privilege, and compliance with security best practices.

## Security Control Categories

### 1. Identity & Access Management

#### Authentication
- **OIDC/OAuth2**: Keycloak as identity provider
- **JWT Tokens**: Short-lived (60 min) access tokens, 7-day refresh tokens
- **MFA**: Required for admin roles, optional for analysts
- **Session Management**: Secure cookies, HttpOnly, SameSite=Strict
- **Token Revocation**: Immediate revocation on logout, password change, role change

#### Authorization (RBAC)
| Role | Permissions |
|------|-------------|
| Viewer | Read-only: dashboards, alerts, incidents |
| Analyst | View + acknowledge alerts, create incidents, search |
| Incident Commander | All Analyst + approve responses, create tickets, run scenarios |
| Administrator | All + user management, system config, lab control |

#### Service Accounts
- Each service has dedicated Kubernetes ServiceAccount
- Minimal permissions via Role/RoleBinding (namespace-scoped)
- No ClusterRoles except for cluster-level operators
- Automated token rotation every 24 hours

### 2. Network Security

#### Network Policies
```yaml
# Default deny-all in aegisforge namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: aegisforge
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### Service-to-Service Communication
- mTLS via Istio/Linkerd (production) or manual certs (dev)
- Service mesh for traffic encryption, observability, auth
- Explicit allow rules for required service communication

#### Egress Controls
- Default deny egress
- Explicit allow for:
  - PostgreSQL (5432)
  - Redpanda (9092)
  - Qdrant (6333)
  - MinIO (9000)
  - Ollama (11434)
  - External: OS package repos, container registries (via proxy)

#### Ingress Controls
- Ingress controller with WAF rules
- Rate limiting: 1000 req/min per IP
- TLS 1.3 only
- HSTS, CSP, X-Frame-Options headers

### 3. Container Security

#### Runtime Hardening
```dockerfile
# All service Dockerfiles
FROM python:3.12-slim AS runtime
RUN groupadd -r -g 1000 appuser && useradd -r -g appuser -u 1000 appuser
USER appuser
WORKDIR /app
# Read-only root filesystem
RUN chmod -R a-w /app
```

#### Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

#### Image Security
- **Base Images**: Distroless, Alpine, or minimal slim variants
- **Vulnerability Scanning**: Trivy on every build, daily scheduled scans
- **Image Signing**: Cosign keyless signing, verification in admission controller
- **SBOM**: Syft-generated SPDX/CycloneDX SBOMs for every image
- **Admission Control**: Kyverno/OPA policies block unsigned, vulnerable images

### 4. Data Protection

#### Encryption at Rest
| Data Store | Encryption |
|------------|------------|
| PostgreSQL | Transparent Data Encryption (TDE), pgcrypto for sensitive columns |
| Redpanda | Volume encryption (LUKS) + TLS in transit |
| Qdrant | Volume encryption (LUKS) |
| MinIO | SSE-S3 (AES-256), KMS integration |
| Redis | TLS, optional encryption at rest |
| Persistent Volumes | CSI driver encryption (LUKS) |

#### Encryption in Transit
- **TLS 1.3** everywhere (minimum TLS 1.2)
- **mTLS** between all services (Istio/Linkerd)
- **Certificate Management**: cert-manager with Let's Encrypt or internal CA
- **Certificate Rotation**: Automated 90-day rotation

#### Secrets Management
- **Development**: `.env` files (gitignored)
- **Production**: External Secrets Operator + HashiCorp Vault / AWS Secrets Manager / Azure Key Vault
- **Kubernetes Secrets**: Only for non-sensitive config; sensitive data in Vault
- **Key Rotation**: Automated 90-day rotation for encryption keys
- **Key Hierarchy**: Master key in HSM/KMS → Data encryption keys → Data

#### Data Classification & Handling
| Classification | Examples | Controls |
|----------------|----------|----------|
| Public | Documentation, public dashboards | Standard access |
| Internal | Config, metrics, non-sensitive logs | RBAC, audit |
| Confidential | Alerts, incidents, evidence | Encryption, RBAC, audit |
| Highly Confidential | Credentials, keys, evidence artifacts | Encryption, RBAC, audit, DLP |

#### PII/Secret Redaction
- **Automatic Redaction**: Before AI processing, logging, storage
- **Patterns**: API keys, JWTs, passwords, IPs, emails, SSH keys, credit cards
- **Custom Patterns**: Configurable via regex
- **Audit**: All redactions logged

### 5. Supply Chain Security

#### Build Pipeline Security
```yaml
# GitHub Actions workflow
- name: Build & Scan
  uses: docker/build-push-action@v5
  with:
    provenance: true
    sbom: true
    
- name: Vulnerability Scan
  uses: aquasecurity/trivy-action@master
  with:
    severity: HIGH,CRITICAL
    exit-code: 1
    
- name: Sign Image
  uses: sigstore/cosign-installer@v3
  with:
    cosign-version: latest
    
- name: Sign
  run: cosign sign --yes $IMAGE
```

#### Dependency Management
- **Renovate/Dependabot**: Automated PRs for updates
- **License Scanning**: FOSSA/Scancode for license compliance
- **Vulnerability Database**: NVD, GitHub Advisory, OSV
- **Allowlist**: Approved licenses only (Apache-2.0, MIT, BSD-3)

#### SBOM Generation
```bash
# Every build
syft $IMAGE -o spdx-json=sbom.spdx.json
syft $IMAGE -o cyclonedx-json=sbom.cdx.json
```

#### Image Signing & Verification
```bash
# Sign
cosign sign --yes $IMAGE

# Verify in admission controller
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
spec:
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["pods"]
  validations:
  - expression: "object.spec.containers.all(c, c.image.startsWith('docker.io/') || c.image.startsWith('ghcr.io/') || c.image.startsWith('registry.example.com/'))"
    message: "Image must be from approved registry"
```

### 6. Runtime Security

#### Falco Rules
```yaml
# Custom Falco rules for AegisForge
- rule: AegisForge Unexpected Network Connection
  desc: Detect unexpected outbound connections
  condition: >
    evt.type = connect and
    fd.sockfamily = AF_INET and
    not container.image.repository in (allowed_images)
  output: "Unexpected connection from %container.name to %fd.rip"
  priority: WARNING
  tags: [network, aegisforge]

- rule: AegisForge Privilege Escalation Attempt
  desc: Detect privilege escalation in containers
  condition: >
    evt.type in (setuid, setgid, capset) and
    not user.name in (root, appuser)
  output: "Privilege escalation attempt by %user.name in %container.name"
  priority: CRITICAL
  tags: [privilege, aegisforge]
```

#### Admission Control
```yaml
# Kyverno policy: Require security context
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-security-context
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-non-root
    match:
      any:
      - resources:
          kinds: ["Pod"]
    validate:
      message: "Container must run as non-root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
              allowPrivilegeEscalation: false
              capabilities:
                drop: ["ALL"]
```

### 7. Observability Security

#### Audit Logging
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "response_action_executed",
  "actor": "incident-commander-1",
  "action": "quarantine_workload",
  "resource_type": "NetworkPolicy",
  "resource_id": "quarantine-webapp-20240115-103000",
  "namespace": "aegisforge-lab",
  "outcome": "success",
  "details": {
    "dry_run": false,
    "target_pod": "webapp-7b9c5f",
    "approver": "incident-commander-1",
    "approval_id": "appr-abc123"
  },
  "ip_address": "10.0.1.50",
  "user_agent": "AegisForge-Console/1.0",
  "correlation_id": "corr-abc123def456"
}
```

#### Log Integrity
- **Immutable Logs**: Loki with retention policies
- **Log Forwarding**: SIEM integration (Splunk, Elastic, etc.)
- **Log Signing**: Cryptographic signing of audit logs
- **Retention**: 1 year hot, 7 years cold

### 8. Compliance Mapping

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

### 9. Security Testing

#### Continuous Testing
```yaml
# GitHub Actions
- name: SAST
  uses: github/super-linter@v5
  
- name: Container Scan
  uses: aquasecurity/trivy-action@master
  with:
    severity: HIGH,CRITICAL
    
- name: Dependency Scan
  run: pip-audit && npm audit --audit-level=high
  
- name: IaC Scan
  uses: aquasecurity/tfsec-action@v1
```

#### Penetration Testing
- **Quarterly**: External penetration test
- **Monthly**: Internal red team exercise
- **Continuous**: Automated DAST in staging

#### Red Team Exercises
- **Scenario**: Simulated attacker with internal access
- **Objectives**: Test detection, response, containment
- **Scope**: aegisforge-lab namespace only
- **Reporting**: Findings tracked as incidents

### 10. Incident Response Security

#### Evidence Handling
- **Chain of Custody**: SHA256 hashes, signed evidence packages
- **Immutable Storage**: MinIO with versioning, legal hold
- **Access Control**: Role-based, audit logged
- **Retention**: 7 years for evidence, 1 year for logs

#### Communication Security
- **Internal**: Encrypted channels (Signal, Mattermost with E2EE)
- **External**: PGP-encrypted email
- **War Room**: Dedicated secure channel per incident

---

*Document Version: 1.0*
*Classification: Internal - Security Sensitive*
*Review Cycle: Quarterly*