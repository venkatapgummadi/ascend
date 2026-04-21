#!/usr/bin/env bash
#
# ASCEND — validate-config.sh
# Quick sanity check for the four platform configurations. Run before committing.
#
# Usage: ./scripts/validate-config.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "ASCEND configuration validator"
echo "==============================="

fail=0

check() {
    local name="$1"; local file="$2"
    if [[ -f "$file" ]]; then
        echo "[OK]    $name ($file)"
    else
        echo "[FAIL]  $name — missing file: $file"
        fail=1
    fi
}

validate_yaml() {
    local file="$1"
    if command -v yamllint >/dev/null 2>&1; then
        if yamllint -d relaxed "$file" >/dev/null 2>&1; then
            echo "[OK]    yaml:   $file"
        else
            echo "[WARN]  yaml:   $file — yamllint warnings"
        fi
    fi
}

echo
echo "--- Core metadata ---"
check "README"              README.md
check "LICENSE"             LICENSE
check "CITATION"            CITATION.cff
check "gitignore"           .gitignore
check "contributing"        CONTRIBUTING.md
check "code-of-conduct"     CODE_OF_CONDUCT.md
check "security"            SECURITY.md

echo
echo "--- Platform configurations ---"
check "GitHub Actions"      platforms/github-actions/.github/workflows/ascend-full.yml
check "GitLab CI/CD"        platforms/gitlab-ci/.gitlab-ci.yml
check "Jenkins"             platforms/jenkins/Jenkinsfile
check "Azure DevOps"        platforms/azure-devops/azure-pipelines.yml

echo
echo "--- Quality gate configs ---"
check "SonarQube gate"      quality-gates/sonarqube-quality-gate.json
check "Semgrep rules"       quality-gates/semgrep-rules.yml
check "Checkov config"      quality-gates/checkov-config.yml
check "ZAP rules"           quality-gates/zap-rules.tsv
check "Trufflehog config"   quality-gates/trufflehog-config.yml

echo
echo "--- AI sync module ---"
check "pyproject.toml"      ai-sync/pyproject.toml
check "package init"        ai-sync/ascend_sync/__init__.py
check "drift detector"      ai-sync/ascend_sync/drift_detector.py
check "conflict classifier" ai-sync/ascend_sync/conflict_classifier.py
check "LLM resolver"        ai-sync/ascend_sync/llm_resolver.py
check "verifier"            ai-sync/ascend_sync/verifier.py
check "PR orchestrator"     ai-sync/ascend_sync/pr_orchestrator.py
check "CLI"                 ai-sync/ascend_sync/cli.py

echo
echo "--- YAML lint (if yamllint installed) ---"
find . -type f \( -name "*.yml" -o -name "*.yaml" \) \
    -not -path "./node_modules/*" -not -path "./.git/*" | while read -r f; do
    validate_yaml "$f"
done

echo
echo "--- Python syntax check ---"
if command -v python3 >/dev/null 2>&1; then
    python3 -c "
import ast, pathlib, sys
bad = []
for p in pathlib.Path('ai-sync').rglob('*.py'):
    try:
        ast.parse(p.read_text())
    except SyntaxError as e:
        bad.append((p, str(e)))
if bad:
    for p, e in bad:
        print(f'[FAIL]  python: {p} — {e}')
    sys.exit(1)
else:
    print(f'[OK]    python: all files parse cleanly')
" || fail=1
fi

echo
if (( fail )); then
    echo "VALIDATION FAILED — see output above."
    exit 1
fi
echo "VALIDATION PASSED."
