# Adoption Guide

ASCEND is designed for incremental adoption. This guide presents a phased rollout plan that de-risks deployment and lets organizations realize value quickly.

## Decision tree: should you adopt ASCEND?

**You are a good fit if:**

- You deploy to production at least weekly.
- You operate multi-track branches (development / staging / production / hotfix).
- You have an existing CI/CD platform (GitHub Actions / GitLab / Jenkins / Azure DevOps).
- You have regulatory or audit requirements (SOC 2, PCI DSS, HIPAA, NIST).
- Your security review process is currently a manual / async bottleneck.

**You may want to start smaller if:**

- You have < 5 engineers and < 10 deploys per month — start with a single SAST tool first.
- You use a CI platform not yet covered by reference configurations (CircleCI, TeamCity, Bamboo). You'll be writing the first platform reference; consider contributing it back.
- You have no historical merge conflict data — Layer 4 model training needs at least 500 resolved conflicts.

## Phase 1 — Layer 1 (Week 1–2)

**Goal:** catch 80%+ of security-relevant issues before they reach production.

**Activities:**

1. Copy the platform-specific Layer 1 workflow into your repository.
2. Configure required secrets (SonarQube, Snyk, etc.).
3. Run in *warning-only* mode for 2 weeks — no blocking, only reporting.
4. Review results weekly. Suppress noisy rules. Tune thresholds.
5. Switch to *enforce* mode.

**Exit criteria:**

- SAST + SCA + Secret detection running on every commit.
- Quality Gate 1 is enforced (blocks PR merge on failure).
- Baseline metrics captured: vulnerabilities detected per week, false positive rate, build duration impact.

**Typical outcomes:** ~80% reduction in security-relevant issues reaching later stages.

## Phase 2 — Layer 2 (Week 3–8)

**Goal:** extend coverage to container images and infrastructure-as-code.

**Activities:**

1. Add Trivy for container and OS package scanning.
2. Add Checkov (or KICS) for IaC policy enforcement.
3. Add license compliance scanning (FOSSA or open-source alternatives).
4. Run integration tests as part of the build gate.
5. Calibrate Quality Gate 2 thresholds.

**Exit criteria:**

- Container images and IaC files scanned on every commit.
- License compliance enforced.
- QG2 in enforce mode.

**Typical outcomes:** IaC misconfigurations drop dramatically (they typically represent ~30% of findings on first scan).

## Phase 3 — Layer 3 (Week 9–14)

**Goal:** automated deployment with security gates at each promotion boundary.

**Activities:**

1. Adopt a deployment strategy: blue-green (stateful apps), canary (high-traffic), or rolling (stateless APIs).
2. Add DAST (OWASP ZAP) scanning of staging deployments.
3. Configure synthetic health checks.
4. Implement automated rollback on quality gate 3 failure.
5. Configure 30-minute post-switch observation window.

**Exit criteria:**

- Deployments automated with zero-downtime guarantees.
- QG3 enforced.
- Automated rollback tested with a synthetic failure scenario.

**Typical outcomes:** deployment frequency increases substantially as manual security review is no longer a bottleneck. Failed deployment rate drops meaningfully.

## Phase 4 — Layer 4 (Week 15+)

**Goal:** automated drift detection and AI-powered synchronization across branches.

**Activities:**

1. Install the AI sync module on a management host.
2. Configure initial drift detection on a 24-hour schedule (increase frequency once stable).
3. Train the conflict classifier on your historical merge conflicts (minimum 500 required).
4. Configure LLM provider (OpenAI / Anthropic / self-hosted).
5. Run in shadow mode for 2 weeks — classifier and resolver run but do not open PRs.
6. Review shadow-mode predictions with the team; calibrate confidence thresholds.
7. Enable automated PR creation for high-confidence resolutions.

**Exit criteria:**

- Drift detection running on schedule.
- AI sync creating PRs for syntactic and configuration conflicts at high confidence.
- Semantic and structural conflicts flagged for human review only.

**Typical outcomes:** significant reduction in manual effort for merge conflict resolution, especially for back-propagating hotfixes from production to development branches.

## Common pitfalls

**Turning on all scanners at once.** Too noisy; teams get alert fatigue. Adopt one tool at a time and tune before adding the next.

**Skipping warning-only mode.** Blocking builds on day 1 frustrates developers. Warning-only for 2 weeks is the single highest-ROI practice.

**No ownership.** Each scanner needs an owner who maintains rules, thresholds, and suppressions. Without ownership, suppressions accumulate silently.

**Treating AI sync as autonomous.** Layer 4 creates PRs; it does not merge them. Human review of every AI-generated PR is required.

## Metrics to track

To demonstrate ASCEND ROI internally, capture these metrics before adoption and 6 months after:

| Metric | Definition |
|--------|------------|
| Critical vulns in production | Count of CVEs found in prod over a 13-week window |
| Mean detection time | Time from code commit to vulnerability detection |
| Mean remediation time | Time from detection to deploy of fix |
| Deployment frequency | Deploys per week |
| Failed deployment rate | % of deploys that fail or roll back |
| Merge conflict resolution time | Avg time from conflict detection to resolved merge |
| Security review lead time | Time a PR waits for security review |

If your organization runs the NIST Cybersecurity Framework or a DORA metrics baseline, these map directly to ASCEND's Layer 1–4 coverage.
