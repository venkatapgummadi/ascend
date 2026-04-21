# ASCEND AI Synchronization Module

Layer 4 of the ASCEND framework: post-deployment code synchronization across multi-track deployment branches using AST-based drift detection, ML-assisted conflict classification, and LLM-based conflict resolution.

## What it does

After a hotfix is deployed to a production branch, the AI sync module:

1. **Detects drift** between production, staging, and development branches using AST differencing and configuration fingerprinting, skipping cosmetic differences (whitespace, comments, formatting).
2. **Classifies conflicts** into one of four categories (syntactic, semantic, structural, configuration) using a trained classifier.
3. **Resolves conflicts** using an LLM conditioned on the three-way merge context (ours, theirs, base).
4. **Verifies resolutions** using property-based testing to ensure functional equivalence.
5. **Creates pull requests** with high-confidence resolutions, marked `[AI-Sync]` and linked to the original hotfix.

## Install

```bash
cd ai-sync
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
pytest tests/
```

## Usage

### CLI

Detect drift between two branches:

```bash
ascend-sync detect-drift --repo /path/to/repo --source main --target develop
```

Resolve a specific merge conflict interactively:

```bash
ascend-sync resolve --conflict-file path/to/conflict.py
```

Run the full post-deploy sync workflow:

```bash
ascend-sync post-deploy-sync \
    --repo /path/to/repo \
    --production-sha abc123 \
    --target-branches develop,staging \
    --create-prs
```

### As a webhook service

```bash
ascend-sync serve --host 0.0.0.0 --port 8080
```

Then configure your CI/CD pipeline to POST to `http://<host>:8080/post-deploy` with JSON body:

```json
{
  "repo": "org/repo",
  "sha": "abc123",
  "trigger": "post-deploy"
}
```

## Configuration

Create `ai-sync/config.yml`:

```yaml
drift:
  schedule: "0 */6 * * *"        # cron — every 6 hours
  threshold: 0.30                # drift risk score threshold
  branches: [main, staging, develop]

classification:
  model: models/conflict_classifier.pkl
  confidence_threshold: 0.85

resolution:
  provider: openai               # openai | anthropic | local
  model: gpt-4o-mini             # model name
  max_candidates: 3
  temperature: 0.2

verification:
  property_tests: 10000
  timeout_seconds: 60

pr_orchestrator:
  github_token: ${GITHUB_TOKEN}
  base_branch: develop
  labels: [ai-sync, automated]
  reviewers: [security-team]
```

## How drift detection works

Given branches `A` and `B`, drift detection computes:

1. **AST diff** (`δ_semantic`) — tree-level differences ignoring formatting.
2. **Configuration diff** (`δ_config`) — differences in config files (YAML, JSON, TOML, env).
3. **Code embeddings** (`e_A`, `e_B`) — dense vectors from a code language model.
4. **Risk score** `r = f(δ_semantic, δ_config, ‖e_A − e_B‖₂)` via a trained MLP.

When `r > θ`, drift is reported and sync is triggered.

## How conflict resolution works

For each merge conflict region:

1. **Classifier** assigns one of: syntactic, semantic, structural, configuration.
2. **LLM** generates candidate resolutions conditioned on `(c_ours, c_theirs, c_base)`.
3. **Verifier** runs property-based tests on each candidate; `Valid(r) = ∀x : f_merged(x; r) ≡ f_expected(x)`.
4. **PR orchestrator** opens a PR with the highest-confidence valid candidate.

Human review is always required before merge — AI sync proposes, humans dispose.

## Model training

The shipped classifier is a baseline model. For production use, retrain on your organization's historical merge conflict resolutions:

```bash
python -m ascend_sync.train \
    --input data/merge_conflicts.jsonl \
    --output models/conflict_classifier.pkl \
    --validation-split 0.2
```

Input format — one JSON object per line:

```json
{"conflict_type": "semantic", "ours": "...", "theirs": "...", "base": "...", "resolved": "..."}
```

## Limitations

- Requires ≥500 historical resolutions to train a reliable classifier.
- LLM providers have rate limits and may return non-deterministic suggestions.
- Property-based verification requires target code to be testable (pure functions or small side-effect surfaces).
- Structural conflicts (architectural refactoring) have lower resolution accuracy (~87%).

## License

MIT — see [../LICENSE](../LICENSE).
