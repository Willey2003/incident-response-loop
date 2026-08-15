# AegisForge Benchmark Plan

## Overview

This document defines the performance benchmarking methodology, test scenarios, and success criteria for the AegisForge platform.

## Benchmark Objectives

1. **Validate CPU-only AI performance** meets latency requirements
2. **Verify detection engine throughput** under load
3. **Confirm response orchestrator latency** meets SLA
4. **Validate end-to-end pipeline** from event to alert to containment
5. **Establish baseline metrics** for regression detection

## Test Environment

### Hardware Specifications

| Component | Development | Production Baseline |
|-----------|-------------|---------------------|
| CPU | AMD EPYC / Intel Xeon (4-8 cores) | AMD EPYC / Intel Xeon (16-32 cores) |
| RAM | 16-32 GB | 64-128 GB |
| Storage | NVMe SSD (500 GB) | NVMe SSD (2 TB) |
| Network | 10 Gbps | 25 Gbps |

### Software Versions

| Component | Version |
|-----------|---------|
| Kubernetes | 1.29+ |
| Docker | 24+ |
| Python | 3.12 |
| Go | 1.22 |
| Node.js | 20 LTS |
| PostgreSQL | 16 |
| Redpanda | 23.3 |
| Qdrant | 1.8 |
| Ollama | 0.1.42 |
| Prometheus | 2.48 |
| Grafana | 10.2 |

## Benchmark Categories

### 1. AI Copilot Benchmarks

#### Test Scenarios

| Scenario | Description | Input Size | Target |
|----------|-------------|------------|--------|
| Incident Summary | Summarize incident with 10 alerts | 50 KB | < 5s p95 |
| Alert Triage | Triage single alert with evidence | 10 KB | < 4s p95 |
| Runbook Recommendation | Match incident to runbook | 20 KB | < 3s p95 |
| Report Generation | 2000-word post-incident report | 100 KB | < 30s p95 |
| NL Search | Search 100K vectors | 1 KB query | < 2s p95 |
| Timeline Summary | 50 events over 24h | 50 KB | < 4s p95 |

#### Load Levels

| Level | Concurrent Requests | Duration |
|-------|---------------------|----------|
| Baseline | 1 | 5 min |
| Light | 5 | 10 min |
| Moderate | 10 | 15 min |
| Heavy | 20 | 20 min |
| Stress | 50 | 30 min |

#### Metrics Collection

```bash
# Run AI benchmarks
cd tests/load/ai
k6 run --vus 10 --duration 10m incident-summary.js
k6 run --vus 10 --duration 10m alert-triage.js
k6 run --vus 10 --duration 10m runbook-recommendation.js
k6 run --vus 5 --duration 10m report-generation.js
k6 run --vus 20 --duration 10m nl-search.js
```

#### Success Criteria

| Metric | Target |
|--------|--------|
| Incident Summary p50 | < 3s |
| Incident Summary p95 | < 5s |
| Alert Triage p50 | < 2s |
| Alert Triage p95 | < 4s |
| Runbook Rec p50 | < 2s |
| Runbook Rec p95 | < 3s |
| Report Gen p50 | < 20s |
| Report Gen p95 | < 30s |
| NL Search p50 | < 1s |
| NL Search p95 | < 2s |
| Error Rate | < 0.1% |
| CPU Utilization | < 80% |
| Memory Usage | < 85% |

### 2. Detection Engine Benchmarks

#### Throughput Tests

| Test | Events/sec | Duration | Target Latency |
|------|------------|----------|----------------|
| Baseline | 1,000 | 10 min | < 100ms p95 |
| Light Load | 5,000 | 15 min | < 200ms p95 |
| Moderate | 10,000 | 20 min | < 300ms p95 |
| Heavy | 25,000 | 30 min | < 500ms p95 |
| Burst | 50,000 (30s) | 1 min | < 1s p95 |

#### Rule Complexity Tests

| Rule Set | Rules | Conditions/Rule | Expected Latency |
|----------|-------|-----------------|------------------|
| Minimal | 10 | 1-2 | < 10ms |
| Standard | 100 | 3-5 | < 50ms |
| Complex | 500 | 5-10 | < 100ms |
| Enterprise | 1000 | 10+ | < 200ms |

#### Correlation Tests

| Scenario | Events in Window | Correlations | Target |
|----------|------------------|--------------|--------|
| Simple | 100 | 5 | < 50ms |
| Moderate | 1,000 | 50 | < 100ms |
| Complex | 10,000 | 500 | < 500ms |

#### Metrics Collection

```bash
# Run detection benchmarks
cd tests/load/detection
k6 run --vus 50 --duration 15m throughput.js
k6 run --vus 100 --duration 20m correlation.js
k6 run --vus 10 --duration 10m rule-complexity.js
```

#### Success Criteria

| Metric | Target |
|--------|--------|
| 1K events/sec p50 | < 50ms |
| 10K events/sec p50 | < 200ms |
| 25K events/sec p50 | < 400ms |
| Correlation p50 | < 100ms |
| p95 Latency | < 2x p50 |
| Error Rate | < 0.01% |
| Memory Growth | < 10%/hour |
| CPU per 1K events | < 100ms |

### 3. Response Orchestrator Benchmarks

#### Action Latency

| Action | Dry Run | Execution | Rollback |
|--------|---------|-----------|----------|
| Quarantine (NetworkPolicy) | < 100ms | < 500ms | < 300ms |
| Scale Deployment | < 50ms | < 1s | < 500ms |
| Revoke SA Binding | < 50ms | < 500ms | < 300ms |
| Create Ticket | < 200ms | < 2s | < 1s |

#### Approval Workflow

| Metric | Target |
|--------|--------|
| Approval request creation | < 100ms |
| Dry-run generation | < 200ms |
| Approval processing | < 50ms |
| Audit log write | < 50ms |

#### Concurrent Actions

| Scenario | Max Concurrent | Target |
|----------|----------------|--------|
| Sequential | 1 | All < SLA |
| Parallel (3) | 3 | All < SLA |
| Burst (10) | 10 | 95% < SLA |

### 4. Emulation Controller Benchmarks

#### Scenario Execution

| Scenario | Events Generated | Duration | Target |
|----------|------------------|----------|--------|
| Auth Brute Force | 1000 | 5 min | 100% delivery |
| DNS Anomaly | 5000 | 10 min | 100% delivery |
| Traffic Spike | 10000 | 15 min | 100% delivery |
| Workload Violation | 100 | 2 min | 100% delivery |

#### Controller Overhead

| Metric | Target |
|--------|--------|
| Scenario start latency | < 1s |
| Event generation rate | > 1000/sec |
| Memory per scenario | < 100 MB |
| CPU per scenario | < 10% |

### 5. End-to-End Pipeline Benchmarks

#### Full Pipeline Latency

| Stage | Target Latency |
|-------|----------------|
| Event Ingestion (Redpanda) | < 10ms |
| Detection Processing | < 200ms |
| Alert Storage (PostgreSQL) | < 50ms |
| Alert → API Gateway | < 50ms |
| AI Copilot Analysis | < 5s |
| Dashboard Update | < 1s |
| **Total (Event → Dashboard)** | **< 6s** |

#### Full Scenario Test

```bash
# Complete smoke test
make smoke-test
```

**Scenario**:
1. Auth simulator generates 100 failed login events
2. Redpanda ingests events
3. Detection engine correlates and creates alert
4. Alert stored in PostgreSQL
5. API Gateway serves alert to console
6. AI Copilot generates triage summary
7. Incident created
8. Response action requested
9. Dry-run executed
10. Approval granted
11. NetworkPolicy applied
12. Audit log verified

**Target**: Complete in < 60 seconds

### 6. Infrastructure Benchmarks

#### Database (PostgreSQL)

| Operation | Target |
|-----------|--------|
| Simple SELECT | < 5ms |
| Complex JOIN (10 tables) | < 100ms |
| INSERT (batch 1000) | < 200ms |
| VACUUM ANALYZE (10GB) | < 60s |
| Backup (10GB) | < 300s |
| Restore (10GB) | < 600s |

#### Redpanda

| Metric | Target |
|--------|--------|
| Produce latency (p99) | < 5ms |
| Consume latency (p99) | < 10ms |
| Throughput (per broker) | > 100 MB/s |
| Partition rebalance | < 30s |

#### Qdrant

| Operation | Target |
|-----------|--------|
| Vector insert (1000) | < 500ms |
| Search top-10 (100K vecs) | < 10ms |
| Search top-10 (1M vecs) | < 50ms |
| Collection rebuild (100K) | < 30s |

#### MinIO

| Operation | Target |
|-----------|--------|
| PUT (100 MB) | < 5s |
| GET (100 MB) | < 3s |
| List (10000 objects) | < 1s |

## Test Execution

### Automated Benchmark Suite

```bash
# Run all benchmarks
make benchmark-all

# Individual suites
make benchmark-ai
make benchmark-detection
make benchmark-response
make benchmark-emulation
make benchmark-e2e
make benchmark-infra

# With custom parameters
BENCH_VUS=50 BENCH_DURATION=20m make benchmark-detection
```

### CI/CD Integration

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmarks
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly
  workflow_dispatch:
    inputs:
      suite:
        type: choice
        options: [ai, detection, response, e2e, all]
jobs:
  benchmark:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Run Benchmarks
        run: make benchmark-${{ github.event.inputs.suite || 'all' }}
      - name: Compare with Baseline
        run: python scripts/compare_benchmarks.py
      - name: Alert on Regression
        if: failure()
        run: gh issue create --title "Performance Regression" --body "Benchmarks failed"
```

### Results Analysis

```python
# scripts/compare_benchmarks.py
import json
import sys

def compare(current_file, baseline_file, threshold=0.10):
    with open(current_file) as f:
        current = json.load(f)
    with open(baseline_file) as f:
        baseline = json.load(f)
    
    regressions = []
    for test, current_val in current.items():
        if test in baseline:
            baseline_val = baseline[test]
            change = (current_val - baseline_val) / baseline_val
            if change > threshold:
                regressions.append({
                    'test': test,
                    'baseline': baseline_val,
                    'current': current_val,
                    'change_pct': change * 100
                })
    
    if regressions:
        print("REGRESSIONS DETECTED:")
        for r in regressions:
            print(f"  {r['test']}: {r['baseline']:.2f} -> {r['current']:.2f} ({r['change_pct']:.1f}%)")
        sys.exit(1)
    else:
        print("No significant regressions detected")
        sys.exit(0)

if __name__ == "__main__":
    compare(sys.argv[1], sys.argv[2])
```

## Reporting

### Benchmark Report Template

```markdown
# AegisForge Benchmark Report
**Date**: {{date}}
**Commit**: {{commit_hash}}
**Environment**: {{environment}}
**Runner**: {{runner_spec}}

## Summary
| Suite | Status | Tests | Passed | Failed |
|-------|--------|-------|--------|--------|
| AI Copilot | ✅ Pass | 12 | 12 | 0 |
| Detection Engine | ✅ Pass | 8 | 8 | 0 |
| Response Orchestrator | ✅ Pass | 6 | 6 | 0 |
| End-to-End | ✅ Pass | 4 | 4 | 0 |

## Key Metrics

### AI Copilot
| Test | p50 | p95 | Target | Status |
|------|-----|-----|--------|--------|
| Incident Summary | 3.2s | 4.8s | <5s | ✅ |
| Alert Triage | 2.1s | 3.8s | <4s | ✅ |
| Report Generation | 18.5s | 28.3s | <30s | ✅ |

### Detection Engine
| Test | p50 | p95 | Target | Status |
|------|-----|-----|--------|--------|
| 1K events/sec | 45ms | 85ms | <100ms | ✅ |
| 10K events/sec | 180ms | 320ms | <300ms | ✅ |

## Resource Utilization
| Component | CPU Avg | CPU Peak | Mem Avg | Mem Peak |
|-----------|---------|----------|---------|----------|
| Ollama | 45% | 78% | 2.1 GB | 3.2 GB |
| Detection Engine | 32% | 65% | 1.2 GB | 1.8 GB |
| PostgreSQL | 15% | 40% | 2.5 GB | 3.5 GB |

## Regressions
None detected.

## Recommendations
1. Consider upgrading to llama3.2:3b for improved accuracy (tested: +15% latency)
2. Increase Qdrant replicas for HA
3. Add connection pooling for PostgreSQL (PgBouncer)
```

## Continuous Benchmarking

### Scheduled Runs
- **Daily**: Light benchmarks (10 min)
- **Weekly**: Full suite (2 hours)
- **Per Release**: Full suite + comparison

### Alerting
```yaml
# Prometheus alerting rules
- alert: BenchmarkRegression
  expr: |
    (benchmark_latency_p95 / benchmark_latency_p95_baseline) > 1.2
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Benchmark regression detected"
    description: "{{ $labels.test }} latency increased by {{ $value | humanizePercentage }}"
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Classification: Internal*