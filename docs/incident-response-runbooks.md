# AegisForge Incident Response Runbooks

## Overview

This document contains standardized runbooks for incident response. Each runbook is versioned, mapped to MITRE ATT&CK techniques, and designed for approval-gated execution with dry-run and rollback capabilities.

## Runbook Format

```yaml
id: RB-001
name: "Quarantine Compromised Workload"
version: "1.2.0"
description: "Isolate a compromised pod/workload using NetworkPolicy"
severity: high
mitre_techniques:
  - T1021.001  # Remote Services: Remote Desktop Protocol
  - T1021.002  # Remote Services: SMB/Windows Admin Shares
  - T1570      # Lateral Tool Transfer
trigger_conditions:
  - alert.severity IN ["critical", "high"]
  - alert.mitre_techniques INTERSECTS ["T1021.*", "T1570"]
  - incident.status IN ["open", "investigating"]
approval_required: true
dry_run_supported: true
rollback_supported: true
allowlist_required: true
namespace: aegisforge-lab
max_concurrent: 3
timeout_seconds: 300
```

## Runbooks

### RB-001: Quarantine Compromised Workload

**Description**: Apply a deny-all NetworkPolicy to isolate a compromised pod from all network traffic.

**MITRE ATT&CK**: T1021.001, T1021.002, T1570, T1021.003, T1021.004

**Trigger Conditions**:
- Alert severity: critical or high
- MITRE techniques: T1021.*, T1570
- Incident status: open or investigating
- Target in aegisforge-lab namespace

**Dry Run**:
1. Generate NetworkPolicy YAML without applying
2. Simulate network connectivity impact
3. Return expected blocked connections

**Execution**:
```bash
# 1. Generate NetworkPolicy
cat <<EOF | kubectl apply --dry-run=client -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine-{pod-name}-{timestamp}
  namespace: {namespace}
  labels:
    aegisforge/quarantine: "true"
    aegisforge/incident-id: "{incident_id}"
spec:
  podSelector:
    matchLabels:
      app: {target_app}
  policyTypes:
  - Ingress
  - Egress
  # Empty rules = deny all
  ingress: []
  egress: []
EOF

# 2. Apply (after approval)
kubectl apply -f quarantine-policy.yaml

# 3. Verify isolation
kubectl exec -n {namespace} {pod} -- nc -zv {external_target} 80 2>&1 || echo "Blocked as expected"
```

**Rollback**:
```bash
kubectl delete networkpolicy quarantine-{pod-name}-{timestamp} -n {namespace}
```

**Verification**:
- NetworkPolicy exists and applied
- Target pod cannot make ingress/egress connections
- Audit log entry created

**Rollback Time**: < 30 seconds

---

### RB-002: Scale Suspicious Deployment to Zero

**Description**: Scale a suspicious deployment to zero replicas to stop malicious activity.

**MITRE ATT&CK**: T1499.001, T1499.002, T1499.003, T1529

**Trigger Conditions**:
- Alert severity: critical or high
- MITRE techniques: T1499.*, T1529
- Deployment in aegisforge-lab namespace
- Deployment has > 0 replicas

**Dry Run**:
```bash
# Show current replica count and expected scale
kubectl get deployment {deployment} -n {namespace} -o jsonpath='{.spec.replicas}'
# Expected: scale from {current} to 0
```

**Execution**:
```bash
# Scale to zero
kubectl scale deployment {deployment} -n {namespace} --replicas=0

# Verify
kubectl get pods -n {namespace} -l app={deployment} --no-headers | wc -l
# Expected: 0
```

**Rollback**:
```bash
# Restore to original replica count
kubectl scale deployment {deployment} -n {namespace} --replicas={original_count}
```

**Verification**:
- Deployment replicas = 0
- No pods running for deployment
- Audit log entry created

**Rollback Time**: < 60 seconds

---

### RB-003: Revoke Test Service Account Binding

**Description**: Revoke a deliberately created test ServiceAccount binding that may be abused.

**MITRE ATT&CK**: T1650, T1610, T1111

**Trigger Conditions**:
- Alert severity: high or medium
- MITRE techniques: T1650, T1610, T1111
- ServiceAccount in aegisforge-lab namespace
- Binding created by emulation controller (label: aegisforge/test-sa=true)

**Dry Run**:
```bash
# Show bindings to be removed
kubectl get rolebinding,clusterrolebinding -n {namespace} -l aegisforge/test-sa=true -o name
```

**Execution**:
```bash
# Remove test bindings
kubectl delete rolebinding,clusterrolebinding -n {namespace} -l aegisforge/test-sa=true

# Verify
kubectl get rolebinding,clusterrolebinding -n {namespace} -l aegisforge/test-sa=true
# Expected: No resources found
```

**Rollback**:
```bash
# Recreate from stored specification
kubectl apply -f /backups/sa-bindings/{binding_name}.yaml
```

**Verification**:
- No test bindings remain
- Legitimate bindings unaffected
- Audit log entry created

**Rollback Time**: < 30 seconds

---

### RB-004: Create Incident Ticket with Evidence

**Description**: Create a formal incident ticket in external ticketing system with all evidence attached.

**MITRE ATT&CK**: All (documentation)

**Trigger Conditions**:
- Incident status: open
- Incident commander assigned
- Evidence collected

**Dry Run**:
```bash
# Generate ticket payload without submitting
cat <<EOF
{
  "title": "INC-{incident_id}: {title}",
  "description": "{description}",
  "severity": "{severity}",
  "labels": ["security", "incident", "aegisforge"],
  "attachments": [
    {"type": "evidence", "url": "minio://..."},
    {"type": "timeline", "url": "minio://..."},
    {"type": "network_policy", "url": "minio://..."}
  ]
}
EOF
```

**Execution**:
```bash
# Submit to ticketing system (e.g., Jira, ServiceNow, GitHub Issues)
# Via API gateway endpoint
curl -X POST http://api-gateway:8000/api/v1/incidents/{incident_id}/create-ticket \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticket_system": "jira", "project": "SEC"}'
```

**Rollback**:
```bash
# Close ticket or add resolution note
curl -X PUT "https://jira.example.com/rest/api/2/issue/{ticket_key}/transitions" \
  -d '{"transition": {"id": "31"}}'  # Close transition
```

---

### RB-005: Isolate Namespace (Emergency)

**Description**: Complete network isolation of aegisforge-lab namespace for severe incidents.

**MITRE ATT&CK**: T1021.*, T1570, T1499.*

**Trigger Conditions**:
- Multiple critical incidents in same namespace
- Incident commander declares emergency
- Explicit admin approval required

**Execution**:
```bash
# Apply namespace-wide deny-all
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-isolate-aegisforge-lab
  namespace: aegisforge-lab
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress: []
  egress: []
EOF
```

**Rollback**:
```bash
kubectl delete networkpolicy emergency-isolate-aegisforge-lab -n aegisforge-lab
```

**Note**: This is a last-resort measure. Requires dual approval (Incident Commander + Platform Engineer).

---

## Runbook Execution Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RUNBOOK EXECUTION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INCIDENT CREATED                                            │
│     │                                                           │
│     ▼                                                           │
│  2. AUTOMATIC RUNBOOK MATCHING                                 │
│     │  • Match incident to runbooks via trigger_conditions    │
│     ▼                                                           │
│  3. PRESENT MATCHED RUNBOOKS TO INCIDENT COMMANDER             │
│     │  • Show dry-run preview                                  │
│     │  • Show rollback plan                                    │
│     ▼                                                           │
│  4. INCIDENT COMMANDER APPROVES                                │
│     │  • Records approver identity + timestamp                 │
│     ▼                                                           │
│  5. DRY-RUN EXECUTION                                          │
│     │  • Simulate action without applying                      │
│     │  • Show expected impact                                  │
│     ▼                                                           │
│  6. INCIDENT COMMANDER CONFIRMS EXECUTION                      │
│     │  • Records confirmation                                  │
│     ▼                                                           │
│  7. EXECUTE ACTION                                             │
│     │  • Apply NetworkPolicy / Scale / Revoke SA               │
│     │  • Record execution result                               │
│     ▼                                                           │
│  8. VERIFY & MONITOR                                           │
│     │  • Confirm action took effect                            │
│     │  • Monitor for adverse effects                           │
│     ▼                                                           │
│  9. DOCUMENT & CLOSE                                           │
│     │  • Update incident with action results                   │
│     │  • Attach audit logs                                     │
│     ▼                                                           │
│  10. ROLLBACK (IF NEEDED)                                      │
│      │  • Execute rollback plan                                │
│      │  • Verify restoration                                   │
│      ▼                                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Approval Matrix

| Runbook | Approver | Dry Run | Rollback | Max Concurrent |
|---------|----------|---------|----------|----------------|
| RB-001 Quarantine | Incident Commander | Yes | Yes | 3 |
| RB-002 Scale Down | Incident Commander | Yes | Yes | 2 |
| RB-003 Revoke SA | Incident Commander | Yes | Yes | 3 |
| RB-004 Create Ticket | Analyst | Yes | N/A | 5 |
| RB-005 Emergency Isolate | Incident Commander + Platform Engineer | Yes | Yes | 1 |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2024-01-15 | Added RB-005, improved rollback procedures |
| 1.1.0 | 2024-01-10 | Added dry-run support, improved RBAC |
| 1.0.0 | 2024-01-01 | Initial release |

## Testing Runbooks

```bash
# Test all runbooks in dry-run mode
make test-runbooks

# Test specific runbook
make test-runbook RB-001

# Integration test with kind
make test-runbooks-kind
```

## Runbook Development Guidelines

1. **Idempotency**: All actions must be idempotent (safe to retry)
2. **Dry-run first**: Every action must support dry-run
3. **Rollback required**: Every action must have rollback plan
4. **Audit everything**: Every action creates audit log entry
5. **Allowlist enforcement**: Actions only on approved resources
6. **Namespace isolation**: Default to aegisforge-lab
6. **Timeout enforcement**: All actions have max duration
7. **Circuit breaker**: Stop after 3 consecutive failures
8. **Dead letter queue**: Failed actions go to DLQ for review