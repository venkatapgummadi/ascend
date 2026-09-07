#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 1 Bandit
set -euo pipefail
python3 -m pip install --quiet bandit
# Bandit exits 1 when it finds issues; the quality gate decides pass/fail.
bandit -r . -f json -o bandit-report.json || true
echo "Wrote bandit-report.json"
