# AegisForge Operations Runbook

## Overview

This runbook provides operational procedures for running AegisForge in production. It covers routine operations, incident response, and emergency procedures.

## Daily Operations

### Morning Checks (08:00 UTC)

```bash
# 1. Check overall platform health
make deploy-status

# 2. Verify all critical pods running
kubectl get pods -n aegisforge -o wide | grep -v Running

# 3. Check alert volume
curl -s http://prometheus:9090/api/v1/query?query=sum\(rate\(alerts_total\[5m\]\)\) | jq .

# 4. Verify AI Copilot responsiveness
curl -s http://ai-copilot:8003/health | jq .

# 5. Check Redpanda consumer lag
kubectl exec -n aegisforge redpanda-0 -- rpk group describe aegisforge-detection

# 6. Check disk space
kubectl exec -n aegisforge postgres-0 -- df -h /var/lib/postgresql/data
```

### Evening Checks (20:00 UTC)

```bash
# 1. Review open incidents
kubectl exec -n aegisforge deploy/api-gateway -- psql -U aegisforge -d aegisforge -c "SELECT id, title, severity, status, created_at FROM detection.incidents WHERE status IN ('open','investigating') ORDER BY created_at DESC;"

# 2. Check approval queue
kubectl exec -n aegisforge deploy/api-gateway -- psql -U aegisforge -d aegisforge -c "SELECT id, action_type, status, requested_by, created_at FROM response.actions WHERE status='pending' ORDER BY created_at;"

# 3. Verify backup completion
ls -la /backups/postgres/
ls -la /backups/minio/

# 4. Check resource utilization
kubectl top pods -n aegisforge --sort-by=memory
kubectl top nodes
```

## Weekly Operations

### Monday - Security Review
```bash
# 1. Review Trivy scan results
cat /var/log/trivy/scan-$(date +%Y%m%d).json | jq '.Results[] | select(.Vulnerabilities != null) | .Vulnerabilities[] | select(.Severity=="CRITICAL" or .Severity=="HIGH")'

# 2. Review dependency updates
cd /aegisforge && make ci-deps

# 3. Review audit logs for anomalies
kubectl exec -n aegisforge deploy/api-gateway -- psql -U aegisforge -d aegisforge -c "SELECT * FROM audit.logs WHERE timestamp > NOW() - INTERVAL '7 days' AND outcome='failure' ORDER BY timestamp DESC LIMIT 50;"
```

### Wednesday - Performance Review
```bash
# 1. Check detection engine latency
curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(detection_engine_processing_seconds_bucket\[5m\]\)\) | jq .

# 2. Check AI inference latency
curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(ai_copilot_inference_seconds_bucket\[5m\]\)\) | jq .

# 3. Check Redpanda lag
for group in aegisforge-detection aegisforge-response aegisforge-emulation; do
  kubectl exec -n aegisforge redpanda-0 -- rpk group describe $group
done
```

### Friday - Capacity Planning
```bash
# 1. Check storage growth
kubectl exec -n aegisforge postgres-0 -- psql -U aegisforge -d aegisforge -c "SELECT pg_size_pretty(pg_database_size('aegisforge'));"
kubectl exec -n aegisforge minio-0 -- mc admin info minio | grep -A 5 "Total"

# 2. Check Redpanda retention
kubectl exec -n aegisforge redpanda-0 -- rpk topic list | grep -E "security-events|security-alerts"

# 3. Plan scaling for next week
kubectl top nodes --sort-by=memory
```

## Incident Response Procedures

### Alert Triage (P1 - Critical)

**Trigger**: Critical severity alert with confidence > 0.8

**Response Time**: 15 minutes

**Steps**:
```bash
# 1. Acknowledge alert
curl -X POST http://api-gateway:8000/api/v1/alerts/{alert_id}/acknowledge \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignee": "analyst-oncall"}'

# 2. Get alert details with AI summary
curl -X GET http://api-gateway:8000/api/v1/alerts/{alert_id}/summary \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Check correlated events
curl -X GET http://api-gateway:8000/api/v1/alerts/{alert_id}/timeline \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Create incident if warranted
curl -X POST http://api-gateway:8000/api/v1/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alert_ids": ["{alert_id}"], "title": "...", "severity": "critical"}'
```

### Containment Approval (P1)

**Trigger**: Incident requires containment

**Response Time**: 30 minutes for approval

**Steps**:
```bash
# 1. Review dry-run results
curl -X GET http://api-gateway:8000/api/v1/response/actions/{action_id}/dry-run \
  -H "Authorization: Bearer $TOKEN" | jq .

# 2. Review rollback plan
curl -X GET http://api-gateway:8000/api/v1/response/actions/{action_id}/rollback \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Approve action (Incident Commander only)
curl -X POST http://api-gateway:8000/api/v1/response/actions/{action_id}/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approver": "incident-commander", "reason": "Confirmed malicious activity"}'

# 4. Monitor execution
watch -n 5 "curl -s http://api-gateway:8000/api/v1/response/actions/{action_id} -H 'Authorization: Bearer $TOKEN' | jq .status"
```

### Rollback Procedure

```bash
# If containment causes issues
curl -X POST http://api-gateway:8000/api/v1/response/actions/{action_id}/rollback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Containment caused service degradation"}'

# Verify rollback
curl -s http://api-gateway:8000/api/v1/response/actions/{action_id} -H "Authorization: Bearer $TOKEN" | jq .status
```

## Service-Specific Procedures

### Detection Engine

**Restart**:
```bash
kubectl rollout restart deployment/detection-engine -n aegisforge
```

**Reload Rules** (without restart):
```bash
# Rules hot-reload every 5 minutes automatically
# Force reload:
kubectl exec -n aegisforge deploy/detection-engine -- kill -HUP 1
```

**Rule Validation**:
```bash
# Validate rule syntax
kubectl exec -n aegisforge deploy/detection-engine -- python -m detection_engine.rule_validator /etc/aegisforge/rules
```

### Response Orchestrator

**Check Approval Queue**:
```bash
curl -s http://response-orchestrator:8002/api/v1/approvals/pending | jq .
```

**Force Complete Stuck Action**:
```bash
# Only if action stuck in "executing" > 10 min
curl -X POST http://response-orchestrator:8002/api/v1/actions/{action_id}/force-complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "reason": "Manual completion after timeout"}'
```

### AI Copilot

**Check Model Status**:
```bash
curl -s http://ollama:11434/api/tags | jq .
```

**Reload Model**:
```bash
# Unload current model
curl -X POST http://ollama:11434/api/generate -d '{"model": "llama3.2:1b", "keep_alive": 0}'

# Preload model
curl -X POST http://ollama:11434/api/generate -d '{"model": "llama3.2:1b", "keep_alive": -1}'
```

**Clear Vector Cache**:
```bash
curl -X DELETE http://ai-copilot:8003/api/v1/cache
```

**Rebuild Index**:
```bash
curl -X POST http://ai-copilot:8003/api/v1/index/rebuild
```

### Emulation Controller

**List Scenarios**:
```bash
curl -s http://emulation-controller:8004/api/v1/scenarios | jq .
```

**Cancel Running Scenario**:
```bash
curl -X POST http://emulation-controller:8004/api/v1/runs/{run_id}/cancel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Manual cancellation"}'
```

### Simulators

**Pause/Resume Simulator**:
```bash
# Scale to 0 to pause
kubectl scale deployment/auth-simulator --replicas=0 -n aegisforge

# Resume
kubectl scale deployment/auth-simulator --replicas=1 -n aegisforge
```

### Database Operations

**Vacuum/Analyze**:
```bash
kubectl exec -n aegisforge postgres-0 -- psql -U aegisforge -d aegisforge -c "VACUUM ANALYZE;"
```

**Reindex**:
```bash
kubectl exec -n aegisforge postgres-0 -- psql -U aegisforge -d aegisforge -c "REINDEX DATABASE aegisforge;"
```

**Check Long-Running Queries**:
```bash
kubectl exec -n aegisforge postgres-0 -- psql -U aegisforge -d aegisforge -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state != 'idle';
"
```

### Redpanda Operations

**Check Topic Health**:
```bash
kubectl exec -n aegisforge redpanda-0 -- rpk topic list
kubectl exec -n aegisforge redpanda-0 -- rpk topic describe security-events
```

**Rebalance Partitions**:
```bash
kubectl exec -n aegisforge redpanda-0 -- rpk cluster rebalance start
```

### Qdrant Operations

**Check Collection**:
```bash
curl -s http://qdrant:6333/collections/security-knowledge | jq .
```

**Optimize Index**:
```bash
curl -X POST http://qdrant:6333/collections/security-knowledge/index -d '{"hnsw_config": {"m": 16, "ef_construct": 100}}'
```

### MinIO Operations

**Check Bucket Health**:
```bash
mc admin info minio
mc ls minio/aegisforge-evidence --recursive | head -20
```

**Enable Versioning** (if not already):
```bash
mc version enable minio/aegisforge-evidence
mc version enable minio/aegisforge-artifacts
```

## Emergency Procedures

### Complete Platform Outage

```bash
# 1. Check cluster health
kubectl get nodes
kubectl get pods -A | grep -E "(Pending|CrashLoop|Error)"

# 2. Check infrastructure
systemctl status k3s  # or kubelet

# 3. Restart critical infrastructure
kubectl rollout restart deployment/postgres -n aegisforge
kubectl rollout restart statefulset/redpanda -n aegisforge
kubectl rollout restart deployment/qdrant -n aegisforge

# 4. Verify core services
kubectl wait --for=condition=ready pod -l app=postgres -n aegisforge --timeout=120s
```

### Data Corruption

```bash
# 1. Stop writers
kubectl scale deployment/api-gateway --replicas=0 -n aegisforge
kubectl scale deployment/detection-engine --replicas=0 -n aegisforge

# 2. Restore from backup
# PostgreSQL
kubectl exec -i -n aegisforge postgres-0 -- psql -U aegisforge -d aegisforge < /backups/postgres/latest.sql

# MinIO
mc mirror --overwrite /backups/minio/evidence minio/aegisforge-evidence

# 3. Verify integrity
kubectl exec -n aegisforge deploy/api-gateway -- alembic check

# 4. Restart services
kubectl scale deployment/api-gateway --replicas=3 -n aegisforge
kubectl scale deployment/detection-engine --replicas=3 -n aegisforge
```

### Security Breach

```bash
# 1. Isolate namespace
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: isolate-aegisforge
  namespace: aegisforge
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress: []
  egress: []
EOF

# 2. Revoke all tokens
kubectl delete secret -n aegisforge -l type=token

# 3. Rotate secrets
kubectl create secret generic aegisforge-secrets \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=jwt-secret=$(openssl rand -base64 64) \
  -n aegisforge --dry-run=client -o yaml | kubectl apply -f -

# 4. Force re-authentication
kubectl delete pods -n aegisforge -l app=api-gateway
```

## Contact Escalation

| Level | Role | Contact | SLA |
|-------|------|---------|-----|
| L1 | On-Call Analyst | Slack #aegisforge-oncall | 15 min |
| L2 | Senior Analyst | Slack #aegisforge-oncall @senior | 30 min |
| L3 | Platform Engineer | Phone/Slack @platform-lead | 1 hour |
| L4 | Security Lead | Phone/Slack @security-lead | 2 hours |
| L5 | CISO | Phone | 4 hours |

## Useful Commands Quick Reference

```bash
# Port forward for debugging
kubectl port-forward -n aegisforge svc/api-gateway 8000:8000
kubectl port-forward -n aegisforge svc/prometheus 9090:9090
kubectl port-forward -n aegisforge svc/grafana 3001:3000

# Exec into pod
kubectl exec -it -n aegisforge deploy/detection-engine -- bash

# View logs with filter
kubectl logs -n aegisforge -l app=detection-engine --since=1h | grep ERROR

# Scale deployment
kubectl scale deployment/detection-engine --replicas=5 -n aegisforge

# Restart with rollout
kubectl rollout restart deployment/detection-engine -n aegisforge

# Check rollout status
kubectl rollout status deployment/detection-engine -n aegisforge

# Force new replica set
kubectl rollout restart deployment/detection-engine -n aegisforge

# Get events
kubectl get events -n aegisforge --sort-by='.lastTimestamp'

# Describe pod for troubleshooting
kubectl describe pod -n aegisforge -l app=detection-engine

# Get resource usage
kubectl top pods -n aegisforge --containers=true --sort-by=memory

# Check PVC status
kubectl get pvc -n aegisforge

# Check PV
kubectl get pv

# Force delete stuck pod
kubectl delete pod <pod-name> -n aegisforge --grace-period=0 --force
```