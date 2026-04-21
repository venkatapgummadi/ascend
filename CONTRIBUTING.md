# Contributing to ASCEND

Thanks for your interest in improving ASCEND. This project is open to contributions from practitioners, researchers, and anyone running DevSecOps pipelines in production.

## How to contribute

1. **Fork the repository** and create a feature branch from `main`.
2. **Make your changes** — keep the scope of each PR focused.
3. **Add or update tests** for any code changes in `ai-sync/`.
4. **Run the validation script** before submitting: `./scripts/validate-config.sh`
5. **Open a pull request** against `main` with a clear description of the change and its motivation.

## Types of contributions we welcome

- **New platform configurations.** CircleCI, TeamCity, Bamboo, Buildkite, AWS CodePipeline, GCP Cloud Build.
- **New scanning tool integrations.** Additional SAST / DAST / SCA / IaC tools with community adoption.
- **Language-specific rule sets.** Semgrep rule packs, SonarQube quality profiles, CodeQL queries.
- **Sample applications.** Reference integrations showing ASCEND in use.
- **Documentation improvements.** Clarifications, corrections, translations.
- **AI sync improvements.** Better drift detection, improved conflict classification, additional verification strategies.

## Code style

- **Python code** must pass `ruff` linting and `black` formatting.
- **YAML configurations** must pass `yamllint` with the project's configuration.
- **Shell scripts** must pass `shellcheck`.

## Commit messages

Use conventional commit format where possible:

```
feat(github-actions): add support for matrix builds
fix(ai-sync): handle empty AST in drift detector
docs(readme): clarify Phase 2 adoption timeline
```

## Reporting security issues

If you find a security vulnerability in ASCEND itself — not a CVE in one of the tools ASCEND integrates with — please report it privately to venkata.p.gummadi@ieee.org rather than opening a public issue.

## Code of conduct

All contributors are expected to follow the [Code of Conduct](./CODE_OF_CONDUCT.md).
