# Changelog

All notable changes to ASCEND are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- IEEE Access reviewer-facing infrastructure under `docs/paper/`:
  - `references.bib` — complete BibTeX for all 20 numbered citations plus 14 resolutions for the unresolved `[?]` placeholders in the initial submission.
  - `REVIEWER_CHECKLIST.md` — `[?]`-to-key mapping, code-vs-paper alignment table, and pre-resubmission verification commands.
  - `EVALUATION.md` — extended methodology document for §VIII, including anonymisation pipeline and threats-to-validity expansion.
- Reproducibility harness under `evaluation/`:
  - `statistics.py` — deterministic Welch t-test + Cohen's d analyser that regenerates Table IX given an aggregate metrics CSV.
  - `aggregate-metrics.csv` — synthetic schema-demonstration CSV (clearly labelled).
  - `expected-synthetic-output.json` — CI assertion target for the analyser against the synthetic input.
  - `paper-table9.json` — verbatim record of the paper's reported Table IX values.
- Top-level `Makefile` with `install`, `test`, `lint`, `eval`, `stats`, `repro`, `clean` targets.
- New tests covering `LLMResolver` (local stub, unknown provider, confidence heuristic, mocked OpenAI failure path), additional `Verifier` cases (determinism regression, empty resolution, JSON round-trip), `DriftDetector` JSON serialisation, explanation text, and threshold boundary, full `PROrchestrator` coverage (PR-body construction, headers, mocked HTTP), and CLI smoke tests via `click.testing.CliRunner`. Suite size grew from 12 to 40, line coverage 83%.
- Coverage floor of 70% enforced via `--cov-fail-under=70` in `ai-sync/pyproject.toml`.
- Bandit self-scan job in `.github/workflows/test.yml`; required to be clean.
- Reproducibility-harness CI job runs `examples/conflict-fixtures/run_fixtures.py --check` and bit-exact-diffs `evaluation/statistics.py` output against `expected-synthetic-output.json`.
- IEEE Access §VII cross-reference docstrings on `DriftDetector`, `ConflictClassifier`, `Verifier`, and `LLMResolver`, naming the equation each class implements.
- Real-world case study `docs/case-study-ai-cve-dependency.md` covering an AI-suggested dependency downgrade reintroducing CVE-2024-1135 (gunicorn) and CVE-2022-23529 (jsonwebtoken).

### Changed

- `CITATION.cff` now includes the paper abstract, an explicit `identifiers` block with a Zenodo DOI placeholder, and a `url` field. Reviewers can ingest it without modification.
- README: added a "Reproducing the paper's results" section, fixed broken `docs/paper/ASCEND.pdf` links to point to `docs/paper/README.md`, and corrected the repository-structure tree to match the actual flat `quality-gates/` layout.

### Fixed

- `pr_orchestrator.py`: `default_labels` and `default_reviewers` constructor arguments now respect explicit empty lists. Previous code used `or` which silently fell back to defaults, making it impossible to opt out of labels.
- `conflict_classifier.py`: model loading is now wrapped in `_safe_pickle_load`, which requires either `ASCEND_TRUST_MODEL_PATH=1` or a verified `.sha256` sidecar before deserialising. Closes the bandit B301 self-scan finding without forcing an opinionated model serialisation format on consumers.
- `docs/paper/README.md`: removed claims of files that don't exist in this repo (`ASCEND.pdf`, `main.tex`, `IEEEtran.cls`, `photo_placeholder.png`); explained where they live and why.
- `ai-sync/ascend_sync/conflict_classifier.py` module docstring + `ai-sync/README.md` Model Training section: removed references to a non-existent `train.py` / `python -m ascend_sync.train` invocation; documented the actual override path (`ConflictClassifier(model_path=...)`).
- `conflict_classifier.py`: `Classification.features` is now correctly typed `dict | None` (was `dict` but defaulted to `None`).
- `conflict_classifier.py`: removed a redundant duplicate scan over `_CONFIG_FILE_EXTENSIONS` that incorrectly matched config-extension substrings anywhere in the path.
- `llm_resolver.py`: `Resolution.preserves_invariants` is now correctly typed `list[str] | None`.
- `verifier.py`: property-test sample selection is now sorted, eliminating non-determinism caused by relying on Python set iteration order.
- `verifier.py`: removed redundant `or not required` clause from `_signatures_preserved` (an empty set is trivially a subset).

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
