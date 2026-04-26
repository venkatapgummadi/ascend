# AI Synchronization Module — API Reference

Python API reference for the `ascend_sync` package. Public classes are exported from the package root; internal helpers are considered private and may change.

## Package overview

```python
from ascend_sync import (
    DriftDetector, DriftReport,
    ConflictClassifier, ConflictType,
    LLMResolver, Resolution,
    Verifier, VerificationResult,
    PROrchestrator,
)
```

## `DriftDetector`

Detects semantic drift between two code trees using AST differencing, configuration fingerprinting, and embedding distance.

```python
class DriftDetector:
    def __init__(
        self,
        threshold: float = 0.30,
        weight_semantic: float = 0.50,
        weight_config: float = 0.25,
        weight_embedding: float = 0.25,
    ) -> None: ...

    def compare_trees(
        self,
        source_root: Path,
        target_root: Path,
        source_ref: str = "source",
        target_ref: str = "target",
    ) -> DriftReport: ...
```

### Example

```python
from pathlib import Path
from ascend_sync import DriftDetector

detector = DriftDetector(threshold=0.25)
report = detector.compare_trees(
    source_root=Path("/repos/my-service/production"),
    target_root=Path("/repos/my-service/develop"),
    source_ref="production",
    target_ref="develop",
)

if report.threshold_exceeded:
    print(f"Drift alert: {report.explanation}")
    for f in report.affected_files:
        print(f"  - {f}")
```

### `DriftReport` fields

| Field | Type | Description |
|-------|------|-------------|
| `source_ref` | `str` | Human-readable source reference |
| `target_ref` | `str` | Human-readable target reference |
| `risk_score` | `float` | Combined risk in `[0, 1]` |
| `semantic_changes` | `int` | Count of AST-level differences |
| `config_changes` | `int` | Count of changed config files |
| `embedding_distance` | `float` | Code embedding distance (proxy or real) |
| `affected_files` | `list[str]` | Relative paths with detected changes |
| `threshold_exceeded` | `bool` | `risk_score > threshold` |
| `explanation` | `str` | Human-readable summary |

### `iter_reports` helper

Pairwise drift comparison across multiple branches:

```python
from ascend_sync.drift_detector import iter_reports

branches = [
    (Path("/repos/production"), "production"),
    (Path("/repos/staging"), "staging"),
    (Path("/repos/develop"), "develop"),
]
for report in iter_reports(detector, branches):
    ...
```

---

## `ConflictClassifier`

Classifies merge conflicts into one of four types using feature extraction and (optionally) a trained sklearn classifier.

```python
class ConflictClassifier:
    def __init__(
        self,
        model_path: Path | None = None,
        confidence_threshold: float = 0.85,
    ) -> None: ...

    def classify(self, conflict: Conflict) -> Classification: ...
    def classify_batch(self, conflicts: list[Conflict]) -> list[Classification]: ...
```

### `Conflict` dataclass

```python
@dataclass
class Conflict:
    file_path: str
    ours: str           # your branch's version
    theirs: str         # their branch's version
    base: str = ""      # common ancestor (optional but recommended)
    line_start: int = 0
    line_end: int = 0
```

### `ConflictType` enum

```python
class ConflictType(str, Enum):
    SYNTACTIC = "syntactic"          # formatting / renaming / cosmetic
    SEMANTIC = "semantic"            # logic changes in overlapping code
    STRUCTURAL = "structural"        # architectural refactoring
    CONFIGURATION = "configuration"  # environment-specific parameters
```

### Example — heuristic classifier

```python
from ascend_sync import ConflictClassifier
from ascend_sync.conflict_classifier import Conflict

conflict = Conflict(
    file_path="app/auth.py",
    ours="def authenticate(token):\n    return validate_token(token)\n",
    theirs="def authenticate(token):\n    return oauth_verify(token)\n",
)

classifier = ConflictClassifier()
result = classifier.classify(conflict)
print(result.conflict_type, result.confidence)  # SEMANTIC 0.80
```

### Example — trained classifier

```python
classifier = ConflictClassifier(model_path=Path("models/conflict_classifier.pkl"))
result = classifier.classify(conflict)
```

See `ai-sync/README.md` for the training data format and training script.

---

## `LLMResolver`

LLM-backed resolution generator. Supports OpenAI, Anthropic, and a local stub for offline testing.

```python
class LLMResolver:
    def __init__(
        self,
        provider: Literal["openai", "anthropic", "local"] = "local",
        model: str = "stub-model",
        max_candidates: int = 3,
        temperature: float = 0.2,
    ) -> None: ...

    def resolve(
        self,
        conflict: Conflict,
        conflict_type: ConflictType,
        historical_context: str = "",
    ) -> list[Resolution]: ...
```

### `Resolution` dataclass

```python
@dataclass
class Resolution:
    resolved_code: str
    provider: str
    model: str
    confidence: float
    reasoning: str = ""
    preserves_invariants: list[str] = None
```

### Example — OpenAI provider

```python
import os
from ascend_sync import LLMResolver, ConflictClassifier
from ascend_sync.conflict_classifier import Conflict

os.environ["OPENAI_API_KEY"] = "sk-..."

resolver = LLMResolver(provider="openai", model="gpt-4o-mini", max_candidates=3)
classifier = ConflictClassifier()

conflict = Conflict(file_path="foo.py", ours="...", theirs="...")
classification = classifier.classify(conflict)
candidates = resolver.resolve(conflict, classification.conflict_type)

for r in candidates:
    print(f"Confidence {r.confidence:.2%}:\n{r.resolved_code}\n")
```

### Example — Anthropic provider

```python
import os
from ascend_sync import LLMResolver

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

resolver = LLMResolver(provider="anthropic", model="claude-opus-4-6", max_candidates=3)
candidates = resolver.resolve(conflict, classification.conflict_type)
```

### Example — local stub (no API key)

```python
resolver = LLMResolver(provider="local")
candidates = resolver.resolve(conflict, classification.conflict_type)
# Returns a single conservative union of both sides.
```

---

## `Verifier`

Validates candidate resolutions against parse, signature preservation, security pattern preservation, and property tests.

```python
class Verifier:
    def __init__(self, property_tests: int = 100) -> None: ...

    def verify(
        self,
        conflict: Conflict,
        resolution: Resolution,
    ) -> VerificationResult: ...
```

### `VerificationResult` fields

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | `bool` | All checks passed |
| `parse_ok` | `bool` | Resolved code parses |
| `signatures_preserved` | `bool` | Public def/class names preserved |
| `security_patterns_preserved` | `bool` | Authentication/crypto/validation patterns preserved |
| `failure_reasons` | `list[str]` | Human-readable failure descriptions |
| `property_tests_passed` | `int` | Passing property test count |
| `property_tests_total` | `int` | Total property tests run |

### Example

```python
from ascend_sync import Verifier

verifier = Verifier(property_tests=1000)
for candidate in candidates:
    result = verifier.verify(conflict, candidate)
    if result.is_valid:
        print("Acceptable candidate:", candidate.resolved_code)
        break
    else:
        print("Rejected:", result.failure_reasons)
```

---

## `PROrchestrator`

Creates pull requests on GitHub (or GitHub Enterprise) with AI-generated resolutions.

```python
class PROrchestrator:
    def __init__(
        self,
        github_token: str | None = None,
        api_base: str = "https://api.github.com",
        default_labels: list[str] | None = None,
        default_reviewers: list[str] | None = None,
    ) -> None: ...

    def create_pr(
        self,
        repo: str,              # "org/repo"
        base_branch: str,       # target branch
        head_branch: str,       # branch with the resolution commit
        conflict: Conflict,
        resolution: Resolution,
        verification: VerificationResult,
        conflict_type: ConflictType,
        hotfix_sha: str | None = None,
    ) -> PRResult: ...
```

### Example

```python
import os
from ascend_sync import PROrchestrator

os.environ["GITHUB_TOKEN"] = "ghp_..."

orchestrator = PROrchestrator(
    default_labels=["ai-sync", "automated", "needs-review"],
    default_reviewers=["security-team"],
)

pr_result = orchestrator.create_pr(
    repo="my-org/my-repo",
    base_branch="develop",
    head_branch="ai-sync/cve-2025-abcd-auth-backport",
    conflict=conflict,
    resolution=best_candidate,
    verification=verification,
    conflict_type=ConflictType.SEMANTIC,
    hotfix_sha="abc123",
)

print(f"PR created: {pr_result.pr_url}")
```

Note: the head branch must already exist in the repo with the resolved code committed. The orchestrator does not create commits — only pull requests.

---

## CLI reference

The `ascend-sync` CLI exposes the same functionality for shell usage.

```
Usage: ascend-sync [OPTIONS] COMMAND [ARGS]...

  ASCEND AI Synchronization Module.

Options:
  --version      Show version.
  -v, --verbose  Enable verbose logging.
  --help         Show this message and exit.

Commands:
  detect-drift   Detect semantic drift between two filesystem trees.
  classify       Classify a merge conflict from a JSON description.
  resolve        Generate candidate resolutions for a merge conflict.
  version        Print the package version.
```

Each subcommand has its own `--help`. See `ai-sync/README.md` for end-to-end usage examples.

---

## Threading and async

The library is synchronous by default. For server use, wrap calls in `asyncio.to_thread()`:

```python
import asyncio
from ascend_sync import DriftDetector

detector = DriftDetector()

async def detect_async(source, target):
    return await asyncio.to_thread(detector.compare_trees, source, target)
```

An async-native version is on the roadmap.

## Error handling

Each public method raises one of:

| Exception | Raised when |
|-----------|-------------|
| `ValueError` | Invalid provider name, malformed conflict, unsupported file type |
| `FileNotFoundError` | Input paths do not exist |
| `RuntimeError` | LLM provider initialization failure (missing API key, missing extra) |
| `requests.HTTPError` | GitHub API errors (rate limit, auth, repo not found) |

All methods use `tenacity` retries for transient network errors (3 attempts, exponential backoff).

## Versioning

The package follows [Semantic Versioning](https://semver.org). Public API stability guarantees:

- **Major version bumps** (`0.x.y` → `1.0.0`) may change class signatures.
- **Minor version bumps** (`0.1.x` → `0.2.0`) may add fields to dataclasses.
- **Patch version bumps** (`0.1.0` → `0.1.1`) are bug-fix only.

Until `1.0.0`, the API is marked alpha. Breaking changes will be documented in [CHANGELOG.md](../CHANGELOG.md).


---

## Auto-generated contribution

Added by bounty bot.
