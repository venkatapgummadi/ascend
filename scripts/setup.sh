#!/usr/bin/env bash
#
# ASCEND — setup.sh
# One-command setup helper for a new ASCEND adoption.
#
# Usage: ./scripts/setup.sh <platform>
# Platforms: github-actions | gitlab-ci | jenkins | azure-devops

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORM="${1:-}"

usage() {
    echo "Usage: $0 <platform>"
    echo
    echo "Platforms:"
    echo "  github-actions   GitHub Actions workflow"
    echo "  gitlab-ci        GitLab CI/CD pipeline"
    echo "  jenkins          Jenkins declarative pipeline"
    echo "  azure-devops     Azure DevOps YAML pipeline"
    exit 1
}

if [[ -z "$PLATFORM" ]]; then
    usage
fi

case "$PLATFORM" in
    github-actions)
        src="$REPO_ROOT/platforms/github-actions/.github/workflows/ascend-full.yml"
        dst=".github/workflows/ascend-full.yml"
        ;;
    gitlab-ci)
        src="$REPO_ROOT/platforms/gitlab-ci/.gitlab-ci.yml"
        dst=".gitlab-ci.yml"
        ;;
    jenkins)
        src="$REPO_ROOT/platforms/jenkins/Jenkinsfile"
        dst="Jenkinsfile"
        ;;
    azure-devops)
        src="$REPO_ROOT/platforms/azure-devops/azure-pipelines.yml"
        dst="azure-pipelines.yml"
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        usage
        ;;
esac

if [[ ! -f "$src" ]]; then
    echo "Source file not found: $src"
    exit 1
fi

if [[ -f "$dst" ]]; then
    echo "Destination already exists: $dst"
    echo "Refusing to overwrite. Merge manually."
    exit 1
fi

mkdir -p "$(dirname "$dst")"
cp "$src" "$dst"

echo "Copied $src -> $dst"
echo
echo "Next steps:"
echo "  1. Configure required secrets/credentials (see platforms/$PLATFORM/README.md)."
echo "  2. Run the pipeline in warning-only mode for 2 weeks."
echo "  3. Calibrate thresholds, then switch to enforce mode."
echo
echo "Optional — enable Layer 4 (AI synchronization):"
echo "  cd ai-sync && pip install -e ."
