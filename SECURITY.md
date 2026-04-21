# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in ASCEND's own code (not in one of the third-party tools that ASCEND integrates with), please report it privately.

**Do not open a public GitHub issue for security reports.**

Instead:

1. Email: venkata.p.gummadi@ieee.org
2. Subject: `[ASCEND SECURITY] <short description>`
3. Include: a description of the issue, steps to reproduce, affected versions, and any proposed mitigation.

You will receive an acknowledgment within 72 hours. Triage and fix timelines depend on severity:

| Severity | Acknowledgment | Fix target |
|----------|----------------|------------|
| Critical | 24 hours       | 7 days     |
| High     | 72 hours       | 30 days    |
| Medium   | 1 week         | 90 days    |
| Low      | 2 weeks        | Best effort |

## Supported versions

Only the latest release of ASCEND is supported for security updates. Older versions should be upgraded.

## Security scope

ASCEND orchestrates third-party scanning tools (SonarQube, Snyk, Trivy, OWASP ZAP, Checkov, TruffleHog, etc.). Vulnerabilities in those tools should be reported to the respective upstream maintainers. ASCEND is in scope for:

- The AI synchronization module code in `ai-sync/`.
- The platform pipeline configurations in `platforms/` (misconfigurations, privilege escalation, secret leakage paths).
- The quality gate logic in `quality-gates/`.
