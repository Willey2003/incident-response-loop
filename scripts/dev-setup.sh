#!/bin/bash
# AegisForge Development Setup Script
# Installs all development tools and dependencies

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    return 0
}

install_go_tools() {
    log_info "Installing Go development tools..."
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    go install github.com/securego/gosec/v2/cmd/gosec@latest
    go install golang.org/x/vuln/cmd/govulncheck@latest
    go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest
    go install github.com/segmentio/golines@latest
    go install mvdan.cc/gofumpt@latest
}

install_python_tools() {
    log_info "Installing Python development tools..."
    pip install --upgrade pip
    pip install uv ruff bandit safety pip-audit pytest pytest-asyncio pytest-cov pytest-mock
    pip install pre-commit
}

install_node_tools() {
    log_info "Installing Node.js development tools..."
    # npm packages will be installed via package.json
    log_info "Node.js tools will be installed via npm install"
}

install_kubernetes_tools() {
    log_info "Installing Kubernetes development tools..."
    # kind
    if ! command -v kind &> /dev/null; then
        log_info "Installing kind..."
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    fi
    
    # kustomize
    if ! command -v kustomize &> /dev/null; then
        log_info "Installing kustomize..."
        curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        sudo mv ./kustomize /usr/local/bin/kustomize
    fi
    
    # helm
    if ! command -v helm &> /dev/null; then
        log_info "Installing helm..."
        curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    # kubectl (should already be present)
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl first."
        return 1
    fi
}

install_container_tools() {
    log_info "Installing container security tools..."
    # trivy
    if ! command -v trivy &> /dev/null; then
        log_info "Installing trivy..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    fi
    
    # cosign
    if ! command -v cosign &> /dev/null; then
        log_info "Installing cosign..."
        curl -fsSL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o cosign
        chmod +x cosign
        sudo mv cosign /usr/local/bin/
    fi
    
    # syft
    if ! command -v syft &> /dev/null; then
        log_info "Installing syft..."
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
    fi
}

install_pre_commit() {
    log_info "Installing pre-commit hooks..."
    pip install pre-commit
    pre-commit install
}

main() {
    echo "=========================================="
    echo "AegisForge Development Environment Setup"
    echo "=========================================="
    
    log_info "Checking system..."
    check_command docker || { log_error "Docker not installed"; exit 1; }
    check_command git || { log_error "Git not installed"; exit 1; }
    
    # Install tools
    install_go_tools
    install_python_tools
    install_node_tools
    install_kubernetes_tools
    install_container_tools
    install_pre_commit
    
    log_info "Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Run 'make dev-up' to start the development stack"
    echo "  2. Run 'make test' to run all tests"
    echo "  3. Run 'make build' to build all images"
    echo "  4. Run 'make kind-up' to create a local Kubernetes cluster"
    echo "  5. Run 'make deploy-dev' to deploy to the kind cluster"
}

# Check if running directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"