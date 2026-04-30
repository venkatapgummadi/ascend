# ASCEND Architecture

## Overview

ASCEND is structured as four layers executed sequentially during the CI/CD pipeline, plus a continuous post-deployment synchronization component.

```
Developer commit
      │
      ▼
┌─────────────────────────────────────────────────┐
│ Layer 1: Source Analysis                         │
│   • SAST (parallel: SonarQube / Semgrep / CodeQL)│
│   • SCA (Snyk)                                   │
│   • Secrets (TruffleHog, Gitleaks)               │
│                    [ QG 1 ]                      │
└─────────────────────────────────────────────────┘
      │ pass
      ▼
┌─────────────────────────────────────────────────┐
│ Layer 2: Build & Integration                     │
│   • Container image scan (Trivy)                 │
│   • IaC scan (Checkov / KICS)                    │
│   • License compliance (FOSSA / pip-licenses)    │
│   • Integration tests                            │
│                    [ QG 2 ]                      │
└─────────────────────────────────────────────────┘
      │ pass
      ▼
┌─────────────────────────────────────────────────┐
│ Layer 3: Deployment Orchestration                │
│   • Deploy to staging (Blue / Green / Canary)    │
│   • DAST scanning (OWASP ZAP)                    │
│   • Synthetic transaction health checks          │
│                    [ QG 3 ]                      │
└─────────────────────────────────────────────────┘
      │ pass
      ▼
   Production
      │
      ▼
┌─────────────────────────────────────────────────┐
│ Layer 4: AI Synchronization                      │
│   • AST drift detection (every 6h)               │
│   • ML conflict classification                   │
│   • LLM-based resolution with verification       │
│   • Automated PR orchestration                   │
│                                                  │
│   (back-propagates hotfixes to upstream branches)│
└─────────────────────────────────────────────────┘
```

## Quality Gate Formalization

Each layer `i` implements a quality gate `G_i : R → {pass, fail}` over scan result set `R`. A build proceeds from stage `s` to stage `s+1` only if all gates in stage `s` pass:

```
Proceed(s) = ∧{i=1..n_s} G_i(R_i)
```

The composite pipeline quality score aggregates individual scanner scores:

```
Q = Σ(w_i * q_i) / Σ(w_i)
```

where `q_i ∈ [0, 1]` is the quality score for scanner `i` and `w_i` is its organizational weight. A build passes `QG` if `Q ≥ Q_min` (default `0.85`).

## Layer details

### Layer 1 — Source Analysis

Executes on every commit. Four parallel operations:

1. **SAST (multi-tool).** Running SonarQube + Semgrep + CodeQL in parallel adds negligible wall-clock time compared to any individual tool, while providing complementary vulnerability coverage.
2. **Secret detection.** Scans full commit history; verification queries prevent false positives on expired credentials.
3. **SCA.** Open-source dependency analysis against CVE databases.
4. **Linting & quality.** Language-specific style / complexity checks.

**Fail-fast design**: noncompliant code rejected before resource-intensive build stages run.

### Layer 2 — Build & Integration

Executes after Layer 1 passes:

1. **Container image scan.** Scans built images for vulnerable OS packages and application dependencies.
2. **IaC scan.** Validates Terraform, CloudFormation, Kubernetes, and Dockerfile configurations against CIS / NIST / SOC 2 policy frameworks.
3. **License compliance.** Prevents GPL contamination in commercial codebases.
4. **Integration tests.** Security-focused test cases in addition to functional integration tests.

### Layer 3 — Deployment Orchestration

Executes when promoting to staging / production:

1. **Multi-track deployment.** Supports blue-green, canary, and rolling strategies.
2. **DAST.** OWASP ZAP baseline or full scan against the deployed staging instance.
3. **Quality gates at each promotion boundary.** Prevents known-vulnerable builds from advancing.
4. **Automated rollback.** Triggers if post-deployment error rate exceeds 1% within a 30-minute window.

### Layer 4 — AI Synchronization

Runs continuously (not in-pipeline):

1. **Drift detection** on a 6-hour schedule, using AST differencing + configuration fingerprinting + embedding distance.
2. **Conflict classification** into `{syntactic, semantic, structural, configuration}`.
3. **LLM resolution** conditioned on `(c_ours, c_theirs, c_base, H)`.
4. **Verification** via property-based testing before PR creation.
5. **PR orchestration** with security-scanned automated pull requests for human review.

## Deployment strategy selection

| Property | Blue-Green | Canary | Rolling | Hotfix |
|----------|-----------|--------|---------|--------|
| Rollback | Instant | Fast | Slow | N/A |
| Infra cost | 2× | 1.1× | 1× | 1× |
| Traffic risk | None | Low | Medium | High |
| DAST coverage | Full | Partial | Partial | Minimal |
| Zero downtime | Yes | Yes | Yes* | No |
| Complexity | High | High | Medium | Low |
| Best for | Stateful apps | High-traffic services | Stateless APIs | Emergency CVE patches |

*With health checks.

## Reference configurations

See the [platforms/](../platforms/) directory for complete, runnable pipeline definitions:

- [GitHub Actions](../platforms/github-actions/)
- [GitLab CI/CD](../platforms/gitlab-ci/)
- [Jenkins](../platforms/jenkins/)
- [Azure DevOps](../platforms/azure-devops/)

## Further reading

- [Quality Gate specifications](./quality-gates.md)
- [Adoption roadmap](./adoption-guide.md)
- [AI Synchronization Module](../ai-sync/README.md)
- [Research paper](./paper/README.md)
