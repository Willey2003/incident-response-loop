#!/bin/bash
# AegisForge Kind Cluster Setup Script
# Creates a local Kubernetes cluster with all required components for testing

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

CLUSTER_NAME="aegisforge-test"
KIND_CONFIG="scripts/kind-config.yaml"

check_prereqs() {
    log_info "Checking prerequisites..."
    command -v kind >/dev/null 2>&1 || { log_error "kind not installed"; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl not installed"; exit 1; }
    command -v helm >/dev/null 2>&1 || { log_error "helm not installed"; exit 1; }
    command -v docker >/dev/null 2>&1 || { log_error "docker not installed"; exit 1; }
    log_info "Prerequisites check passed"
}

create_cluster() {
    log_info "Creating kind cluster: $CLUSTER_NAME"
    
    if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        log_warn "Cluster $CLUSTER_NAME already exists"
        return 0
    fi
    
    kind create cluster --name "$CLUSTER_NAME" --config scripts/kind-config.yaml
    
    log_info "Waiting for cluster to be ready..."
    kubectl wait --for=condition=ready node --all --timeout=120s
}

install_calico() {
    log_info "Installing Calico CNI..."
    kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
    kubectl wait --for=condition=ready pod -l k8s-app=calico-node -n kube-system --timeout=120s
    kubectl wait --for=condition=ready pod -l k8s-app=calico-kube-controllers -n kube-system --timeout=120s
}

install_local_registry() {
    log_info "Deploying local Docker registry..."
    docker run -d --restart=always --name registry-local -p 5000:5000 registry:2 || true
    
    # Connect registry to kind network
    docker network connect kind registry-local || true
    
    # Configure containerd to use local registry
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:5000"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
EOF
}

deploy_aegisforge() {
    log_info "Deploying AegisForge platform..."
    
    # Add helm repo if needed
    helm repo add aegisforge https://charts.aegisforge.example.com || true
    helm repo update
    
    # Deploy development overlay
    kubectl apply -k deploy/manifests/overlays/development
    
    # Wait for deployments
    kubectl wait --for=condition=available --timeout=300s deployment -n aegisforge --all
    
    log_info "AegisForge deployed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    kubectl get pods -n aegisforge
    kubectl get pods -n aegisforge-lab
    kubectl get pods -n monitoring
    
    # Check services
    kubectl get svc -n aegisforge
    kubectl get svc -n monitoring
    
    # Check network policies
    kubectl get netpol -n aegisforge
    kubectl get netpol -n aegisforge-lab
    
    log_info "Deployment verification complete"
}

run_smoke_test() {
    log_info "Running smoke test..."
    
    # Port forward for local access
    kubectl port-forward -n aegisforge svc/aegisforge-api-gateway 8000:8000 >/dev/null 2>&1 &
    PF_API=$!
    kubectl port-forward -n aegisforge svc/aegisforge-emulation-controller 8004:8004 >/dev/null 2>&1 &
    PF_EMU=$!
    
    sleep 5
    
    # Run smoke test
    cd tests/chaos
    pip install -r requirements.txt
    python chaos_test.py --namespace incident-response --duration 120 --scenarios burst_traffic payload_spike
    
    kill $PF_API $PF_EMU 2>/dev/null || true
}

main() {
    echo "=========================================="
    echo "AegisForge Kind Cluster Setup"
    echo "=========================================="
    
    check_prereqs
    create_cluster
    install_calico
    install_local_registry
    deploy_aegisforge
    verify_deployment
    
    log_info "AegisForge is ready!"
    echo ""
    echo "Access points:"
    echo "  Analyst Console: http://localhost:3000 (run: kubectl port-forward -n aegisforge svc/aegisforge-analyst-console 3000:3000)"
    echo "  API Gateway: http://localhost:8000 (run: kubectl port-forward -n aegisforge svc/aegisforge-api-gateway 8000:8000)"
    echo "  Grafana: http://localhost:3001 (run: kubectl port-forward -n monitoring svc/aegisforge-grafana 3001:3000)"
    echo "  Prometheus: http://localhost:9090 (run: kubectl port-forward -n monitoring svc/aegisforge-prometheus 9090:9090)"
    echo "  MinIO Console: http://localhost:9001 (run: kubectl port-forward -n aegisforge svc/aegisforge-minio 9001:9001)"
    echo ""
    echo "Run smoke test: ./scripts/smoke-test.sh"
}

main "$@"