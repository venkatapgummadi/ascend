#!/usr/bin/env bash
# ASCEND Bamboo agent - Layer 2 Trivy
set -euo pipefail
IMAGE="${ASCEND_IMAGE:-ascend-app:local}"
if [[ ! -f Dockerfile ]]; then
  echo "No Dockerfile in $(pwd); scanning the filesystem instead."
  trivy fs --severity CRITICAL,HIGH --ignore-unfixed \
    --exit-code 0 --format sarif --output trivy.sarif .
else
  docker build -t "$IMAGE" .
  trivy image --severity CRITICAL,HIGH --ignore-unfixed \
    --exit-code 0 --format sarif --output trivy.sarif "$IMAGE"
fi
echo "Wrote trivy.sarif"
