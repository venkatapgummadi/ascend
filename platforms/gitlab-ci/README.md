# ASCEND — GitLab CI/CD

Full reference configuration for the ASCEND framework on GitLab CI/CD.

GitLab provides the lowest-friction integration of the four supported platforms — native security scanning templates can be enabled with a single `include:` directive, and results flow directly into the merge request security dashboard.

## Files

- [`.gitlab-ci.yml`](./.gitlab-ci.yml) — Complete four-layer pipeline.

## Setup

### 1. Copy the configuration

```bash
cp .gitlab-ci.yml /path/to/your/repo/.gitlab-ci.yml
```

### 2. Configure CI/CD variables

Go to `Settings → CI/CD → Variables` and add:

| Variable | Type | Purpose |
|----------|------|---------|
| `ASCEND_SYNC_WEBHOOK` | Variable | URL for the AI Sync service (Layer 4) |
| `SAST_EXCLUDED_PATHS` | Variable | Paths to exclude from SAST (overrides default) |
| `DAST_WEBSITE` | Variable | Staging URL for DAST scanning |

### 3. Enable required scanners in GitLab

GitLab's native templates run automatically once included in the CI file. Verify in `Secure → Security configuration` that:

- SAST is enabled
- Secret Detection is enabled
- Dependency Scanning is enabled
- Container Scanning is enabled
- DAST is enabled (staging URL configured)

### 4. Merge request approval rules

Require security approval in `Settings → Merge requests → Merge request approvals`:

- Require approval when vulnerabilities are detected
- Minimum approvers from Security team: 1

## Progressive rollout

Start in reporting-only mode by commenting out `quality-gate-1` and `quality-gate-2` jobs. Collect scan results for 2–4 weeks. Calibrate thresholds:

```yaml
variables:
  ASCEND_CRITICAL_THRESHOLD: "0"
  ASCEND_HIGH_THRESHOLD: "5"
```

Then re-enable the quality gate jobs.

## Merge request security dashboard

GitLab's merge request security dashboard automatically displays:

- Vulnerability introductions vs. fixes
- SAST, DAST, SCA, and Container findings grouped by severity
- Remediation suggestions from Dependency Scanning

No additional configuration required.
