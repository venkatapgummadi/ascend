# Migration Guide

Moving from an existing CI/CD setup to ASCEND. This guide covers the three most common starting points.

## Starting point A: No security scanning today

You have a functional CI/CD pipeline but no automated security scanning. This is the simplest migration path.

### Week 1

1. Pick your platform configuration from `platforms/<your-platform>/`.
2. Copy the pipeline file into your repo under a new branch.
3. Do not enable as default. Run it manually via workflow_dispatch / manual trigger.
4. Observe: does the pipeline complete? What are the baseline findings?

### Week 2

5. Triage the initial findings. Distinguish:
   - Real issues that should be fixed.
   - False positives to suppress with documented reasons.
   - Dev-only issues out of scope for security review.
6. Configure baselines so existing issues are grandfathered.

### Week 3–4

7. Merge the pipeline into your default branch in *warning-only* mode.
8. Quality gates configured but non-blocking.
9. Daily review of findings with the engineering team. Tune noisy rules.

### Week 5–6

10. Switch Quality Gate 1 to *enforce* mode.
11. Keep Layer 2 / 3 in warning-only for another 2 weeks.
12. Observe developer reactions; adjust thresholds.

### Week 7+

13. Progressively enforce Layer 2, then Layer 3.
14. Add Layer 4 (AI sync) after the first three layers are stable for 4+ weeks.

**Timeline:** 8–12 weeks to full four-layer operation.

## Starting point B: Partial security scanning exists

You already run SonarQube, Snyk, or similar, but ad hoc — not integrated into quality gates, or running only nightly.

### Inventory first

Before migrating, document:

- Which tools run currently (name, version, where executed).
- Who owns each tool (individuals or teams).
- Which rules are active, which are suppressed, and why.
- Current false positive rate (rough estimate).
- Historical findings and remediation timelines.

### Migration approach: integrate, don't replace

ASCEND is pluggable. If you run SonarQube already, keep it — just move invocation into the ASCEND pipeline layer structure.

**Example:** you run SonarQube nightly via a separate job. Migration:

1. Move SonarQube invocation into the Layer 1 `sast-sonarqube` job in the ASCEND pipeline.
2. Change the cadence from nightly to per-commit.
3. Add the SonarQube Quality Gate check as a blocking step.

Do not try to swap SonarQube for Semgrep unless you have a specific reason. Tool migration is expensive and risky; integrate what you have.

### Resolving tool overlap

ASCEND configurations invoke multiple tools per scan type (SonarQube + Semgrep + CodeQL for SAST). If you already use one of these three, consider:

- **Keep it.** Multi-tool gives better coverage.
- **Add another.** The paper reports ~14% additional vulnerability coverage per tool added.
- **Don't add.** If you already have a robust single-tool configuration and your org won't support multi-tool, stick with one.

Configure ASCEND to invoke only the tools you want:

```yaml
# GitHub Actions — disable Semgrep if you only want SonarQube + CodeQL
jobs:
  sast-semgrep:
    if: false   # disabled
  sast-sonarqube:
    # ... runs ...
  sast-codeql:
    # ... runs ...
```

### Timeline

Partial-scanning starting points typically complete migration in 4–8 weeks because the organization already has security scanning mindset and tooling.

## Starting point C: Competing DevSecOps framework already deployed

You use GitLab Ultimate's native security dashboard, Snyk Full Pipeline, Veracode, or a commercial platform like Palo Alto Prisma Cloud Secure DevOps.

### Decide: integrate or replace

Most commercial DevSecOps platforms include:

- A scanning component (SAST / SCA / IaC).
- A dashboard / reporting layer.
- Policy enforcement.
- Some provide their own pipeline orchestration.

**Integrate** (keep the commercial platform):

- ASCEND contributes the open-source scanning tools (Semgrep, Trivy, OWASP ZAP) that commercial platforms may not include.
- Route ASCEND findings into the commercial dashboard via SARIF.
- Use ASCEND's AI synchronization module as a layer on top of the commercial pipeline.

**Replace** (remove the commercial platform):

- Expected cost savings: often $100K+/year for mid-size deployments.
- Expected risk: loss of vendor support, training, and established workflows.
- Typical timeline: 6–12 months with careful change management.

Most organizations integrate first, then evaluate replacement after 6+ months of parallel operation.

### Migration patterns

**Pattern 1: ASCEND as the orchestration layer.**

Use ASCEND's four-layer pipeline structure. Configure each layer to invoke commercial tools alongside (or instead of) the recommended open-source ones.

```yaml
# Example: Layer 1 uses Veracode instead of SonarQube + Semgrep
sast-veracode:
  runs-on: ubuntu-latest
  steps:
    - uses: veracode/veracode-pipeline-scan-action@v1.0.9
      with:
        # ... Veracode config ...
```

**Pattern 2: Commercial as orchestration, ASCEND components as supplement.**

Keep your commercial pipeline. Add ASCEND's AI synchronization module as a separate service:

```bash
# Commercial pipeline (existing) deploys to prod
# ASCEND Layer 4 runs separately on a 6-hour schedule
ascend-sync post-deploy-sync \
    --repo org/repo \
    --production-sha $(git rev-parse origin/main) \
    --target-branches develop,staging
```

**Pattern 3: Parallel operation.**

Run both systems on the same repo. ASCEND in warning-only mode, commercial system in enforce. After 13 weeks, compare findings. Then decide which to keep authoritative.

## Technical migration checklist

Regardless of starting point, verify before going live:

- [ ] All required secrets configured in CI platform.
- [ ] Branch protection rules updated to require ASCEND gates.
- [ ] Scanner versions pinned in pipeline configs.
- [ ] `.gitignore` excludes scan report artifacts.
- [ ] Baseline files (`.checkov.baseline`, `.snyk`, etc.) committed.
- [ ] Monitoring and alerting route to correct destinations.
- [ ] Runbook for common pipeline failures exists.
- [ ] On-call rotation includes someone familiar with the pipeline.

## Common migration issues

### "The pipeline doubles our build time."

Parallelize wherever possible. Don't run SonarQube + Semgrep + CodeQL sequentially. Consider moving DAST to nightly if per-commit impact is unacceptable.

### "Our team ignores the findings."

Findings without a clear owner get ignored. Assign findings to the PR author by default, and route critical findings to both author and security team. Track remediation SLAs in your metrics dashboard.

### "Our auditors say we can't use open-source scanners."

This is usually a misunderstanding. Open-source scanners produce the same SARIF outputs as commercial ones. What matters for audit is: evidence retention, access controls on the evidence, and documented review process. Open-source tools meet all three.

If your auditor insists on commercial tools specifically, use the commercial tools via the ASCEND pipeline structure.

### "We can't deploy Layer 4 because we can't send our code to OpenAI / Anthropic."

Use the local stub provider (`provider: local`) for offline operation, or deploy a self-hosted LLM:

- **Ollama**: easy to deploy; supports Llama 3.1, Mistral, CodeLlama.
- **vLLM**: higher throughput; supports many open weights.
- **Hugging Face TGI**: similar to vLLM.

All expose an OpenAI-compatible API; just point the OpenAI client at your internal endpoint.

```python
import os
os.environ["OPENAI_API_KEY"] = "unused"
os.environ["OPENAI_BASE_URL"] = "https://internal-llm.company.com/v1"
resolver = LLMResolver(provider="openai", model="codellama-34b")
```

### "Migration is taking longer than planned."

Reasons why migration stalls:

1. **Unclear ownership.** Nominate a single person responsible for the migration's success.
2. **Too many simultaneous changes.** Don't upgrade scanner versions during migration.
3. **Resistance from specific teams.** Address the root cause — often past bad experiences with loud/noisy tooling.

A successful migration is paced at the speed of human adoption, not pipeline configuration.

## Post-migration: what to do after cutover

Once ASCEND is authoritative:

1. **Document what you built.** Future maintainers will thank you.
2. **Train secondary on-call.** Don't concentrate knowledge.
3. **Decommission parallel systems.** Don't let duplicate pipelines run forever.
4. **Set quarterly review cadence.** Revisit thresholds, add new rulesets, retire stale suppressions.
5. **Feed metrics to leadership.** Demonstrate ROI while the memory is fresh.
