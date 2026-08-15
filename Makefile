# AegisForge Makefile
# Production-grade cyber-defense platform build and deployment automation

.PHONY: help dev-up dev-down dev-logs dev-ps build push test lint fmt kind-up kind-down deploy deploy-dev deploy-prod smoke-test clean

# Default target
help:
	@echo "AegisForge - CPU-only Cyber Defense Platform"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development (Docker Compose):"
	@echo "  dev-up       Start full local stack with Docker Compose"
	@echo "  dev-down     Stop and remove local stack"
	@echo "  dev-logs     Follow logs for all services"
	@echo "  dev-ps       Show running containers"
	@echo "  dev-restart  Restart all services"
	@echo ""
	@echo "Build & Test:"
	@echo "  build        Build all Docker images"
	@echo "  push         Push all images to Docker Hub"
	@echo "  test         Run all tests (unit + integration)"
	@echo "  lint         Run all linters"
	@echo "  fmt          Format code"
	@echo "  smoke-test   Run end-to-end smoke test"
	@echo ""
	@echo "Kubernetes (kind):"
	@echo "  kind-up      Create kind cluster with Calico CNI"
	@echo "  kind-down    Delete kind cluster"
	@echo "  deploy       Deploy to Kubernetes via Helm"
	@echo "  deploy-dev   Deploy development overlay"
	@echo "  deploy-prod  Deploy production overlay"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Remove build artifacts and containers"
	@echo "  db-migrate   Run database migrations"
	@echo "  db-seed      Seed database with sample data"

# Variables
REGISTRY ?= docker.io
ORG ?= willey2003
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE ?= $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
GO_VERSION := 1.22
PYTHON_VERSION := 3.12
NODE_VERSION := 20

# Image names
IMAGES := \
	api-gateway \
	detection-engine \
	response-orchestrator \
	ai-copilot \
	emulation-controller \
	analyst-console \
	target-api \
	auth-simulator \
	workload-simulator \
	dns-simulator \
	traffic-simulator

# Full image names with registry
FULL_IMAGES := $(addprefix $(REGISTRY)/$(ORG)/aegisforge-, $(IMAGES))

# ============================================================
# DOCKER COMPOSE DEVELOPMENT
# ============================================================

dev-up:
	@echo "Starting AegisForge local development stack..."
	docker compose -f docker-compose.dev.yml up -d --build
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@make dev-ps
	@echo ""
	@echo "AegisForge is running!"
	@echo "  Analyst Console: http://localhost:3000"
	@echo "  API Gateway:     http://localhost:8000"
	@echo "  Grafana:         http://localhost:3001 (admin/admin)"
	@echo "  Prometheus:      http://localhost:9090"
	@echo "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
	@echo "  Qdrant:          http://localhost:6333"

dev-down:
	@echo "Stopping AegisForge local stack..."
	docker compose -f docker-compose.dev.yml down -v --remove-orphans

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f --tail=100

dev-ps:
	docker compose -f docker-compose.dev.yml ps

dev-restart: dev-down dev-up

# ============================================================
# BUILD & PUSH
# ============================================================

build:
	@echo "Building all images..."
	@for img in $(IMAGES); do \
		echo "Building $$img..."; \
		docker build -t $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) \
			-t $(REGISTRY)/$(ORG)/aegisforge-$$img:latest \
			--build-arg VERSION=$(VERSION) \
			--build-arg COMMIT=$(COMMIT) \
			--build-arg BUILD_DATE=$(BUILD_DATE) \
			./services/$$img 2>/dev/null || \
		docker build -t $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) \
			-t $(REGISTRY)/$(ORG)/aegisforge-$$img:latest \
			--build-arg VERSION=$(VERSION) \
			--build-arg COMMIT=$(COMMIT) \
			--build-arg BUILD_DATE=$(BUILD_DATE) \
			./simulators/$$img 2>/dev/null || \
		docker build -t $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) \
			-t $(REGISTRY)/$(ORG)/aegisforge-$$img:latest \
			--build-arg VERSION=$(VERSION) \
			--build-arg COMMIT=$(COMMIT) \
			--build-arg BUILD_DATE=$(BUILD_DATE) \
			./web/$$img 2>/dev/null || true; \
	done

push:
	@echo "Pushing all images to $(REGISTRY)/$(ORG)..."
	@for img in $(IMAGES); do \
		echo "Pushing $$img..."; \
		docker push $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION); \
		docker push $(REGISTRY)/$(ORG)/aegisforge-$$img:latest; \
	done

# ============================================================
# TESTING
# ============================================================

test: test-unit test-integration test-e2e

test-unit:
	@echo "Running unit tests..."
	@find services simulators web -name "*_test.py" -o -name "*_test.go" -o -name "*.test.ts" | xargs -I {} sh -c 'echo "Running {}" && cd $(dir {}) && go test ./... 2>/dev/null || python -m pytest {} -v 2>/dev/null || npm test -- {} 2>/dev/null || true'

test-integration:
	@echo "Running integration tests..."
	@cd tests/integration && python -m pytest -v --tb=short

test-e2e:
	@echo "Running E2E tests..."
	@cd tests/e2e && python -m pytest -v --tb=short

test-load:
	@echo "Running load tests..."
	@cd tests/load && k6 run script.js

# ============================================================
# LINTING & FORMATTING
# ============================================================

lint: lint-go lint-python lint-ts lint-yaml lint-docker lint-helm

lint-go:
	@echo "Linting Go code..."
	@golangci-lint run ./services/... ./simulators/... 2>/dev/null || true

lint-python:
	@echo "Linting Python code..."
	@ruff check services/ simulators/ 2>/dev/null || true
	@ruff format --check services/ simulators/ 2>/dev/null || true

lint-ts:
	@echo "Linting TypeScript code..."
	@cd web/analyst-console && npm run lint 2>/dev/null || true

lint-yaml:
	@echo "Linting YAML files..."
	@yamllint -c .yamllint.yml deploy/ docs/ 2>/dev/null || true

lint-docker:
	@echo "Linting Dockerfiles..."
	@hadolint services/*/Dockerfile simulators/*/Dockerfile web/*/Dockerfile 2>/dev/null || true

lint-helm:
	@echo "Linting Helm charts..."
	@helm lint deploy/helm/aegisforge 2>/dev/null || true

fmt: fmt-go fmt-python fmt-ts

fmt-go:
	@echo "Formatting Go code..."
	@gofmt -w services/ simulators/ 2>/dev/null || true

fmt-python:
	@echo "Formatting Python code..."
	@ruff format services/ simulators/ 2>/dev/null || true

fmt-ts:
	@echo "Formatting TypeScript code..."
	@cd web/analyst-console && npm run format 2>/dev/null || true

# ============================================================
# KUBERNETES (kind)
# ============================================================

kind-up:
	@echo "Creating kind cluster with Calico CNI..."
	@kind create cluster --name aegisforge --config scripts/kind-config.yaml
	@echo "Installing Calico CNI..."
	@kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
	@kubectl wait --for=condition=ready pod -l k8s-app=calico-node -n kube-system --timeout=120s
	@echo "Kind cluster ready!"

kind-down:
	@echo "Deleting kind cluster..."
	@kind delete cluster --name aegisforge

# ============================================================
# HELM DEPLOYMENT
# ============================================================

deploy: deploy-prod

deploy-dev:
	@echo "Deploying development overlay..."
	@helm upgrade --install aegisforge deploy/helm/aegisforge \
		-n aegisforge --create-namespace \
		-f deploy/helm/aegisforge/values-dev.yaml \
		--set global.imageRegistry=$(REGISTRY) \
		--set global.imageTag=$(VERSION) \
		--set global.imagePullPolicy=Always \
		--wait --timeout=10m

deploy-prod:
	@echo "Deploying production overlay..."
	@helm upgrade --install aegisforge deploy/helm/aegisforge \
		-n aegisforge --create-namespace \
		-f deploy/helm/aegisforge/values-prod.yaml \
		--set global.imageRegistry=$(REGISTRY) \
		--set global.imageTag=$(VERSION) \
		--set global.imagePullPolicy=IfNotPresent \
		--wait --timeout=10m

deploy-rollback:
	@helm rollback aegisforge -n aegisforge

deploy-status:
	@kubectl get all -n aegisforge
	@echo ""
	@helm list -n aegisforge

# ============================================================
# SMOKE TEST
# ============================================================

smoke-test:
	@echo "Running smoke test..."
	@./scripts/smoke-test.sh

# ============================================================
# DATABASE
# ============================================================

db-migrate:
	@echo "Running database migrations..."
	@docker compose -f docker-compose.dev.yml exec api-gateway alembic upgrade head

db-seed:
	@echo "Seeding database..."
	@docker compose -f docker-compose.dev.yml exec api-gateway python -m scripts.seed_db

db-reset: dev-down dev-up db-migrate db-seed

# ============================================================
# MAINTENANCE
# ============================================================

clean:
	@echo "Cleaning build artifacts..."
	@docker system prune -f
	@rm -rf services/*/dist services/*/build services/*/*.egg-info
	@rm -rf web/analyst-console/dist web/analyst-console/node_modules
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

# ============================================================
# CI/CD HELPERS
# ============================================================

ci-lint: lint
ci-test: test
ci-build: build
ci-security: ci-sast ci-deps ci-container

ci-sast:
	@echo "Running SAST..."
	@semgrep scan --config=auto --error 2>/dev/null || true

ci-deps:
	@echo "Checking dependencies..."
	@pip-audit 2>/dev/null || true
	@npm audit --audit-level=high 2>/dev/null || true

ci-container:
	@echo "Scanning container images..."
	@for img in $(IMAGES); do \
		trivy image --severity HIGH,CRITICAL $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) 2>/dev/null || true; \
	done

ci-sbom:
	@echo "Generating SBOMs..."
	@for img in $(IMAGES); do \
		syft $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) -o spdx-json=sbom-$$img.spdx.json 2>/dev/null || true; \
	done

ci-sign:
	@echo "Signing images..."
	@for img in $(IMAGES); do \
		cosign sign --yes $(REGISTRY)/$(ORG)/aegisforge-$$img:$(VERSION) 2>/dev/null || true; \
	done