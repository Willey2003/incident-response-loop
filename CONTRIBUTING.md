# Contributing to AegisForge

Thank you for your interest in contributing to AegisForge! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before reporting a bug, please search the existing issues to avoid duplicates. When reporting a bug, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, Kubernetes version, AegisForge version)
- Relevant logs or screenshots

### Suggesting Features

Feature requests are welcome! Please provide:

- A clear description of the feature
- Use cases and motivation
- Potential implementation approach
- Any breaking changes or migration considerations

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Ensure all tests pass
5. Update documentation as needed
6. Submit a pull request

### Pull Request Guidelines

- Keep changes focused and atomic
- Write clear commit messages
- Include tests for new functionality
- Update documentation for user-facing changes
- Ensure CI passes

## Development Setup

### Prerequisites

- Go 1.22+
- Python 3.11+
- Node.js 20+
- Docker 24+
- Kubernetes 1.27+ (or kind for local development)
- Helm 3.12+

### Local Development

```bash
# Clone repository
git clone https://github.com/your-org/aegisforge.git
cd aegisforge

# Install development tools
make dev-setup

# Install pre-commit hooks
pre-commit install

# Start local stack
make dev-up

# Run tests
make test

# Run linters
make lint
```

### Code Style

- **Go**: Follow standard Go conventions, use `gofmt`, `golangci-lint`
- **Python**: Follow PEP 8, use `ruff` for linting/formatting
- **TypeScript**: Use `prettier` and `eslint`
- **YAML**: Use `yamllint`
- **Dockerfile**: Use `hadolint`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

Examples:
```
feat(sensor): add new entropy-based detection
fix(detection-engine): handle empty event batch in rule evaluator
docs(architecture): update threat model diagram
test(response-orchestrator): add unit tests for rollback logic
```

## Testing

### Unit Tests

```bash
# Go tests
make test-go

# Python tests
make test-python

# All tests
make test
```

### Integration Tests

```bash
# Requires kind cluster
make test-integration
```

### Chaos Tests

```bash
# Requires deployed stack
make test-chaos
```

### Load Tests

```bash
# Requires deployed cluster and k6
make test-load
```

## Security

### Secret Management

- **Never commit secrets** - enforced by pre-commit hooks
- Use **SealedSecrets** or **External Secrets Operator** in cluster
- Local development uses `.env` files (gitignored)

### Dependency Security

- **Go**: `go vet`, `gosec`, `govulncheck` in CI
- **Python**: `bandit`, `safety`, `pip-audit` in CI
- **Container**: `trivy` scans on every build

### Code Review Requirements

- **CODEOWNERS** defines required reviewers per component
- **Security team** must approve RBAC/NetworkPolicy changes
- **Minimum 2 approvals** for merge

## Branch Strategy

```
main (protected)
  ├── release/v1.0.x (maintenance branches)
  ├── feature/* (feature branches)
  ├── fix/* (bug fixes)
  ├── security/* (security patches)
  └── docs/* (documentation updates)
```

### Protection Rules for `main`

- Require PR reviews (2 minimum)
- Require status checks (CI pass)
- Require linear history
- No force pushes
- Signed commits required

## Security Practices

### Vulnerability Reporting

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policy.

### Security-First Development

- **Never commit secrets** - enforced by pre-commit hooks
- Use **SealedSecrets** or **External Secrets Operator** in cluster
- Local development uses `.env` files (gitignored)

### Dependency Security

- **Go**: `go vet`, `gosec`, `govulncheck` in CI
- **Python**: `bandit`, `safety`, `pip-audit` in CI
- **Container**: `trivy` scans on every build

### Supply Chain

- **SBOM generation** (Syft) on release
- **Artifact signing** (Cosign) on release
- **Pin dependencies** with lock files (`go.sum`, `uv.lock`)
- **Renovate/Dependabot** for automated updates

## Code Review Requirements

### Reviewer Checklist

- [ ] Code follows project conventions
- [ ] Tests added/updated for changes
- [ ] Documentation updated
- [ ] No secrets or credentials committed
- [ ] No breaking changes without version bump
- [ ] Security implications considered
- [ ] Performance impact assessed

### Required Approvals

- **Security team** must approve RBAC/NetworkPolicy changes
- **Minimum 2 approvals** for merge
- **CI must pass** before merge

## Release Process

See [RELEASE.md](RELEASE.md) for detailed release process.

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# CI/CD handles rest automatically
```

## License

By contributing to AegisForge, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to AegisForge! 🛡️