# ASCEND - Atlassian Bamboo

Reference plan for ASCEND **Layer 1** (source analysis) and **Layer 2** (container + IaC) on Bamboo.

The other platform packs ship a four-layer sketch. Several of those Layer-2 "quality gates" only echo `PASS` after the scanners have already run. This pack is narrower on purpose: it is the two layers that actually block a build, and the veto is a real script (`scripts/severity_gate.py`) with unit tests.

## Files

| File | Purpose |
|------|---------|
| [`bamboo.yaml`](./bamboo.yaml) | Bamboo Specs YAML v2 - four stages, parallel L1/L2 jobs |
| [`agent-scripts/`](./agent-scripts/) | Same jobs as shell, for servers that do not load YAML Specs |
| [`../../scripts/severity_gate.py`](../../scripts/severity_gate.py) | Shared veto used by QG1 and QG2 |
| [`../../quality-gates/severity-policy.json`](../../quality-gates/severity-policy.json) | Default CRITICAL=0 / HIGH budget |

## What the plan enforces

**Quality Gate 1** (after Semgrep + Bandit + Gitleaks):

- Critical findings = 0 (Semgrep `ERROR`, Bandit `HIGH`, any Gitleaks hit)
- High findings <= `ASCEND_HIGH_THRESHOLD` (default 5)

**Quality Gate 2** (after Trivy + Checkov):

- Critical findings = 0
- High findings = 0

Set `ASCEND_MODE=warning-only` on the plan variables to collect findings for 2-4 weeks without failing the build, then switch to `enforce`.

## Prerequisites

- Bamboo 6.8+ with Docker capability on Linux agents (or remote Docker)
- Git repository linked to the plan so Specs YAML can be scanned, or a Specs repository that publishes this file
- Copy `scripts/severity_gate.py` into the application repository (or check this whole tree out as a sibling and point the script path at it)

Paid tools are optional. If the Bamboo server already has SonarQube or Snyk, add a job that writes SARIF and pass those files to `--sarif` on the same QG script.

## Setup

### 1. Vendor the veto script

```bash
mkdir -p scripts
curl -fsSL -o scripts/severity_gate.py \
  https://raw.githubusercontent.com/venkatapgummadi/ascend/main/scripts/severity_gate.py
```

Until this branch is merged, use the commit SHA of the pull request instead of `main`.

### 2. Add the Specs file

```bash
cp platforms/bamboo/bamboo.yaml /path/to/your/repo/bamboo.yaml
```

Link the repository in Bamboo: **Plan configuration -> Repositories**, then **Specs** status should show the YAML imported.

Project key `ASCEND` and plan key `L12` are placeholders. Change them to keys that already exist on your Bamboo server.

### 3. Calibrate, then enforce

1. Set plan variable `ASCEND_MODE` = `warning-only`.
2. Run against a representative branch for two to four weeks.
3. Suppress noisy rules in `quality-gates/semgrep-rules.yml` / Checkov skip lists.
4. Set `ASCEND_MODE` = `enforce`.

## Agent-script fallback

If the Bamboo server does not import YAML Specs, create a plan with four stages and paste the matching file from `agent-scripts/` into each script task. Download shared artifacts between stages the same way the YAML plan does.

```bash
# on a Linux agent with Docker, from the application checkout
bash platforms/bamboo/agent-scripts/l1-semgrep.sh
bash platforms/bamboo/agent-scripts/l1-bandit.sh
bash platforms/bamboo/agent-scripts/l1-gitleaks.sh
bash platforms/bamboo/agent-scripts/qg1.sh
bash platforms/bamboo/agent-scripts/l2-trivy.sh
bash platforms/bamboo/agent-scripts/l2-checkov.sh
bash platforms/bamboo/agent-scripts/qg2.sh
```

`qg1.sh` / `qg2.sh` fail the job in `enforce` mode when the threshold is exceeded.

## Progressive rollout

Same pattern as the other platforms: warning-only first, then fail the build. The veto script's `--mode warning-only` flag is the Bamboo equivalent of wrapping a Jenkins `sh` in `catchError`.
