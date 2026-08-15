# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and monorepo setup
- Phase 1: Telemetry Sensor (Go) - DaemonSet with eBPF/cgroup network anomaly detection
- Phase 2: Threat Contextualizer (Python/FastAPI) - Aho-Corasick IoC matching with mock CVE/MITRE DB
- Phase 3: Reconciler Engine (Go) - Dynamic NetworkPolicy isolation + workload replacement
- Complete Kustomize manifests with dev/staging/prod overlays
- Helm chart with values-dev.yaml and values-prod.yaml
- Full CI/CD pipeline with GitHub Actions
- Local development stack with docker-compose.dev.yml
- Comprehensive documentation suite

### Security
- CPU-only AI Security Copilot with Ollama + Qdrant
- Automatic PII/secret redaction before LLM processing
- Prompt injection defense with fixed system prompts
- Distroless/non-root container images
- NetworkPolicy default-deny with explicit allow rules
- Namespace-scoped RBAC (no ClusterRoles)

## [1.0.0] - 2024-01-15

### Added
- Initial release of AegisForge Autonomous Incident Response Control Loop
- Phase 1: Telemetry Sensor (Go) with EWMA/Z-score anomaly detection
- Phase 2: Threat Contextualizer with Aho-Corasick IoC matching
- Phase 3: Reconciler Engine with NetworkPolicy isolation + workload replacement
- Kustomize/Helm deployment manifests
- GitHub Actions CI/CD pipeline with security scanning
- Local development stack with docker-compose
- Kind cluster support for local testing
- Comprehensive documentation suite

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/).

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions
- **PATCH** version for backward-compatible bug fixes

## Release Process

1. Update version in `Chart.yaml`, `pyproject.toml`, and `go.mod` files
2. Update `CHANGELOG.md` with release notes
3. Create release tag: `git tag -a v1.x.x -m "Release v1.x.x"`
4. Push tag: `git push origin v1.x.x`
5. GitHub Actions will build, test, sign, and create GitHub Release

## Release Types

- **Patch** (1.0.x): Bug fixes, security patches
- **Minor** (1.x.0): New features, backward compatible
- **Major** (x.0.0): Breaking changes, major architecture changes

## Release Schedule

- **Patch releases**: As needed (security patches ASAP)
- **Minor releases**: Monthly
- **Major releases**: Annually

## Support Policy

- **Current minor version**: Full support (bug fixes, security patches)
- **Previous minor version**: Security patches only (6 months)
- **Older versions**: End of life

## Release Checklist

- [ ] All CI checks pass
- [ ] Security scans pass (Trivy, gosec, govulncheck, bandit)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass (Kind cluster)
- [ ] Smoke test passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in all relevant files
- [ ] Git tag created and pushed
- [ ] GitHub Release created with artifacts
- [ ] Docker images pushed to registry
- [ ] Helm chart published
- [ ] SBOM generated and attested
- [ ] Images signed with Cosign