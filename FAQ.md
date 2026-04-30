# Frequently Asked Questions

## About the project

### What is ASCEND?

ASCEND is a comprehensive four-layer DevSecOps framework that integrates automated security scanning into CI/CD pipelines with build-gating, multi-track deployment orchestration, and AI-powered post-deployment code synchronization. It is described in detail in the accompanying [research paper](./docs/paper/README.md).

### Who is ASCEND for?

Engineering organizations that:

- Deploy to production at least weekly.
- Operate multi-track branches (development, staging, production, hotfix).
- Have regulatory or audit requirements (SOC 2, PCI DSS, HIPAA, NIST).
- Currently experience security review as a bottleneck rather than an enabler.

If you deploy once a quarter and have no security review process, ASCEND is overkill. Start simpler.

### What does ASCEND *not* do?

- **It doesn't replace your security team.** ASCEND automates enforcement of policies; humans still define those policies, review AI-proposed resolutions, and investigate findings.
- **It doesn't remove the need for runtime security.** ASCEND operates in the build/deploy pipeline. Runtime Application Self-Protection (RASP) and continuous production monitoring are complementary, not replacements.
- **It doesn't magically resolve every merge conflict.** Layer 4 auto-resolves high-confidence conflicts (typically ~70%). Structural and complex semantic conflicts still require human judgment.

### Is ASCEND free?

The framework code and reference configurations are MIT-licensed and free. The scanning tools ASCEND integrates with have their own licensing — some are free (OWASP ZAP, Checkov, Semgrep Community, Trivy, TruffleHog), others are commercial (SonarQube Enterprise, Snyk Team, FOSSA Enterprise). Plan for ~$50K–$150K/year in commercial tooling costs for a mid-size enterprise deployment.

### Can I use ASCEND in a proprietary project?

Yes. The MIT license permits commercial use without restriction. You don't need to publish your configurations, attribute ASCEND in user-facing materials, or share changes. We appreciate attribution in engineering blog posts or internal documentation, but it's not required.

## Technical questions

### Which CI/CD platform should I use?

| Platform | Best when |
|----------|-----------|
| GitHub Actions | Already using GitHub, want tight PR integration via GHAS |
| GitLab CI/CD | Prioritizing fastest adoption via native security templates |
| Jenkins | Existing Jenkins infrastructure requiring gradual migration |
| Azure DevOps | Microsoft ecosystem, enterprise RBAC requirements |

All four support the full ASCEND feature set. Your existing investment and team familiarity usually dominate the choice.

### Will ASCEND slow down my builds?

Yes, measurably — but less than you'd expect. Layer 1 adds ~7 minutes median overhead per build. Layer 2 adds another ~6 minutes. Layer 3 DAST adds ~8 minutes but only runs at staging promotion. The parallel execution design keeps each layer's overhead bounded.

If your baseline build is 8 minutes, expect ~15 minutes with Layer 1, ~21 minutes with Layers 1–2, ~30 minutes with full pipeline. Most teams find this acceptable; some route DAST to nightly runs to keep per-commit builds under 20 minutes.

### How do I tune for lots of false positives?

Two main levers:

1. **Multi-tool cross-validation.** ASCEND flags a finding only when ≥2 tools agree at the same code location. Enabling this alone typically drops false positive rate by 30–40%.
2. **Baselining.** Use `.checkov.baseline`, SonarQube's "new code" mode, and Snyk's ignore lists to grandfather existing findings and enforce only on new code.

Avoid the temptation to globally disable noisy rules — that creates blind spots. Suppress specific rule instances with documented expiration dates.

### Does ASCEND support languages beyond Python/Java/JavaScript?

The scanning tools cover: Python, Java, JavaScript/TypeScript, Go, Ruby, C#, C/C++, Kotlin, Swift, PHP, Rust, and several others. The AI synchronization module currently ships with Python-specific AST diffing; PRs welcome to add other languages.

### How do I handle secrets in the pipeline?

- CI platform secret storage (GitHub Actions secrets, GitLab CI/CD variables, Jenkins credentials, Azure DevOps library variables).
- Never commit secrets. TruffleHog's full-history scan will catch historical leaks.
- Use short-lived OIDC tokens for cloud deployments (GitHub Actions → AWS IAM, Azure federated credentials) rather than long-lived service account keys.

### Can I run Layer 4 (AI sync) without an LLM API?

Yes — set `provider: local` in the AI sync config to use the offline stub resolver. It produces the union of both sides as a conservative placeholder. This is useful for dry-run evaluation and for organizations that can't route source code through external LLM providers. For production use you'll want a real provider.

### How does ASCEND handle mono-repos?

The platform configurations target single repositories by default. For mono-repos, adapt:

- **Matrix builds** (GitHub Actions matrix, GitLab parallel:matrix) scan each service in parallel.
- **Path filters** limit scanning to directories that changed (e.g., `paths: ['services/auth/**']`).
- **Dedicated quality gates per service** let you tune thresholds per module.

The ASCEND research paper briefly discusses multi-module evaluation; see `docs/architecture.md` for architectural guidance.

## Adoption questions

### How long does adoption take?

- **Phase 1 (Layer 1):** 1–2 weeks for a cooperative team, 4–6 weeks for larger or skeptical teams.
- **Phase 2 (Layer 2):** additional 4–6 weeks.
- **Phase 3 (Layer 3):** additional 4–6 weeks.
- **Phase 4 (Layer 4):** additional 8–12 weeks including ML model training.

Most value comes from Phase 1. Don't try to do all four phases at once.

### My team hates mandatory security gates. How do I sell ASCEND?

Two facts to lead with:

1. **Deployment frequency increases**, not decreases, after ASCEND adoption. Teams deploy more often because automated scanning removes the manual security review bottleneck. The ASCEND paper reports a 171.9% increase in deployment frequency in the evaluated cohort.
2. **Failure rate drops** from 14.3% to 4.1% and rollback rate from 8.7% to 2.3%. Automation catches defects that otherwise cause production incidents.

Start in warning-only mode. Show the team findings that would have been caught before they hit production. Convert to blocking only after the team has seen the value.

### We have thousands of existing findings. How do we start without drowning?

Use the baselining pattern. Every scanning tool supports grandfathering existing findings:

- **Checkov**: `checkov --create-baseline` then `--baseline .checkov.baseline`.
- **SonarQube**: configure the Quality Gate to apply only to "New Code" (since a specific date or version).
- **Snyk**: bulk-ignore existing issues with a 90-day expiration; chip away at them in dedicated sprints.

This lets you enforce strict rules on new code without blocking on technical debt you can't immediately address.

### What if we can't use the cloud scanning tools ASCEND recommends?

All the recommended tools have self-hosted options:

- SonarQube: self-hostable Community or Enterprise edition.
- Snyk: self-hosted Snyk Code.
- Trivy: runs offline with airgapped DB updates.
- OWASP ZAP: fully self-hosted.
- Checkov: local-only by default.
- TruffleHog: self-hosted.
- Semgrep: Community Edition runs offline; Enterprise has self-hosted.

For highly regulated environments (government, defense, healthcare), all major tools support airgapped deployment with offline vulnerability database updates.

### Does ASCEND conflict with existing security tools?

Usually no — ASCEND *integrates* with your existing tools rather than replacing them. If you already have SonarQube, Snyk, or ZAP, keep them. If your security team prefers Checkmarx over SonarQube, wire Checkmarx into the pipeline via its CLI. The framework is the layered architecture; the specific tools are pluggable.

## AI synchronization questions

### How accurate is the AI conflict resolver?

Varies by conflict type:

- Syntactic: ~97%
- Configuration: ~96%
- Semantic: ~92%
- Structural: ~87%

The system only auto-creates PRs for conflicts with confidence ≥0.85. Lower-confidence conflicts are flagged for human review, so the overall system acceptance rate stays high.

### Can the AI resolver introduce security regressions?

It is explicitly designed to avoid this. The resolver's system prompt requires preservation of security-relevant patterns (authentication, crypto, input validation, rate limiting) from both merge sides. The verifier then enforces this by checking that security patterns present in either side are present in the resolved code. Any resolution that fails this check is rejected before a PR is opened.

That said, humans must review every AI-generated PR. AI sync proposes; humans dispose.

### What models does the AI synchronization module support?

Out of the box: OpenAI (e.g., GPT-4o, GPT-4o-mini) and Anthropic (e.g., Claude Opus, Claude Sonnet). Adding other providers requires a small adapter following the pattern in `llm_resolver.py`.

For privacy-sensitive environments, self-hosted options via Ollama or vLLM work with the OpenAI-compatible API surface — point the OpenAI client at your internal endpoint.

### How much data does the conflict classifier need?

The shipped baseline classifier uses heuristics and needs no training data. The ML classifier needs ~500 historical merge conflicts minimum to produce useful predictions, ~5,000 for production-grade accuracy. Most organizations accumulate this over 6–18 months. If you have less history, stick with the heuristic classifier.

## Contributing and community

### How do I contribute?

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Areas where contributions are especially valuable: additional CI platform configurations, language-specific Semgrep rules, sample applications for new ecosystems.

### How do I report a security issue in ASCEND itself?

See [`SECURITY.md`](./SECURITY.md). Email security reports privately to venkata.p.gummadi@ieee.org — do not open public issues for security reports.

### Can I cite ASCEND in a paper?

Yes — see [`CITATION.cff`](./CITATION.cff) for citation metadata. BibTeX is in the main [`README.md`](./README.md).

### Will you offer commercial support?

Not currently. The project is maintained as open source. Organizations needing commercial support can engage security consultancies that work with the underlying scanning tools (SonarSource, Snyk, Aqua) — those providers offer commercial implementation support for their respective tools in ASCEND pipelines.
