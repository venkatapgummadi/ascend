# ASCEND — GitHub Actions

Full reference configuration for the ASCEND framework on GitHub Actions.

## Files

- [`ascend-full.yml`](./.github/workflows/ascend-full.yml) — Complete four-layer pipeline.

## Setup

### 1. Copy the workflow

```bash
mkdir -p /path/to/your/repo/.github/workflows
cp .github/workflows/ascend-full.yml /path/to/your/repo/.github/workflows/
```

### 2. Configure repository secrets

Navigate to `Settings → Secrets and variables → Actions` and add:

| Secret | Purpose | Required |
|--------|---------|----------|
| `SONAR_TOKEN` | SonarQube / SonarCloud authentication | Yes (if using Sonar) |
| `SONAR_HOST_URL` | SonarQube server URL | Yes (if using Sonar) |
| `SNYK_TOKEN` | Snyk API token | Yes (if using Snyk) |
| `SEMGREP_APP_TOKEN` | Semgrep SaaS token | Optional |
| `FOSSA_API_KEY` | FOSSA license compliance | Optional |
| `ASCEND_SYNC_WEBHOOK` | AI Sync service webhook URL | Optional (Layer 4) |

### 3. Enable GitHub Advanced Security (if available)

GitHub Advanced Security enables native SARIF result display in pull requests and provides:
- CodeQL scanning integration
- Secret scanning with push protection
- Dependency review action

Available for all public repos. For private repos, requires GHAS license.

### 4. Configure branch protection

Go to `Settings → Branches → Branch protection rules` and require the following status checks before merging:

- `L1 / Quality Gate 1`
- `L2 / Quality Gate 2`

This enforces Layer 1 and Layer 2 gates as blocking before merge. Layer 3 gates enforce at deployment time.

## Quality gate tuning

Adjust thresholds at the top of the workflow file:

```yaml
env:
  ASCEND_QUALITY_GATE_MIN: "0.85"     # Composite quality score
  ASCEND_CRITICAL_THRESHOLD: "0"      # Max critical vulns allowed
  ASCEND_HIGH_THRESHOLD: "5"          # Max high vulns allowed
```

## Progressive rollout

The NIST DevSecOps guidelines recommend starting with warning-only mode. To do this:

1. Keep all scans enabled.
2. Change `exit-code: "1"` to `exit-code: "0"` in Trivy step.
3. Change `soft_fail: false` to `soft_fail: true` in Checkov step.
4. Remove `--fail` from TruffleHog args.
5. Review reports for 2–4 weeks, calibrate thresholds, then re-enable blocking mode.

## Troubleshooting

**CodeQL matrix job fails for a language not in your project:** Remove that language from the matrix.

**SonarQube Quality Gate times out:** Increase `timeout-minutes` or check that the quality profile is defined in your SonarQube server.

**Trivy blocks on unfixable CVE:** The `ignore-unfixed: true` setting should skip these. If it doesn't, add specific CVEs to `.trivyignore`.
