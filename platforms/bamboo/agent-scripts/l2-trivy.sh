#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 2 Trivy (filesystem scan; do not docker build here)
set -euo pipefail
trivy fs --severity CRITICAL,HIGH --ignore-unfixed \
  --exit-code 0 --format sarif --output trivy.sarif .
echo "Wrote trivy.sarif"
