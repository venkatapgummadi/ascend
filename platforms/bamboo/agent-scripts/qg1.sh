#!/usr/bin/env bash
# ASCEND Bamboo agent - Quality Gate 1
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GATE="${ASCEND_GATE_SCRIPT:-$SCRIPT_DIR/scripts/severity_gate.py}"
python3 "$GATE" --layer 1 \
  --mode "${ASCEND_MODE:-enforce}" \
  --semgrep semgrep-report.json \
  --bandit bandit-report.json \
  --gitleaks gitleaks-report.json \
  --summary-json qg1-summary.json
