# Roadmap

This document outlines the planned direction for ASCEND. Timelines are aspirational; the project is volunteer-maintained.

## Near-term (next 3–6 months)

### Additional platform coverage

- **CircleCI**: YAML config parallel to GitHub Actions.
- **TeamCity**: Kotlin DSL build configuration.
- **Buildkite**: `.buildkite/pipeline.yml` with parallel steps.
- **AWS CodePipeline + CodeBuild**: CloudFormation template for full pipeline.
- **Google Cloud Build**: `cloudbuild.yaml` reference.

### Polyglot AI sync

Current AST drift detection is Python-specific. Add:

- JavaScript / TypeScript AST via `@typescript-eslint/parser` or `babel-parser`.
- Java AST via JavaParser (jar invoked as subprocess).
- Go AST via `go/ast` (small helper binary).
- Ruby AST via `parser` gem.

Each language needs an adapter implementing the `_semantic_diff` contract.

### More language-specific Semgrep rules

- Java Spring (authentication misconfigurations, unsafe deserialization).
- Go (context handling, goroutine leaks that lead to DoS).
- Ruby on Rails (CSRF bypass, mass assignment).
- .NET (deserialization, authorization bypass patterns).

### AI sync model improvements

- **Training pipeline** for the conflict classifier with cross-validation and hyperparameter tuning.
- **Curated training dataset** with 5,000+ anonymized resolved conflicts.
- **Transformer-based classifier** (fine-tuned CodeBERT / GraphCodeBERT).

### Documentation expansion

- **Compliance deep-dives** per framework: PCI DSS 4.0 mapping, SOC 2 Type II evidence guide, HIPAA § 164.312 controls, NIST 800-53 crosswalk, ISO 27001 Annex A controls.
- **Workshop materials** for internal team training.
- **Video walkthroughs** for each platform.

## Medium-term (6–12 months)

### Supply chain security integration

- **SBOM generation** at each build (CycloneDX and SPDX formats).
- **SBOM signing** via Sigstore / Cosign.
- **Provenance attestation** following SLSA levels 2 and 3.
- **Dependency risk scoring** combining Snyk, EPSS, and maintainer activity signals.

### Federated learning for AI sync

Enable organizations to improve the shared conflict resolution model without exposing proprietary code:

- Local model fine-tuning on each organization's data.
- Encrypted gradient aggregation.
- Model updates distributed via signed releases.

### Runtime feedback loop

Close the loop between production runtime anomalies and CI/CD policy:

- **RASP integration**: receive runtime exploit attempts and auto-generate Semgrep rules preventing the pattern in future builds.
- **Production incident → pipeline policy**: when an incident roots to a code defect, generate the equivalent SAST/DAST rule automatically.

### Multi-repo coordination

For organizations with hundreds of services, centralize:

- Quality gate threshold management.
- Tool version pinning.
- Aggregated vulnerability dashboards across all ASCEND-equipped repos.

## Long-term (12+ months)

### Reinforcement learning for quality gates

Adaptive thresholds that learn organization-specific risk signals:

- Loosen gates on low-traffic services.
- Tighten gates for services handling PII / PCI data.
- Incorporate blast radius estimation into gate decisions.

### Self-healing pipelines

Automated pipeline recovery:

- Detect flaky scans and adjust retry strategies.
- Auto-generate suppressions for confirmed false positives with expiration.
- Propose gate threshold adjustments based on observed noise.

### Research directions

- **Formal verification integration**: invoke bounded model checking for security-critical code paths in Layer 1.
- **Homomorphic ML inference**: run the conflict classifier on encrypted code to enable SaaS deployment without source code exposure.
- **Differential privacy**: anonymize organization-specific signals in the shared classifier training loop.

## Intentionally not on the roadmap

- **Commercial SaaS**: ASCEND will remain open source. Organizations can deploy self-hosted.
- **Replacement of existing scanning tools**: ASCEND orchestrates third-party tools; it does not aim to replace SonarQube, Snyk, etc.
- **Full autonomy**: AI sync proposes, humans dispose. No plans for human-out-of-the-loop deployment.

## How you can help

Every item on this roadmap can be accelerated by community contribution. If any of these interest you, open an issue labeled `roadmap` to express intent, then submit a design proposal before starting significant implementation work.

Priority signals come from:

1. Issues with lots of :+1: reactions.
2. Dependencies of other planned features.
3. Fit with the stated project principles (honest, incremental, open).

The maintainer has veto authority on architectural direction but aims to operate transparently. Major decisions are recorded in GitHub Discussions.
