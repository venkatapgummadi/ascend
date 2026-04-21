# ASCEND

**A**utomated **S**canning, **C**ompliance **EN**forcement, and **D**eployment

A comprehensive four-layer DevSecOps framework that integrates automated security scanning directly into CI/CD pipelines with build-gating mechanisms, multi-track deployment orchestration, and AI-powered post-deployment code synchronization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Paper](https://img.shields.io/badge/paper-PDF-red.svg)](./docs/paper/ASCEND.pdf)

---

## Overview

Modern CI/CD pipelines prioritize velocity. ASCEND's thesis is that velocity and security are not in tension — the tension comes from treating security scanning as a passive reporting step rather than as an active build gate. ASCEND integrates security scanning, build gating, multi-track deployment orchestration, and AI-powered synchronization into a single, platform-agnostic framework.

### Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Source Analysis                                        │
│  SAST (CodeQL, Semgrep, SonarQube) + SCA (Snyk) + Secrets       │
│                           [ Quality Gate 1 ]                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Build & Integration                                    │
│  Container Scan (Trivy) + IaC Scan (Checkov) + License Check    │
│                           [ Quality Gate 2 ]                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Deployment Orchestration                               │
│  Blue-Green / Canary / Rolling + DAST (OWASP ZAP)               │
│                           [ Quality Gate 3 ]                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: AI-Powered Synchronization                             │
│  AST Drift Detection + ML Conflict Classification + LLM Resolve  │
│                      [ Back-propagation ]                        │
└─────────────────────────────────────────────────────────────────┘
```

### Key Contributions

1. **Four-layer DevSecOps architecture** with formal quality gate definitions.
2. **Platform reference configurations** for GitHub Actions, GitLab CI/CD, Jenkins, and Azure DevOps.
3. **Multi-track deployment framework** supporting blue-green, canary, and rolling strategies with automated quality gates at each promotion boundary.
4. **AI-powered synchronization system** using AST differencing, ML conflict classification, and LLM-based resolution with property-based verification.
5. **Comprehensive scanning tool integration** covering SonarQube, Semgrep, CodeQL, Snyk, Trivy, OWASP ZAP, Checkov, and TruffleHog.

---

## Quick Start

### 1. Choose your platform

ASCEND provides full reference configurations for four major CI/CD platforms:

| Platform | Location | Best For |
|----------|----------|----------|
| GitHub Actions | [`platforms/github-actions/`](./platforms/github-actions/) | Teams on GitHub with GHAS |
| GitLab CI/CD | [`platforms/gitlab-ci/`](./platforms/gitlab-ci/) | Fastest integration via native templates |
| Jenkins | [`platforms/jenkins/`](./platforms/jenkins/) | Existing Jenkins infrastructure |
| Azure DevOps | [`platforms/azure-devops/`](./platforms/azure-devops/) | Microsoft enterprise ecosystems |

### 2. Copy the pipeline configuration

Example for GitHub Actions:

```bash
cp platforms/github-actions/.github/workflows/ascend-full.yml \
   /path/to/your/repo/.github/workflows/
```

### 3. Configure scanning tools

Each scanning tool requires minimal configuration (API tokens, organization IDs). See [`quality-gates/README.md`](./quality-gates/README.md) for setup instructions for each tool.

### 4. Enable the AI synchronization layer (optional)

```bash
cd ai-sync
pip install -e .
ascend-sync --help
```

See [`ai-sync/README.md`](./ai-sync/README.md) for configuration.

### 5. Run your first pipeline

Push a commit to your feature branch. ASCEND will execute Layer 1 scanning immediately. Passing builds progress through Layer 2, Layer 3, and Layer 4 according to your promotion rules.

---

## Adoption Roadmap

ASCEND is designed for incremental adoption. Most organizations realize the majority of security value from Layer 1 alone.

| Phase | Effort | Layers | Outcome |
|-------|--------|--------|---------|
| Phase 1 | 1–2 weeks | Layer 1 | ~80% of vulnerability reduction |
| Phase 2 | 4–6 weeks | Layers 1–2 | Container & IaC coverage |
| Phase 3 | 4–6 weeks | Layers 1–3 | Multi-track deployment gates |
| Phase 4 | 8–12 weeks | Layers 1–4 | Full AI synchronization |

Start with Phase 1, measure impact, and progress only when the current phase is operating smoothly.

---

## Repository Structure

```
ASCEND/
├── docs/                    # Architecture docs and research paper
│   ├── architecture.md
│   ├── quality-gates.md
│   ├── adoption-guide.md
│   └── paper/               # Published research paper (PDF + LaTeX)
├── platforms/               # Platform-specific CI/CD configurations
│   ├── github-actions/
│   ├── gitlab-ci/
│   ├── jenkins/
│   └── azure-devops/
├── ai-sync/                 # AI synchronization Python module
│   ├── ascend_sync/         # Source package
│   ├── tests/
│   └── examples/
├── quality-gates/           # Scanning tool configurations
│   ├── sonarqube/
│   ├── semgrep/
│   ├── checkov/
│   └── zap/
├── examples/                # Sample applications with ASCEND integrated
└── scripts/                 # Setup and validation utilities
```

---

## Documentation

### Getting started

- [Architecture Overview](./docs/architecture.md) — four-layer design with diagrams
- [Adoption Guide](./docs/adoption-guide.md) — phased rollout plan
- [Migration Guide](./docs/migration-guide.md) — moving from existing CI/CD setups
- [FAQ](./FAQ.md) — common questions answered
- [Troubleshooting](./TROUBLESHOOTING.md) — diagnosing common pipeline issues

### Reference

- [Quality Gate Specifications](./docs/quality-gates.md) — QG1/QG2/QG3 tuning
- [AI Synchronization Module](./ai-sync/README.md) — Layer 4 deep-dive
- [API Reference](./docs/api-reference.md) — Python API for `ascend_sync`
- [Glossary](./docs/glossary.md) — terminology
- [Research Paper (PDF)](./docs/paper/ASCEND.pdf) — full technical treatment

### Enterprise and compliance

- [Compliance Framework Mapping](./docs/compliance-mapping.md) — PCI DSS, SOC 2, HIPAA, NIST, ISO 27001, FedRAMP
- [Metrics and KPIs](./docs/metrics-and-kpis.md) — what to measure and how
- [Threat Model](./docs/threat-model.md) — threats to the framework itself

### Project information

- [Changelog](./CHANGELOG.md)
- [Roadmap](./ROADMAP.md)
- [Contributing](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)

## Examples

Working sample applications with ASCEND pre-integrated — see [`examples/`](./examples/) for details.

- [`sample-python-app`](./examples/sample-python-app/) — Flask API on GitHub Actions
- [`sample-node-app`](./examples/sample-node-app/) — Express API on GitLab CI/CD
- [`terraform-baseline`](./examples/terraform-baseline/) — Checkov-compliant AWS IaC
- [`conflict-fixtures`](./examples/conflict-fixtures/) — JSON fixtures for testing AI sync

---

## Research Paper

ASCEND is described in detail in the accompanying research paper. The paper presents the formal quality gate definitions, the AI synchronization algorithms, and an empirical evaluation of framework effectiveness.

**Citation:**

```bibtex
@misc{gummadi2025ascend,
  title  = {ASCEND: A Comprehensive DevSecOps Framework for Automated Code Scanning,
            Multi-Track Deployment, and AI-Powered Post-Deployment Synchronization
            in Enterprise CI/CD},
  author = {Gummadi, Venkata Pavan Kumar},
  year   = {2026},
  note   = {Preprint}
}
```

See [`CITATION.cff`](./CITATION.cff) for additional citation formats.

---

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the contribution workflow and [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) for community standards.

Areas where contributions are especially valuable:

- Additional platform configurations (CircleCI, TeamCity, Bamboo, Buildkite)
- Additional scanning tool integrations
- Conflict resolution model training data (anonymized merge conflict histories)
- Language-specific SAST rule sets
- Sample application integrations

---

## License

ASCEND is released under the MIT License. See [`LICENSE`](./LICENSE) for the full license text.

---

## Author

**Venkata Pavan Kumar Gummadi**
IEEE Senior Member | Professional Software Engineer
Email: venkata.p.gummadi@ieee.org

---

## Acknowledgments

The ASCEND framework draws on the public DevSecOps knowledge base assembled by the broader security engineering community, including the NIST Cybersecurity Framework, OWASP Top 10, CIS Benchmarks, and the authors of the scanning tools integrated into this framework.
