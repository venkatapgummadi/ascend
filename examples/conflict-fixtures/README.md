# Conflict Fixtures

JSON fixtures representing each of the four merge conflict types defined by ASCEND's AI synchronization module. Use these for testing the classifier, experimenting with the resolver, or training a custom model.

## Format

Each fixture is a JSON file with the following schema:

```json
{
  "file_path": "path/relative/to/repo",
  "ours": "our branch's version of the conflicting code",
  "theirs": "their branch's version of the conflicting code",
  "base": "(optional) common ancestor version",
  "expected_type": "syntactic | semantic | structural | configuration",
  "expected_confidence_floor": 0.7,
  "description": "Human-readable explanation of the conflict"
}
```

The `expected_type` and `expected_confidence_floor` fields are metadata for tests; they are not consumed by the classifier at inference time.

## Fixtures in this directory

| File | Type | Heuristic handles? | What it tests |
|------|------|-------------------|---------------|
| [`01-syntactic-whitespace.json`](./01-syntactic-whitespace.json) | Syntactic | Yes | Whitespace-only diff recognition |
| [`02-syntactic-import-reorder.json`](./02-syntactic-import-reorder.json) | Syntactic | No | Import-only diff where shared code contains function defs |
| [`03-semantic-auth-logic.json`](./03-semantic-auth-logic.json) | Semantic | Yes | Authentication logic change |
| [`04-semantic-hotfix-vs-refactor.json`](./04-semantic-hotfix-vs-refactor.json) | Semantic | Yes | Hotfix applied to refactored code |
| [`05-structural-class-split.json`](./05-structural-class-split.json) | Structural | No | Class extracted across module boundaries |
| [`06-configuration-yaml-values.json`](./06-configuration-yaml-values.json) | Configuration | Yes | YAML config value changes |
| [`07-configuration-env-new-keys.json`](./07-configuration-env-new-keys.json) | Configuration | No | .env file with new keys added on both sides |

The "Heuristic handles?" column reflects the baseline classifier's out-of-the-box accuracy. Fixtures marked "No" are intentionally included — they exercise cases that demonstrate the value of training the classifier on organization-specific merge conflict history (see [`ai-sync/README.md`](../../ai-sync/README.md) for the training workflow).

## Using fixtures in tests

```python
import json
from pathlib import Path

from ascend_sync.conflict_classifier import Conflict, ConflictClassifier, ConflictType

classifier = ConflictClassifier()

for fixture_path in Path("examples/conflict-fixtures").glob("*.json"):
    rec = json.loads(fixture_path.read_text())
    conflict = Conflict(
        file_path=rec["file_path"],
        ours=rec["ours"],
        theirs=rec["theirs"],
        base=rec.get("base", ""),
    )
    result = classifier.classify(conflict)
    expected = ConflictType(rec["expected_type"])
    assert result.conflict_type == expected, (
        f"{fixture_path.name}: expected {expected}, got {result.conflict_type}"
    )
    assert result.confidence >= rec["expected_confidence_floor"]
    print(f"{fixture_path.name}: {result.conflict_type.value} ({result.confidence:.2%})")
```

## Contributing new fixtures

Contributions welcome, especially:

- Non-Python / non-YAML conflicts (JavaScript, Go, Java, Terraform).
- Real-world conflicts you'd like the classifier to handle better (anonymize first).
- Adversarial cases designed to break classification rules.

Submit via pull request with a clear description of what pattern the fixture exercises.
