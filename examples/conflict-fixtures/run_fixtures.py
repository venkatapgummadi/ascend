"""
Report-style runner for the bundled conflict fixtures.

Runs each fixture through ConflictClassifier (heuristic baseline) and prints
the result. Fixtures that the heuristic classifier does NOT solve correctly
are expected -- they demonstrate the motivation for training a classifier
on organization-specific merge conflict history (see ai-sync/README.md).

Usage:
    python examples/conflict-fixtures/run_fixtures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ascend_sync.conflict_classifier import Conflict, ConflictClassifier, ConflictType


def main() -> int:
    fixtures_dir = Path(__file__).parent
    classifier = ConflictClassifier()
    fixtures = sorted(fixtures_dir.glob("*.json"))
    if not fixtures:
        print("No fixtures found.", file=sys.stderr)
        return 1

    print(f"Running {len(fixtures)} fixtures against the heuristic ConflictClassifier.")
    print("Baseline heuristic only. Train the ML classifier on your own data for production.")
    print()

    hits = 0
    for fx in fixtures:
        rec = json.loads(fx.read_text(encoding="utf-8"))
        conflict = Conflict(
            file_path=rec["file_path"],
            ours=rec["ours"],
            theirs=rec["theirs"],
            base=rec.get("base", ""),
        )
        result = classifier.classify(conflict)
        expected_type = ConflictType(rec["expected_type"])
        match = result.conflict_type == expected_type
        if match:
            hits += 1
        status = "HIT " if match else "MISS"
        print(f"[{status}] {fx.name}")
        print(f"    expected: {expected_type.value}")
        print(f"    got:      {result.conflict_type.value} ({result.confidence:.2%})")
        print()

    total = len(fixtures)
    rate = 100 * hits / total
    print(f"Heuristic baseline hit rate: {hits}/{total} ({rate:.0f}%).")
    print("Target with trained ML classifier: >= 90%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
