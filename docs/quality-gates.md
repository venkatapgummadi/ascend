# Quality Gate Specifications

ASCEND defines three explicit quality gates (`QG1`, `QG2`, `QG3`) and a continuous synchronization layer (`L4`). This document describes what each gate evaluates and how it is tuned.

## QG1 — End of Layer 1 (Source Analysis)

**Input scanners:** SAST (SonarQube, Semgrep, CodeQL), SCA (Snyk), Secret detection (TruffleHog).

**Pass criteria (all must be true):**

- SonarQube Quality Gate status = `PASS`
- Semgrep findings at `ERROR` level = 0
- CodeQL critical security findings = 0
- Snyk findings at `critical` severity with known fix = 0
- Snyk findings at `high` severity with known fix ≤ `ASCEND_HIGH_THRESHOLD` (default 5)
- TruffleHog verified secrets = 0

**Pass output:** proceed to Layer 2.

**Fail output:** pipeline terminates; developer receives inline PR comments with remediation guidance.

## QG2 — End of Layer 2 (Build & Integration)

**Input scanners:** Trivy (container + SCA), Checkov (IaC), FOSSA or pip-licenses (license compliance), integration test suite.

**Pass criteria:**

- Trivy critical vulnerabilities in image layers (excluding unfixed, excluding dev-only base images) = 0
- Checkov CRITICAL policy violations = 0
- No GPL / AGPL in the dependency graph for commercial codebases (configurable per repo)
- Integration test pass rate = 100%

**Pass output:** proceed to deployment.

**Fail output:** pipeline terminates; artifact is not published.

## QG3 — End of Layer 3 (Deployment)

**Input scanners:** OWASP ZAP baseline scan against staging, synthetic transaction health checks.

**Pass criteria:**

- ZAP findings at `FAIL` level (per [zap-rules.tsv](../quality-gates/zap-rules.tsv)) = 0
- Synthetic health check success rate ≥ 99% over 5-minute observation window
- Deployed version responds to `/healthz` or equivalent within SLA

**Pass output:** traffic switches to new production slot.

**Fail output:** deployment rolled back automatically; staging slot retained for investigation.

## Layer 4 — Continuous Synchronization

Layer 4 is not a blocking gate. It operates on a schedule (default every 6 hours) and after each production deployment.

**Drift threshold:** risk score `r > 0.30` triggers sync workflow.

**Conflict resolution confidence:** candidate resolutions with LLM confidence `≥ 0.85` are eligible for auto-PR creation. Below this threshold, the conflict is flagged for manual review only.

**Resolution verification:** all auto-created PRs must pass:

- Syntactic validity
- Function/class signature preservation
- Security pattern preservation (authentication, crypto, input validation, rate limiting)
- Property-based tests (when applicable)

## Gate calibration

Start each gate in *warning-only* mode:

```yaml
ASCEND_MODE: warning-only
```

Collect scan findings without blocking builds for 2–4 weeks. Use the aggregated results to:

1. Identify noisy rules to suppress.
2. Set realistic severity thresholds.
3. Calibrate the composite quality score weights.

Then transition to *enforce* mode:

```yaml
ASCEND_MODE: enforce
```

The progressive rollout pattern aligns with NIST DevSecOps guideline recommendations to avoid disrupting development workflow during initial adoption.

## Composite quality score

```
Q = Σ(w_i * q_i) / Σ(w_i)
```

Default weight configuration (tunable via CI environment variables):

| Scanner | Default weight | Description |
|---------|---------------|-------------|
| SonarQube | 0.25 | Comprehensive SAST |
| Semgrep | 0.20 | Fast semantic scanning |
| CodeQL | 0.20 | Deep semantic queries |
| Snyk | 0.15 | Dependency SCA |
| Trivy | 0.10 | Container + IaC |
| Checkov | 0.05 | IaC policy |
| TruffleHog | 0.05 | Verified secrets |

Pass threshold: `Q ≥ 0.85`.

Organizations with different risk appetites may adjust weights. For example, a security-first organization might weight secret detection at 0.15 and Checkov at 0.10.
