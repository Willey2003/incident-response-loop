# Makefile for Incident Response Control Loop
# Provides common build, test, and deployment targets

# Variables
REGISTRY ?= registry.local
PROJECT := incident-response
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME := $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
GO_VERSION := 1.22
PYTHON_VERSION := 3.11

# Component directories
SENSOR_DIR := cmd/telemetry-sensor
CONTEXTUALIZER_DIR := cmd/threat-contextualizer
RECONCILER_DIR := cmd/reconciler-engine

# Image names
SENSOR_IMAGE := $(REGISTRY)/$(PROJECT)/telemetry-sensor
CONTEXTUALIZER_IMAGE := $(REGISTRY)/$(PROJECT)/threat-contextualizer
RECONCILER_IMAGE := $(REGISTRY)/$(PROJECT)/reconciler-engine

# Kubernetes
KUBECTL ?= kubectl
KUSTOMIZE ?= kustomize
HELM ?= helm
NAMESPACE := incident-response

# Go build flags
GO_LDFLAGS := -s -w \
  -X main.version=$(VERSION) \
  -X main.commit=$(COMMIT) \
  -X main.buildTime=$(BUILD_TIME)
GO_BUILD_FLAGS := -trimpath -ldflags="$(GO_LDFLAGS)" -buildmode=pie

# Default target
.PHONY: all
all: build

# ============================================================================
# DEVELOPMENT SETUP
# ============================================================================

.PHONY: dev-setup
dev-setup: ## Install development tools
	@echo "Installing development tools..."
	# Go tools
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/securego/gosec/v2/cmd/gosec@latest
	go install golang.org/x/vuln/cmd/govulncheck@latest
	go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest
	# Python tools
	pip install --upgrade pip
	pip install uv ruff bandit safety pip-audit pytest pytest-asyncio pytest-cov pytest-mock
	# Kubernetes tools
	@which kind >/dev/null || (echo "Install kind: https://kind.sigs.k8s.io/" && exit 1)
	@which kustomize >/dev/null || (echo "Install kustomize: https://kustomize.io/" && exit 1)
	@which helm >/dev/null || (echo "Install helm: https://helm.sh/" && exit 1)
	# Container tools
	@which docker >/dev/null || (echo "Install docker" && exit 1)
	@which trivy >/dev/null || (echo "Install trivy: https://aquasecurity.github.io/trivy/" && exit 1)
	@which cosign >/dev/null || (echo "Install cosign: https://docs.sigstore.dev/cosign/installation/" && exit 1)
	@which syft >/dev/null || (echo "Install syft: https://github.com/anchore/syft" && exit 1)
	# Pre-commit
	pip install pre-commit
	pre-commit install
	@echo "Development setup complete!"

# ============================================================================
# CODE QUALITY
# ============================================================================

.PHONY: lint
lint: lint-go lint-python lint-yaml ## Run all linters

.PHONY: lint-go
lint-go: ## Lint Go code
	@echo "Linting Go code..."
	golangci-lint run ./cmd/... ./pkg/...

.PHONY: lint-python
lint-python: ## Lint Python code
	@echo "Linting Python code..."
	cd $(CONTEXTUALIZER_DIR) && ruff check src/ tests/
	cd $(CONTEXTUALIZER_DIR) && ruff format --check src/ tests/

.PHONY: lint-yaml
lint-yaml: ## Lint YAML files
	@echo "Linting YAML files..."
	yamllint -c .yamllint.yml deploy/ configs/ .github/

.PHONY: fmt
fmt: fmt-go fmt-python ## Format all code

.PHONY: fmt-go
fmt-go: ## Format Go code
	@echo "Formatting Go code..."
	go fmt ./cmd/... ./pkg/...

.PHONY: fmt-python
fmt-python: ## Format Python code
	@echo "Formatting Python code..."
	cd $(CONTEXTUALIZER_DIR) && ruff format src/ tests/

.PHONY: vet
vet: ## Run go vet
	go vet ./cmd/... ./pkg/...

.PHONY: security-scan
security-scan: ## Run security scanners
	@echo "Running security scans..."
	gosec ./cmd/... ./pkg/...
	govulncheck ./cmd/... ./pkg/...
	cd $(CONTEXTUALIZER_DIR) && bandit -r src/
	cd $(CONTEXTUALIZER_DIR) && safety check
	cd $(CONTEXTUALIZER_DIR) && pip-audit

# ============================================================================
# TESTING
# ============================================================================

.PHONY: test
test: test-go test-python ## Run all tests

.PHONY: test-go
test-go: ## Run Go tests
	@echo "Running Go tests..."
	go test -v -race -coverprofile=coverage.out ./cmd/... ./pkg/...

.PHONY: test-python
test-python: ## Run Python tests
	@echo "Running Python tests..."
	cd $(CONTEXTUALIZER_DIR) && pytest -v --cov=contextualizer --cov-report=term-missing tests/

.PHONY: test-integration
test-integration: ## Run integration tests (requires kind cluster)
	@echo "Running integration tests..."
	./scripts/integration-test.sh

.PHONY: test-chaos
test-chaos: ## Run chaos tests (requires deployed stack)
	@echo "Running chaos tests..."
	cd test/chaos && python chaos_test.py --namespace $(NAMESPACE) --duration 300

.PHONY: test-load
test-load: ## Run load tests
	@echo "Running load tests..."
	k6 run test/load/k6/sensor_load.js
	k6 run test/load/k6/contextualizer_load.js

.PHONY: bench
bench: ## Run benchmarks
	go test -bench=. -benchmem ./cmd/... ./pkg/...

# ============================================================================
# BUILD
# ============================================================================

.PHONY: build
build: build-sensor build-contextualizer build-reconciler ## Build all components

.PHONY: build-sensor
build-sensor: ## Build telemetry-sensor
	@echo "Building telemetry-sensor..."
	cd $(SENSOR_DIR) && CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build $(GO_BUILD_FLAGS) -o telemetry-sensor ./main.go

.PHONY: build-contextualizer
build-contextualizer: ## Build threat-contextualizer (Python - creates wheel)
	@echo "Building threat-contextualizer..."
	cd $(CONTEXTUALIZER_DIR) && uv build --wheel

.PHONY: build-reconciler
build-reconciler: ## Build reconciler-engine
	@echo "Building reconciler-engine..."
	cd $(RECONCILER_DIR) && CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build $(GO_BUILD_FLAGS) -o reconciler-engine ./main.go

.PHONY: docker-build
docker-build: docker-build-sensor docker-build-contextualizer docker-build-reconciler ## Build all Docker images

.PHONY: docker-build-sensor
docker-build-sensor: ## Build telemetry-sensor Docker image
	@echo "Building telemetry-sensor Docker image..."
	docker build -t $(SENSOR_IMAGE):$(VERSION) -t $(SENSOR_IMAGE):latest $(SENSOR_DIR)

.PHONY: docker-build-contextualizer
docker-build-contextualizer: ## Build threat-contextualizer Docker image
	@echo "Building threat-contextualizer Docker image..."
	docker build -t $(CONTEXTUALIZER_IMAGE):$(VERSION) -t $(CONTEXTUALIZER_IMAGE):latest $(CONTEXTUALIZER_DIR)

.PHONY: docker-build-reconciler
docker-build-reconciler: ## Build reconciler-engine Docker image
	@echo "Building reconciler-engine Docker image..."
	docker build -t $(RECONCILER_IMAGE):$(VERSION) -t $(RECONCILER_IMAGE):latest $(RECONCILER_DIR)

# ============================================================================
# REGISTRY OPERATIONS
# ============================================================================

.PHONY: login
login: ## Login to registry
	@echo "Logging into $(REGISTRY)..."
	docker login $(REGISTRY)

.PHONY: push
push: push-sensor push-contextualizer push-reconciler ## Push all images to registry

.PHONY: push-sensor
push-sensor: docker-build-sensor ## Push telemetry-sensor
	docker push $(SENSOR_IMAGE):$(VERSION)
	docker push $(SENSOR_IMAGE):latest

.PHONY: push-contextualizer
push-contextualizer: docker-build-contextualizer ## Push threat-contextualizer
	docker push $(CONTEXTUALIZER_IMAGE):$(VERSION)
	docker push $(CONTEXTUALIZER_IMAGE):latest

.PHONY: push-reconciler
push-reconciler: docker-build-reconciler ## Push reconciler-engine
	docker push $(RECONCILER_IMAGE):$(VERSION)
	docker push $(RECONCILER_IMAGE):latest

.PHONY: pull
pull: ## Pull all images from registry
	docker pull $(SENSOR_IMAGE):$(VERSION)
	docker pull $(CONTEXTUALIZER_IMAGE):$(VERSION)
	docker pull $(RECONCILER_IMAGE):$(VERSION)

# ============================================================================
# DEPLOYMENT
# ============================================================================

.PHONY: deploy
deploy: deploy-kustomize ## Deploy via Kustomize (default)

.PHONY: deploy-kustomize
deploy-kustomize: ## Deploy using Kustomize
	@echo "Deploying via Kustomize to $(NAMESPACE)..."
	$(KUSTOMIZE) build deploy/manifests/overlays/production | $(KUBECTL) apply -f -

.PHONY: deploy-dev
deploy-dev: ## Deploy development overlay
	@echo "Deploying development overlay..."
	$(KUSTOMIZE) build deploy/manifests/overlays/development | $(KUBECTL) apply -f -

.PHONY: deploy-staging
deploy-staging: ## Deploy staging overlay
	@echo "Deploying staging overlay..."
	$(KUSTOMIZE) build deploy/manifests/overlays/staging | $(KUBECTL) apply -f -

.PHONY: deploy-prod
deploy-prod: ## Deploy production overlay
	@echo "Deploying production overlay..."
	$(KUSTOMIZE) build deploy/manifests/overlays/production | $(KUBECTL) apply -f -

.PHONY: deploy-helm
deploy-helm: ## Deploy using Helm
	@echo "Deploying via Helm..."
	$(HELM) upgrade --install incident-response ./deploy/helm/incident-response-loop \
		-n $(NAMESPACE) --create-namespace \
		--set global.imageRegistry=$(REGISTRY) \
		--set global.imageTag=$(VERSION)

.PHONY: undeploy
undeploy: ## Remove deployment
	@echo "Removing deployment..."
	$(KUSTOMIZE) build deploy/manifests/overlays/production | $(KUBECTL) delete -f --ignore-not-found=true

.PHONY: status
status: ## Check deployment status
	@echo "=== Pods ==="
	$(KUBECTL) get pods -n $(NAMESPACE) -o wide
	@echo ""
	@echo "=== Services ==="
	$(KUBECTL) get svc -n $(NAMESPACE)
	@echo ""
	@echo "=== NetworkPolicies ==="
	$(KUBECTL) get netpol -n $(NAMESPACE)
	@echo ""
	@echo "=== RBAC ==="
	$(KUBECTL) get role,rolebinding -n $(NAMESPACE)

.PHONY: logs
logs: ## View logs for all components
	$(KUBECTL) logs -n $(NAMESPACE) -l app.kubernetes.io/part-of=incident-response-loop --tail=100 -f

.PHONY: logs-sensor
logs-sensor: ## View sensor logs
	$(KUBECTL) logs -n $(NAMESPACE) -l app.kubernetes.io/name=telemetry-sensor --tail=100 -f

.PHONY: logs-contextualizer
logs-contextualizer: ## View contextualizer logs
	$(KUBECTL) logs -n $(NAMESPACE) -l app.kubernetes.io/name=threat-contextualizer --tail=100 -f

.PHONY: logs-reconciler
logs-reconciler: ## View reconciler logs
	$(KUBECTL) logs -n $(NAMESPACE) -l app.kubernetes.io/name=reconciler-engine --tail=100 -f

# ============================================================================
# SECURITY & COMPLIANCE
# ============================================================================

.PHONY: scan-images
scan-images: ## Scan Docker images for vulnerabilities
	@echo "Scanning images with Trivy..."
	trivy image --severity HIGH,CRITICAL $(SENSOR_IMAGE):$(VERSION)
	trivy image --severity HIGH,CRITICAL $(CONTEXTUALIZER_IMAGE):$(VERSION)
	trivy image --severity HIGH,CRITICAL $(RECONCILER_IMAGE):$(VERSION)

.PHONY: generate-sbom
generate-sbom: ## Generate SBOM for all images
	@echo "Generating SBOMs..."
	syft $(SENSOR_IMAGE):$(VERSION) -o spdx-json=sbom-sensor.spdx.json
	syft $(CONTEXTUALIZER_IMAGE):$(VERSION) -o spdx-json=sbom-contextualizer.spdx.json
	syft $(RECONCILER_IMAGE):$(VERSION) -o spdx-json=sbom-reconciler.spdx.json

.PHONY: sign-images
sign-images: ## Sign images with Cosign
	@echo "Signing images..."
	cosign sign --yes $(SENSOR_IMAGE):$(VERSION)
	cosign sign --yes $(CONTEXTUALIZER_IMAGE):$(VERSION)
	cosign sign --yes $(RECONCILER_IMAGE):$(VERSION)

.PHONY: verify-signatures
verify-signatures: ## Verify image signatures
	cosign verify $(SENSOR_IMAGE):$(VERSION)
	cosign verify $(CONTEXTUALIZER_IMAGE):$(VERSION)
	cosign verify $(RECONCILER_IMAGE):$(VERSION)

# ============================================================================
# UTILITIES
# ============================================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -f $(SENSOR_DIR)/telemetry-sensor
	rm -f $(RECONCILER_DIR)/reconciler-engine
	rm -rf $(CONTEXTUALIZER_DIR)/dist $(CONTEXTUALIZER_DIR)/build *.egg-info
	rm -f coverage.out sbom-*.spdx.json
	docker system prune -f

.PHONY: generate-certs
generate-certs: ## Generate TLS certificates for local development
	@echo "Generating certificates..."
	./scripts/cert-gen.sh

.PHONY: registry-setup
registry-setup: ## Setup local registry (Harbor)
	@echo "Setting up local registry..."
	./scripts/registry-setup.sh

.PHONY: kind-create
kind-create: ## Create kind cluster for testing
	@echo "Creating kind cluster..."
	kind create cluster --name incident-response --config scripts/kind-config.yaml

.PHONY: kind-delete
kind-delete: ## Delete kind cluster
	kind delete cluster --name incident-response

.PHONY: help
help: ## Show this help
	@echo "Incident Response Control Loop - Make Targets"
	@echo ""
	@awk 'BEGIN {FS = ":.*## "; printf "%-25s %s\n", "Target", "Description"} /^[a-zA-Z_-]+:.*##/ {printf "%-25s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================================================
# CI TARGETS (Used by GitHub Actions)
# ============================================================================

.PHONY: ci-lint
ci-lint: lint security-scan ## CI lint target

.PHONY: ci-test
ci-test: test ## CI test target

.PHONY: ci-build
ci-build: build docker-build ## CI build target

.PHONY: ci-security
ci-security: scan-images generate-sbom ## CI security target

.PHONY: ci-release
ci-release: build docker-build scan-images generate-sbom sign-images ## CI release target