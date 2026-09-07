#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 2 Checkov
set -euo pipefail
checkov -d . --framework terraform,cloudformation,kubernetes,dockerfile \
  -o sarif --output-file-path . --soft-fail || true
if [[ -f results_sarif.sarif ]]; then
  mv results_sarif.sarif checkov.sarif
fi
echo "Wrote ${PWD}/checkov.sarif (if Checkov produced SARIF)"
