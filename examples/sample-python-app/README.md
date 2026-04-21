# Sample Python Application — ASCEND Integrated

A minimal Flask API demonstrating the full ASCEND four-layer pipeline on GitHub Actions. Use this as a reference for Python service integration.

## What this example demonstrates

- **Layer 1:** SAST findings caught by Bandit / Semgrep / SonarQube (intentional demonstrative issues plus a hardened version).
- **Layer 2:** Container image scanning with Trivy, IaC scanning with Checkov.
- **Layer 3:** DAST with OWASP ZAP against a deployed staging instance.
- **Layer 4:** AI sync integration webhook.

## Structure

```
sample-python-app/
├── .github/
│   └── workflows/
│       └── ascend.yml          # Full pipeline
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask app
│   ├── auth.py                 # Token validation
│   └── database.py             # DB access (parameterized queries)
├── tests/
│   ├── test_main.py
│   └── test_auth.py
├── terraform/
│   ├── main.tf                 # AWS infrastructure
│   └── variables.tf
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── .checkov.baseline
├── .trivyignore
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Docker
- Terraform (if deploying infrastructure)

### Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the app
FLASK_APP=app.main flask run

# Run tests
pytest tests/
```

### Build container locally

```bash
docker build -t sample-python-app:local .
docker run -p 5000:5000 sample-python-app:local
```

### Run Layer 1 scans locally

```bash
# SAST
bandit -r app/
semgrep --config=p/owasp-top-ten app/

# SCA
pip-audit

# Secret scan
trufflehog filesystem . --only-verified
```

## Enabling the ASCEND pipeline

1. Push this directory to a GitHub repository.
2. Configure secrets at `Settings → Secrets and variables → Actions`:
   - `SONAR_TOKEN`
   - `SONAR_HOST_URL`
   - `SNYK_TOKEN`
3. Enable GitHub Advanced Security (available on all public repos).
4. Push a commit to the default branch.

The pipeline will run. Layer 1 findings surface as PR comments via GitHub Code Scanning.

## What findings to expect

The sample app is *deliberately* clean of high-severity issues. To see the pipeline react to findings, check out the `demo-vulns` branch which intentionally introduces:

- A hardcoded secret (caught by TruffleHog).
- A SQL injection via string concatenation (caught by Semgrep + Bandit).
- A dependency with a known CVE (caught by Snyk).
- A Dockerfile running as root (caught by Trivy + Checkov).
- An unauthenticated admin endpoint (caught by DAST in Layer 3).

Merge attempts on `demo-vulns` will be blocked at each corresponding gate.

## Further reading

- [Architecture overview](../../docs/architecture.md)
- [Quality gate specifications](../../docs/quality-gates.md)
- [Adoption guide](../../docs/adoption-guide.md)
