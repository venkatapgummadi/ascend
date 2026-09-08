#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 1 Semgrep
set -euo pipefail
semgrep --config=p/ci --config=p/owasp-top-ten --config=p/security-audit \
  --json -o semgrep-report.json .
echo "Wrote semgrep-report.json"
