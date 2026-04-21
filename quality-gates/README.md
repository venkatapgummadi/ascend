# Quality Gate Configurations

Reference configurations for the scanning tools integrated with ASCEND. Each tool has recommended settings tuned to the quality gate thresholds described in the paper.

## Tool catalog

| Tool | Type | Config file | Purpose |
|------|------|-------------|---------|
| SonarQube | SAST | [`sonarqube-quality-gate.json`](./sonarqube-quality-gate.json) | Comprehensive multi-language SAST |
| Semgrep | SAST | [`semgrep-rules.yml`](./semgrep-rules.yml) | Fast semantic scanning |
| CodeQL | SAST | GitHub-native | Deep semantic queries |
| Snyk | SCA | `.snyk` (per repo) | Dependency vulnerability scanning |
| Trivy | SCA + Container | [`trivyignore.example`](./trivyignore.example) | Container + IaC + dependency scanning |
| OWASP ZAP | DAST | [`zap-rules.tsv`](./zap-rules.tsv) | Dynamic web application scanning |
| Checkov | IaC | [`checkov-config.yml`](./checkov-config.yml) | Terraform / K8s / CloudFormation policy checks |
| TruffleHog | Secrets | [`trufflehog-config.yml`](./trufflehog-config.yml) | Verified secret detection |

## Quality Gate thresholds

The composite quality score is computed as:

```
Q = Σ(w_i * q_i) / Σ(w_i)
```

Default weights:

| Tool | Weight | Per-scanner threshold |
|------|--------|-----------------------|
| SonarQube | 0.25 | Quality Gate = PASS |
| Semgrep | 0.20 | No findings at ERROR level |
| CodeQL | 0.20 | No critical security findings |
| Snyk | 0.15 | No high/critical with known fix |
| Trivy | 0.10 | No critical in non-dev dependencies |
| Checkov | 0.05 | No CRITICAL violations |
| TruffleHog | 0.05 | Zero verified secrets |

The pipeline fails if `Q < 0.85` OR any of: critical vulnerability count > 0, high vulnerability count > 5, verified secret count > 0.

## Progressive rollout

Start all tools in reporting-only mode. Measure baseline findings over 2–4 weeks. Calibrate thresholds. Switch to blocking mode one tool at a time.

See individual tool configuration files for specific thresholds and tunable parameters.
