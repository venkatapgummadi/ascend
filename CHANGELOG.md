# Changelog

All notable changes to ASCEND are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Additional platform configurations: CircleCI, TeamCity, Buildkite
- Polyglot AI conflict resolution beyond Python
- Federated learning for the conflict classifier
- Integration with SBOM standards (CycloneDX, SPDX)
- Reinforcement learning for dynamic quality gate thresholds

## [0.1.0] — 2026-04-21

### Added

#### Framework architecture

- Four-layer DevSecOps architecture: Source Analysis (L1), Build & Integration (L2), Deployment Orchestration (L3), AI Synchronization (L4).
- Formal Quality Gate definitions with configurable composite scoring.
- Multi-track deployment framework supporting blue-green, canary, rolling, and hotfix paths.

#### Platform reference configurations

- GitHub Actions: complete four-layer pipeline with matrix SAST, parallel scanning, and native GHAS SARIF integration.
- GitLab CI/CD: full pipeline using native security templates and merge request security dashboard.
- Jenkins: declarative Jenkinsfile with parallel stage execution and Blue Ocean compatibility.
- Azure DevOps: YAML pipeline with AzureWebApp slot swap deployment and Environments approval gates.

#### AI synchronization module (`ai-sync`)

- `DriftDetector`: AST-based semantic drift detection with configuration fingerprinting and embedding distance components.
- `ConflictClassifier`: feature-based and sklearn-backed classification into `{syntactic, semantic, structural, configuration}` types.
- `LLMResolver`: pluggable LLM backend with OpenAI, Anthropic, and local stub providers.
- `Verifier`: property-based verification with parse checking, signature preservation, and security pattern preservation.
- `PROrchestrator`: automated GitHub PR creation with labels, reviewers, and structured PR bodies.
- CLI entrypoint: `ascend-sync {detect-drift|classify|resolve|version}`.

#### Quality gate configurations

- SonarQube quality gate definition with 8 conditions covering security, reliability, maintainability, coverage, and duplication.
- Semgrep ruleset integrating community rules with custom ASCEND rules for hardcoded secrets, SQL injection, eval usage, weak crypto, TLS verification, and debug-in-prod.
- Checkov configuration covering Terraform, CloudFormation, Kubernetes, Dockerfile, Helm, and GitHub Actions.
- OWASP ZAP rules file tuned for high-volume CI execution.
- TruffleHog config with `--only-verified` to minimize false positives.
- Snyk `.snyk` example with documented ignore pattern.

#### Documentation

- `docs/architecture.md`: full architecture deep-dive with ASCII diagrams.
- `docs/quality-gates.md`: QG1/QG2/QG3 specifications and tuning guide.
- `docs/adoption-guide.md`: phased rollout plan (Phase 1 through Phase 4).
- Research paper bundle: PDF + LaTeX source + IEEEtran class.

#### Tooling

- `scripts/setup.sh`: one-command platform-specific adoption helper.
- `scripts/validate-config.sh`: pre-commit sanity check for all configuration files.
- `.github/workflows/test.yml`: self-CI for the ASCEND repo (pytest + ruff + validator).
- Issue templates: bug report and feature request.

### Notes

- This is the initial public release. API surface is marked alpha; breaking changes possible until 1.0.
- The AI synchronization module ships with a heuristic classifier by default. Production deployments should retrain on organization-specific merge conflict history.
- Sample applications (Python/Flask, Node.js/Express, Terraform) are included as adoption references.
