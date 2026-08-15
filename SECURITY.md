# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in AegisForge, please report it responsibly.

### Reporting Process

1. **Do not create a public issue** for security vulnerabilities
2. Email us at **security@aegisforge.example.com** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. We will acknowledge receipt within 48 hours
4. We will provide a timeline for fix within 5 business days
4. We will coordinate disclosure timeline with you

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact
- Any proof-of-concept code (if applicable)
- Suggested remediation (if known)

## Security Architecture

### Defense in Depth

AegisForge implements multiple layers of security:

1. **Network Security**
   - Default deny NetworkPolicies
   - mTLS between all services
   - Egress controls for external access

2. **Identity & Access**
   - OIDC/OAuth2 with Keycloak
   - RBAC with least privilege
   - Short-lived JWT tokens (60 min)
   - MFA for admin roles

3. **Runtime Security**
   - Falco runtime monitoring
   - Non-root containers
   - Read-only root filesystems
   - Dropped capabilities
   - Seccomp profiles

4. **Data Protection**
   - TLS 1.3 everywhere
   - Encryption at rest (PostgreSQL, MinIO, Qdrant)
   - PII/secret redaction before AI processing
   - Immutable evidence storage

5. **Supply Chain Security**
   - SBOM generation (Syft)
   - Image signing (Cosign)
   - Vulnerability scanning (Trivy)
   - Dependency scanning (Dependabot)

### AI Safety Controls

The AI Copilot includes multiple safety layers:

- **Prompt Injection Defense**: Fixed system prompts, untrusted document handling
- **Citation Requirements**: All AI outputs must cite evidence
- **Redaction Pipeline**: Automatic PII/secret/IP/token redaction
- **Evidence Verification**: AI outputs must cite source evidence
- **Confidence Scoring**: Confidence scores on all outputs
- **Insufficient Evidence Fallback**: "Insufficient evidence to determine this"
- **No External Calls**: All inference runs locally on CPU

### Response Orchestration Safety

- **Approval Gates**: All actions require explicit approval
- **Dry-run Mode**: Preview actions before execution
- **Allowlist Enforcement**: Only approved resources can be affected
- **Rollback Capability**: Every action has rollback plan
- **Audit Trail**: Immutable audit logs for all actions
- **Circuit Breakers**: Automatic halt on repeated failures

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

## Security Testing

### Continuous Testing

- **Daily**: Container image scanning (Trivy)
- **Daily**: Dependency scanning (Dependabot, pip-audit, govulncheck)
- **Weekly**: SAST analysis (Semgrep, CodeQL)
- **Monthly**: Penetration testing (internal)
- **Quarterly**: External penetration test

### Automated Testing in CI

```yaml
# GitHub Actions
- name: SAST
  uses: github/super-linter@v5

- name: Container Scan
  uses: aquasecurity/trivy-action@master
  with:
    severity: HIGH,CRITICAL

- name: Dependency Scan
  run: |
    pip-audit
    npm audit --audit-level=high
    govulncheck ./...
    gosec ./...
```

### Penetration Testing

- **Quarterly**: External penetration test
- **Monthly**: Internal red team exercise
- **Continuous**: Automated DAST in staging

### Red Team Exercises

- **Scenario**: Simulated attacker with internal access
- **Objectives**: Test detection, response, containment
- **Scope**: aegisforge-lab namespace only
- **Reporting**: Findings tracked as incidents

## Incident Response Security

### Evidence Handling

- **Chain of Custody**: SHA256 hashes, signed evidence packages
- **Immutable Storage**: MinIO with versioning, legal hold
- **Access Control**: Role-based, audit logged
- **Retention**: 7 years for evidence, 1 year for logs

### Communication Security

- **Internal**: Encrypted channels (Signal, Mattermost with E2EE)
- **External**: PGP-encrypted email
- **War Room**: Dedicated secure channel per incident

## Vulnerability Management

### Patch Management

- **Critical**: Patch within 24 hours
- **High**: Patch within 72 hours
- **Medium**: Patch within 7 days
- **Low**: Patch within 30 days

### Dependency Management

- **Go**: `go vet`, `gosec`, `govulncheck` in CI
- **Python**: `bandit`, `safety`, `pip-audit` in CI
- **Container**: `trivy` scans on every build

### Supply Chain

- **SBOM generation** (Syft) on release
- **Artifact signing** (Cosign) on release
- **Pin dependencies** with lock files (`go.sum`, `uv.lock`)
- **Renovate/Dependabot** for automated updates

## Security Contacts

- **Security Team**: security@aegisforge.example.com
- **PGP Key**: [Available on keyserver](https://keyserver.ubuntu.com/pks/lookup?search=0xXXXXXXXXXXXXXXXX&fingerprint=on&op=vindex)
- **Emergency**: +1-XXX-XXX-XXXX (24/7)

## Responsible Disclosure

We follow [Coordinated Vulnerability Disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure) principles:

1. Private disclosure to security@aegisforge.example.com
2. Acknowledgment within 48 hours
3. Regular updates every 5 business days
4. Coordinated public disclosure after fix deployment
4. Credit given to reporter (unless anonymous requested)

## Security Hall of Fame

We recognize researchers who responsibly disclose vulnerabilities:

- [Researcher names and affiliations would be listed here]

---

*This security policy is reviewed quarterly. Last updated: 2024-01-15*