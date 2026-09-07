#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 1 Gitleaks
set -euo pipefail
gitleaks detect --source . --report-format json --report-path gitleaks-report.json --no-git || true
echo "Wrote gitleaks-report.json"
