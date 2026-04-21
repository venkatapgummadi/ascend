# Sample Node.js Application — ASCEND Integrated

A minimal Express REST API demonstrating the full ASCEND four-layer pipeline on GitLab CI/CD. Use this as a reference for Node.js service integration with GitLab's native security scanning.

## What this example demonstrates

- **Layer 1:** SAST via GitLab native SAST template + Semgrep, SCA via GitLab Dependency Scanning, secret detection.
- **Layer 2:** Container scanning via GitLab Container Scanning + Trivy, IaC scanning via Checkov.
- **Layer 3:** DAST via GitLab native DAST template against a deployed staging environment.
- Integration with GitLab's merge request security dashboard.

## Structure

```
sample-node-app/
├── .gitlab-ci.yml               # Full ASCEND pipeline
├── src/
│   ├── index.js                 # Express app entrypoint
│   ├── auth.js                  # JWT authentication middleware
│   ├── routes/
│   │   ├── users.js
│   │   └── health.js
│   └── db.js                    # SQLite with parameterized queries
├── test/
│   ├── auth.test.js
│   └── users.test.js
├── Dockerfile
├── package.json
├── .eslintrc.json
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Node.js 20+
- npm 10+
- Docker

### Local development

```bash
npm ci
npm test

# Run locally
npm run dev

# The server listens on http://localhost:3000
```

### Build container

```bash
docker build -t sample-node-app:local .
docker run -p 3000:3000 sample-node-app:local
```

## Enabling the ASCEND pipeline

1. Push this directory to a GitLab repository.
2. In your GitLab project, go to `Settings → CI/CD → Variables` and add:
   - `JWT_SIGNING_SECRET` (masked, protected)
   - Any cloud credentials needed for deployment.
3. Enable the GitLab native security scanners at `Secure → Security configuration`:
   - SAST, Secret Detection, Dependency Scanning, Container Scanning, DAST.
4. Configure merge request approval rules to require security review when vulnerabilities are detected.

## What findings to expect

This sample is clean of intentional vulnerabilities. Typical findings on a passing run:

- Optional ESLint rule violations (cosmetic).
- Zero critical / high findings across SAST, SCA, container, DAST.

The `demo-vulns` branch (to be added) would contain intentional:

- Hardcoded secret.
- NoSQL injection via unsafe query composition.
- Dependency with known CVE.
- Container running as root.
- Missing rate limiting on the auth endpoint.

## GitLab-specific tips

- The merge request security dashboard automatically groups findings by severity.
- Use `allow_failure: true` on SAST jobs during initial rollout to avoid blocking merges.
- Protected branches should require all security jobs to pass.

## Further reading

- [Architecture overview](../../docs/architecture.md)
- [Quality gate specifications](../../docs/quality-gates.md)
- [Adoption guide](../../docs/adoption-guide.md)
