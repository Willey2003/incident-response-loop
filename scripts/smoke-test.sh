#!/bin/bash
# AegisForge Smoke Test Script
# Validates the end-to-end cyber defense control loop

set -euo pipefail

NAMESPACE="${NAMESPACE:-aegisforge}"
TIMEOUT="${TIMEOUT:-300}"
INTERVAL="${INTERVAL:-10}"
SCENARIOS="${SCENARIOS:-auth-brute-force,dns-tunneling,traffic-beaconing,traffic-port-scan}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prereqs() {
    log_info "Checking prerequisites..."
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl not found"; exit 1; }
    command -v curl >/dev/null 2>&1 || { log_error "curl not found"; exit 1; }
    command -v jq >/dev/null 2>&1 || { log_error "jq not found"; exit 1; }
    
    # Check cluster connectivity
    kubectl cluster-info >/dev/null 2>&1 || { log_error "Cannot connect to Kubernetes cluster"; exit 1; }
    
    # Check namespace exists
    kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || { log_error "Namespace $NAMESPACE not found"; exit 1; }
    
    log_info "Prerequisites check passed"
}

wait_for_pods() {
    log_info "Waiting for pods to be ready in namespace $NAMESPACE..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=aegisforge -n "$NAMESPACE" --timeout=300s || {
        log_error "Pods not ready within timeout"
        kubectl get pods -n "$NAMESPACE"
        return 1
    }
    log_info "All pods ready"
}

run_scenario() {
    local scenario=$1
    local run_id=""
    
    log_info "Starting scenario: $scenario"
    
    # Create emulation run
    local payload=$(cat <<EOF
{
  "scenario_id": "$scenario",
  "config_override": {},
  "target_namespace": "aegisforge-lab",
  "duration_override": 120
}
EOF
)
    
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "http://localhost:8004/api/v1/emulation/runs" 2>/dev/null || echo "{}")
    
    run_id=$(echo "$response" | jq -r '.run_id // empty')
    
    if [[ -z "$run_id" ]]; then
        log_error "Failed to start scenario $scenario"
        echo "$response" | jq .
        return 1
    fi
    
    log_info "Started run $run_id for scenario $scenario"
    
    # Wait for run to complete
    local elapsed=0
    while [[ $elapsed -lt 180 ]]; do
        sleep 10
        elapsed=$((elapsed + 10))
        
        local status=$(curl -s "http://localhost:8004/api/v1/emulation/runs/$run_id" 2>/dev/null | jq -r '.status // "unknown"')
        local progress=$(curl -s "http://localhost:8004/api/v1/emulation/runs/$run_id" 2>/dev/null | jq -r '.progress_percent // 0')
        
        log_info "Run $run_id status: $status, progress: ${progress}%"
        
        if [[ "$status" == "completed" ]]; then
            log_info "Scenario $scenario completed successfully"
            return 0
        elif [[ "$status" == "failed" ]]; then
            log_error "Scenario $scenario failed"
            return 1
        fi
    done
    
    log_warn "Scenario $scenario timed out"
    return 1
}

verify_alerts() {
    local scenario=$1
    log_info "Verifying alerts generated for scenario: $scenario"
    
    # Wait a bit for alerts to be generated
    sleep 10
    
    # Query alerts
    local alerts=$(curl -s "http://localhost:8000/api/v1/alerts?namespace=aegisforge-lab&page_size=50" 2>/dev/null)
    local count=$(echo "$alerts" | jq -r '.total // 0')
    
    if [[ $count -gt 0 ]]; then
        log_info "Found $count alerts generated"
        return 0
    else
        log_warn "No alerts generated yet"
        return 1
    fi
}

verify_incident_created() {
    log_info "Verifying incident creation..."
    
    sleep 5
    
    local incidents=$(curl -s "http://localhost:8000/api/v1/incidents?page_size=10" 2>/dev/null)
    local count=$(echo "$incidents" | jq -r '.total // 0')
    
    if [[ $count -gt 0 ]]; then
        log_info "Found $count incidents created"
        return 0
    else
        log_warn "No incidents created yet"
        return 1
    fi
}

verify_response_action() {
    log_info "Verifying response action execution..."
    
    sleep 5
    
    local actions=$(curl -s "http://localhost:8002/api/v1/response/actions?page_size=10" 2>/dev/null)
    local count=$(echo "$actions" | jq -r '.total // 0')
    
    if [[ $count -gt 0 ]]; then
        log_info "Found $count response actions"
        return 0
    else
        log_warn "No response actions executed yet"
        return 1
    fi
}

verify_audit_log() {
    log_info "Verifying audit log entry..."
    
    sleep 3
    
    local logs=$(curl -s "http://localhost:8000/api/v1/audit/logs?limit=10" 2>/dev/null)
    local count=$(echo "$logs" | jq '. | length')
    
    if [[ $count -gt 0 ]]; then
        log_info "Found $count audit log entries"
        return 0
    else
        log_warn "No audit log entries found"
        return 1
    fi
}

main() {
    log_info "Starting AegisForge Smoke Test"
    log_info "Namespace: $NAMESPACE"
    log_info "Scenarios: $SCENARIOS"
    
    check_prereqs
    
    # Port forward for local access
    log_info "Setting up port forwards..."
    kubectl port-forward -n "$NAMESPACE" svc/aegisforge-api-gateway 8000:8000 >/dev/null 2>&1 &
    PF_API=$!
    kubectl port-forward -n "$NAMESPACE" svc/aegisforge-emulation-controller 8004:8004 >/dev/null 2>&1 &
    PF_EMU=$!
    
    sleep 5
    
    wait_for_pods
    
    # Run each scenario
    IFS=',' read -ra SCENARIO_LIST <<< "$SCENARIOS"
    local failed=0
    local passed=0
    
    for scenario in "${SCENARIO_LIST[@]}"; do
        if run_scenario "$scenario"; then
            ((passed++))
            log_info "Scenario $scenario PASSED"
        else
            ((failed++))
            log_error "Scenario $scenario FAILED"
        fi
    done
    
    # Verify system responses
    log_info "Verifying system responses..."
    verify_alerts
    verify_incident_created
    verify_response_action
    verify_audit_log
    
    # Cleanup port forwards
    kill $PF_API $PF_EMU 2>/dev/null || true
    
    # Summary
    echo ""
    log_info "=== SMOKE TEST SUMMARY ==="
    log_info "Scenarios passed: $passed"
    log_info "Scenarios failed: $failed"
    
    if [[ $failed -eq 0 ]]; then
        log_info "ALL TESTS PASSED"
        exit 0
    else
        log_error "SOME TESTS FAILED"
        exit 1
    fi
}

main "$@"