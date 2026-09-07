#!/usr/bin/env bash
# ASCEND Bamboo agent - Quality Gate 2
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GATE="${ASCEND_GATE_SCRIPT:-$SCRIPT_DIR/scripts/severity_gate.py}"
python3 "$GATE" --layer 2 \
  --mode "${ASCEND_MODE:-enforce}" \
  --sarif trivy.sarif checkov.sarif \
  --summary-json qg2-summary.json
