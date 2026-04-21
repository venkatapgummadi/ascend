# Metrics and KPIs

This document describes what to measure when adopting ASCEND, how to measure it, and what good looks like. Measuring outcomes (not just activity) is what separates a successful DevSecOps program from a checklist exercise.

## The four categories

ASCEND improvements fall into four measurable categories:

1. **Security posture** — vulnerabilities detected, where, and how fast.
2. **Deployment velocity** — how often and how reliably you ship.
3. **Developer experience** — the human cost of running the pipeline.
4. **Compliance and audit readiness** — evidence artifacts available on demand.

## Before you start: capture a baseline

Before adopting ASCEND, spend 2–4 weeks collecting these metrics from your existing pipeline. Without a baseline, you cannot demonstrate improvement.

## Security posture metrics

### Critical vulnerabilities reaching production

```
Critical Vulns / Week = count of CRITICAL CVEs detected in production runtime
                        / weeks in measurement window
```

**How to capture:** runtime security tools (AWS Security Hub, GCP SCC, Azure Defender, Wiz, Prisma Cloud, etc.) or your SIEM.

**What good looks like:** after Phase 1 adoption, this should drop by 70–85% within 13 weeks.

### Mean Detection Time (MDT)

Time from code commit to vulnerability detection.

```
MDT = mean(detection_timestamp - commit_timestamp) across all findings
```

**How to capture:** scan reports include timestamps. Correlate with `git log`.

**What good looks like:** baseline is typically 24–72 hours (manual review cycles). Post-ASCEND is typically 10–20 minutes (build-gated scan completes within the pipeline window).

### Mean Remediation Time (MRT)

Time from detection to deploy of fix.

```
MRT = mean(fix_deploy_timestamp - detection_timestamp)
```

**How to capture:** correlate scan report timestamps with deployment history.

**What good looks like:** baseline is typically 40–60 hours. Post-ASCEND typically drops to 5–10 hours because developers receive inline PR comments rather than async security team reports.

### False Positive Rate (FPR)

```
FPR = false positives / total findings
```

**How to capture:** classify each finding as true or false positive over a sample period (at least 200 findings).

**What good looks like:** 8–12% is typical for mature multi-tool configurations. Under 20% on a single-tool pipeline. Above 30% suggests rule tuning is needed.

### Security debt

Count of known vulnerabilities in production that haven't been fixed yet.

```
Security Debt = count of open findings with severity >= HIGH that are older than 30 days
```

**How to capture:** scanner dashboards or security tooling.

**What good looks like:** declining trend. Absolute number depends on codebase age; trajectory matters more than magnitude.

## Deployment velocity metrics (DORA)

ASCEND should *improve* deployment velocity, not slow it down. The [DORA metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance) are the right yardstick.

### Deployment Frequency

```
Deployments / Week = count of production deployments
```

**What good looks like:** typically increases 50–200% after ASCEND adoption — not because ASCEND makes deployment faster, but because it removes the manual security review bottleneck.

### Lead Time for Changes

```
Lead Time = mean(deploy_timestamp - commit_timestamp)
```

**What good looks like:** flat or improving. If lead time increases significantly, the pipeline is over-gated — tune thresholds.

### Change Failure Rate

```
CFR = failed_deployments / total_deployments
```

**What good looks like:** drops from typical 12–18% to 3–6% after adoption.

### Time to Restore Service

For incidents caused by code defects (not infrastructure):

```
MTTR = mean(incident_resolved_timestamp - incident_start_timestamp)
```

**What good looks like:** improves because ASCEND's hotfix track with AI back-propagation accelerates the fix-and-backport cycle.

## Developer experience metrics

### Build duration at each layer

```
L1 Duration = mean(duration of Layer 1 jobs)
L2 Duration = mean(duration of Layer 2 jobs)
L3 Duration = mean(duration of Layer 3 jobs — staging deploy + DAST)
Total Pipeline Duration = mean(commit to production-ready artifact)
```

**What good looks like:** full pipeline under 30 minutes for typical services. L1 under 15 minutes. DAST frequently dominates L3; consider nightly scheduling if L3 duration is prohibitive.

### Security-blocked build rate

```
Security-Blocked = count(builds failed on L1, L2, or L3 quality gate)
                   / total builds
```

**What good looks like:** 5–15% after calibration. Higher than 25% indicates gates are too strict or there is significant security debt. Lower than 3% may mean gates are too permissive.

### Developer friction survey

A quarterly 5-question survey:

> 1. How often does the security pipeline block a PR you needed to merge? (Never / Rarely / Sometimes / Often / Always)
> 2. How clear are the pipeline's error messages when something fails?
> 3. How often do you bypass or disable the pipeline to ship quickly?
> 4. Has the pipeline caught issues you would have otherwise shipped?
> 5. How would you rate the pipeline's net impact on your productivity?

**What good looks like:** Q3 "Never" > 95%. Q5 mean > 7/10 within 6 months.

### Time spent resolving merge conflicts

```
Weekly Conflict Time = hours per developer per week resolving merge conflicts
```

**How to capture:** developer self-report survey, or derive from `git reflog` and PR metadata.

**What good looks like:** industry baseline is approximately 4–5 hours/week. With Layer 4 AI sync fully active, expect meaningful reduction — though the improvement varies significantly by codebase and team practices.

## Compliance metrics

### Audit evidence availability

For each compliance framework you're subject to, measure whether evidence is available on demand:

| Framework | Evidence item | Target: available in minutes |
|-----------|---------------|------------------------------|
| SOC 2 CC8.1 | Change management records | Yes |
| SOC 2 CC7.1 | Threat detection history | Yes |
| PCI DSS 6.3.2 | Code inventory with severity | Yes |
| PCI DSS 6.4.1 | Web app protection scan results | Yes |
| NIST CSF ID.RA-1 | Asset vulnerability reports | Yes |
| HIPAA 164.312(b) | Audit trail | Yes |

ASCEND's pipeline artifacts (scan reports, quality gate outcomes, deploy records) provide this evidence automatically.

### Policy exception age

```
Exception Age = mean(today - exception_created_date) for all active exceptions
```

**What good looks like:** under 90 days. Exceptions should always have expiration dates; none should be "permanent."

## Dashboard template

A simple Grafana dashboard tracking ASCEND's impact. Wire the following metrics:

| Panel | Query source | Alert threshold |
|-------|-------------|-----------------|
| Critical vulns reaching prod (weekly) | Security tool API | > 0 |
| Mean detection time | CI pipeline logs | > 30 minutes |
| Deployment frequency | CI/CD deploy logs | declining trend |
| Change failure rate | CI/CD + incident tracker | > 10% |
| Pipeline security block rate | CI/CD logs | > 25% or < 2% |
| L1 mean duration | CI/CD logs | > 20 minutes |
| Open high/critical findings | Security tool API | growing trend |

Replicate per team and per service for accountability.

## Reporting cadence

| Audience | Cadence | Focus |
|----------|---------|-------|
| Engineering team | Daily (dashboard) | Pipeline health, build failures |
| Engineering leadership | Weekly | DORA metrics, security posture trends |
| Security leadership | Weekly | Vulnerability detection rates, critical findings |
| Executive team | Monthly | Risk posture, compliance readiness, ROI |
| Audit / compliance | Quarterly | Evidence completeness, exception inventory |

## ROI calculation

For budget conversations, estimate savings:

```
Savings per prevented late-stage vuln = (baseline_MRT - new_MRT) * $senior_engineer_hourly
```

Typical values:

- Baseline MRT: 40–60 hours.
- New MRT: 5–10 hours.
- Senior engineer loaded cost: $150–200/hour.

```
Savings per vuln ≈ 35 hours × $175 = $6,125
```

Multiply by your prevented vulnerability count:

```
Annual savings = prevented_vulns_per_year × savings_per_vuln
```

Compare against tooling costs (typically $50K–$150K/year for mid-size enterprise deployment). ROI is usually positive after 10–20 prevented late-stage vulnerabilities.

## Common measurement pitfalls

**Vanity metrics.** "Findings detected" goes up, but that's not progress — reaching-production count is what matters.

**Selection bias.** If you only measure on repos that adopted ASCEND, you miss the organization-wide picture. Compare against repos that haven't yet adopted.

**Hawthorne effects.** Teams perform differently when they know they're being measured. Bake measurement into normal operations so it's not an exception.

**Short evaluation windows.** 4 weeks isn't long enough. Aim for a 13-week baseline and 13-week post-adoption window.

**Confounding change.** Don't evaluate ASCEND in a period when the team also changed frameworks, migrated cloud providers, or reorganized. You can't attribute changes cleanly.

## Further reading

- Forsgren, Humble, and Kim. *Accelerate: The Science of Lean Software and DevOps.* IT Revolution Press, 2018.
- DORA metrics baseline: https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance
- NIST SP 800-55 Rev. 2: Performance Measurement Guide for Information Security.
