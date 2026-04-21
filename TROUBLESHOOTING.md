# Troubleshooting

Common issues encountered when deploying ASCEND, organized by layer.

## Layer 1 — Source Analysis

### "SonarQube Quality Gate check times out"

**Symptom:** CI job times out waiting for SonarQube to report quality gate status.

**Causes:**

1. SonarQube scanner analysis is still running; report publication takes longer than the default 5-minute timeout.
2. Quality profile for the project language is not defined.
3. Network connectivity between runner and SonarQube server is slow.

**Fix:**

```yaml
# GitHub Actions
- uses: SonarSource/sonarqube-quality-gate-action@master
  timeout-minutes: 15   # was 5
```

Also confirm the project exists in SonarQube (the scanner step should create it, but some configurations require explicit provisioning).

### "Semgrep findings flood the pipeline on first run"

**Symptom:** First Semgrep run reports hundreds of findings, blocking every PR.

**Fix:** Start with baselining. Run Semgrep against the base branch and suppress existing findings:

```bash
semgrep --config=p/owasp-top-ten --baseline-ref main
```

Then tighten rulesets incrementally. Typical progression:

1. `p/ci` — core correctness rules.
2. Add `p/owasp-top-ten` once core rules are clean.
3. Add `p/security-audit` once OWASP rules are clean.
4. Add language-specific rules last.

### "CodeQL matrix job fails for a language not in my repo"

**Symptom:** `CodeQL — python` fails because the repo has no Python files.

**Fix:** Remove unused languages from the matrix:

```yaml
strategy:
  matrix:
    language: [javascript, java]   # removed python
```

### "Snyk reports vulnerabilities in dev dependencies"

**Symptom:** `snyk test` fails on packages used only in development (linters, test frameworks).

**Fix:** Use `--dev false` to exclude dev dependencies, or add to `.snyk` ignore list:

```bash
snyk test --dev=false --severity-threshold=high
```

### "TruffleHog blocks on a test fixture that looks like a secret"

**Symptom:** Test fixture containing a mock AWS key or JWT is flagged.

**Fix:** TruffleHog's `--only-verified` flag should prevent this by checking if the credential is actually valid with the issuing service. If a fixture still triggers:

```yaml
# .trufflehog.yml
exclude:
  - "**/tests/fixtures/**"
  - "**/test/fixtures/**"
```

## Layer 2 — Build & Integration

### "Trivy scan blocks on CVEs in the base image that have no fix"

**Symptom:** `CRITICAL` vulnerability in a base image (often `libc`, `openssl`) with no upstream fix yet.

**Fix:** Use `--ignore-unfixed` to skip unfixable CVEs:

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    ignore-unfixed: true
```

For specific CVEs that have fixes but you can't yet apply, use `.trivyignore`:

```
CVE-2024-12345  # Unable to upgrade base image until Q3; documented in SECURITY_EXCEPTIONS.md
```

Always document why a CVE is ignored and set an expiration date.

### "Checkov flags a VPC default security group"

**Symptom:** Checkov CKV_AWS_* rule fails on AWS default security group or similar "managed by cloud provider" resources.

**Fix:** These are often intentional. Suppress at the resource level with a comment:

```terraform
# checkov:skip=CKV_AWS_23:Default SG is managed by VPC module
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id
}
```

### "License compliance scan blocks on a transitive GPL dependency"

**Symptom:** FOSSA or pip-licenses flags a GPL-licensed transitive dependency.

**Fix:** First, check whether you actually use the offending library. If yes:

1. Replace it with an MIT/Apache alternative (preferred).
2. Isolate GPL code as a separate service that communicates over a network interface (the "aggregation" exception).
3. Obtain legal sign-off and add to the approved GPL list in the license compliance config.

Do not silently whitelist — GPL contamination is a real legal risk for commercial software.

## Layer 3 — Deployment & DAST

### "OWASP ZAP baseline scan takes 30+ minutes"

**Symptom:** ZAP baseline scan significantly exceeds the expected 8–12 minute duration.

**Causes:**

1. Staging instance is slow to respond (underprovisioned).
2. Scan is following too many links (`spider` depth too high).
3. Authentication is failing and ZAP is stuck at the login page.

**Fix:**

- Right-size the staging environment to match production resource allocation.
- Limit scan scope:
  ```bash
  zap-baseline.py -t https://staging.example.com -I -j -m 2
  # -m 2: max spider depth
  ```
- Configure authentication explicitly via ZAP's `-z` flag or a scripted login.

### "Blue-green deployment leaves two slots running indefinitely"

**Symptom:** After a successful traffic switch, the old slot continues consuming infrastructure resources.

**Fix:** ASCEND's default behavior retains the old slot for a 30-minute rollback window. After that, teardown should run automatically. If it doesn't:

1. Check the post-switch teardown job in your CI config.
2. Verify Kubernetes deployment history is set to a small number (`revisionHistoryLimit: 3`).
3. Ensure cloud provider cleanup runs (AWS Elastic Beanstalk, Azure Web App deployment slots have their own cleanup schedules).

### "Canary error rate briefly spikes above threshold and auto-rolls back even though deploy is fine"

**Symptom:** Canary deployment rolls back due to a transient error spike in the first seconds after traffic shift.

**Fix:** Extend the observation window:

```yaml
ASCEND_CANARY_OBSERVATION_MINUTES: 15   # was 5
ASCEND_CANARY_ERROR_THRESHOLD: 0.05     # 5% — tune to your baseline
```

Also consider the canary ramp: rolling from 0% to 10% to 50% to 100% rather than 0% to 100% gives the system time to warm up before taking measurements.

## Layer 4 — AI Synchronization

### "AI sync creates too many low-value PRs"

**Symptom:** The PR orchestrator opens PRs for conflicts that humans easily resolve.

**Fix:** Raise the confidence threshold:

```yaml
# ai-sync/config.yml
classification:
  confidence_threshold: 0.90   # was 0.85
```

Or restrict AI sync to specific conflict types:

```yaml
resolution:
  allowed_types: [syntactic, configuration]   # exclude semantic, structural
```

### "AI resolver returns `CANNOT_RESOLVE` for most conflicts"

**Symptom:** The LLM consistently outputs `CANNOT_RESOLVE`, producing no useful resolutions.

**Causes:**

1. Conflict context is missing the base version (three-way merge requires base).
2. Model is too small for the task — try a larger model.
3. System prompt is too conservative — the provided prompt prioritizes caution.

**Fix:** Ensure `conflict.base` is populated before calling `resolver.resolve()`. If using a local stub, upgrade to a real provider:

```bash
ascend-sync resolve --provider openai --model gpt-4o --file conflict.json
```

### "Drift detector reports false positives on branches that are semantically identical"

**Symptom:** Pure formatting changes (black/prettier reformat, whitespace) trigger drift alerts.

**Fix:** AST-based detection should handle this, but if it doesn't, verify:

1. Files parse cleanly (check with `python -m py_compile file.py`).
2. Whitespace-insensitive hashing is active (the DriftDetector hashes AST signatures, not source text).
3. For files the AST detector can't parse (non-Python languages), it falls back to line-count diff which is whitespace-sensitive.

## Cross-cutting issues

### "All scans pass locally but fail in CI"

**Symptom:** Works on my machine; broken in CI.

**Common causes:**

1. **Different tool versions.** Pin all scanner versions in the pipeline: `uses: snyk/actions/setup@master` downloads latest; pin to `@v1.4.0`.
2. **Different dependency lock files.** CI uses `package-lock.json` or `poetry.lock`; local uses cached resolution.
3. **Environment variables.** Missing CI-only env vars fail gracefully locally but break in CI.
4. **Network restrictions.** CI runners often cannot reach external tool registries; mirror critical dependencies.

### "Quality Gate 2 blocks a hotfix that needs to go out immediately"

**Symptom:** Emergency security patch needs to skip quality gates to reach production faster.

**Fix:** Use the hotfix track. The paper's architecture defines a dedicated hotfix path with reduced gates:

```
Hotfix track:
  L1 scans (fast): SAST + Secrets only (no SCA deep scan)
  L3 scans (fast): DAST baseline only
  AI back-propagation: automatic within 15 minutes
```

Configure in your pipeline:

```yaml
on:
  push:
    branches: [hotfix/**]

jobs:
  hotfix-expedited:
    runs-on: ubuntu-latest
    # Skip Layer 2 license/container deep scan; use only fast gates
```

Never disable all gates entirely — the hotfix track should still run SAST and secret scanning. The accelerated path trades comprehensiveness for speed, not safety.

### "Pipeline passes but production still has vulnerabilities"

**Symptom:** ASCEND claims clean builds, but production monitoring or penetration tests find issues.

**Causes:**

1. **False negatives.** No tool catches 100% of issues; the paper reports 96% combined coverage. Residual vulnerabilities reach production.
2. **Runtime-only vulnerabilities.** SQL injection in a query constructed via dynamic config is invisible to SAST.
3. **Supply chain vulnerabilities disclosed after the last scan.** New CVEs emerge daily; a clean scan at deploy time doesn't guarantee a clean scan a week later.

**Fix:**

- Schedule nightly re-scans of deployed versions against latest vulnerability databases.
- Integrate RASP for runtime protection (out of scope for ASCEND itself).
- Feed production incident root causes back into Semgrep rules or SonarQube profiles so the same defect class doesn't reach production twice.

## Getting help

If your issue isn't listed here:

1. Check the [FAQ](./FAQ.md).
2. Search [existing issues](https://github.com/venkatapgummadi/ascend/issues).
3. Open a new issue with the bug report template.
4. For security issues in ASCEND itself, follow [SECURITY.md](./SECURITY.md).
