"""
Benchmark runner for the bundled conflict fixtures.

Reproduces the heuristic-baseline accuracy referenced in the ASCEND paper
(§VII.B). The script:

  * loads every JSON fixture in this directory,
  * classifies each via the heuristic ConflictClassifier,
  * compares against the fixture's labelled `expected_type`,
  * prints a per-fixture report and an aggregate hit rate,
  * optionally emits a machine-readable JSON report (`--json out.json`).

The ML-trained classifier referenced in the paper is trained on
organisation-specific data and is not bundled (see `ai-sync/README.md`).
The heuristic baseline reported here is the lower bound; the trained model
is expected to clear 90% on the same fixtures.

Usage:
    python examples/conflict-fixtures/run_fixtures.py
    python examples/conflict-fixtures/run_fixtures.py --json report.json
    python examples/conflict-fixtures/run_fixtures.py --check expected-results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from ascend_sync.conflict_classifier import Conflict, ConflictClassifier, ConflictType


def run(fixtures_dir: Path) -> dict:
    classifier = ConflictClassifier()
    fixtures = sorted(fixtures_dir.glob("*.json"))
    if not fixtures:
        raise FileNotFoundError(f"no fixtures in {fixtures_dir}")

    per_fixture: list[dict] = []
    by_class_total: Counter[str] = Counter()
    by_class_hits: Counter[str] = Counter()
    hits = 0
    for fx in fixtures:
        rec = json.loads(fx.read_text(encoding="utf-8"))
        # Skip non-fixture JSON files (like an expected-results manifest).
        if "expected_type" not in rec or "ours" not in rec or "theirs" not in rec:
            continue
        conflict = Conflict(
            file_path=rec["file_path"],
            ours=rec["ours"],
            theirs=rec["theirs"],
            base=rec.get("base", ""),
        )
        result = classifier.classify(conflict)
        expected = ConflictType(rec["expected_type"])
        ok = result.conflict_type == expected
        if ok:
            hits += 1
            by_class_hits[expected.value] += 1
        by_class_total[expected.value] += 1
        per_fixture.append({
            "fixture": fx.name,
            "expected": expected.value,
            "predicted": result.conflict_type.value,
            "confidence": round(result.confidence, 4),
            "hit": ok,
        })

    total = len(per_fixture)
    by_class = {
        cls: {
            "n": by_class_total[cls],
            "hits": by_class_hits[cls],
            "accuracy": round(by_class_hits[cls] / by_class_total[cls], 4)
                        if by_class_total[cls] else None,
        }
        for cls in sorted(by_class_total)
    }
    return {
        "classifier": "heuristic-baseline",
        "n_fixtures": total,
        "hits": hits,
        "accuracy": round(hits / total, 4) if total else None,
        "by_class": by_class,
        "per_fixture": per_fixture,
    }


def print_report(report: dict) -> None:
    print(f"Running {report['n_fixtures']} fixtures against the heuristic ConflictClassifier.")
    print("Baseline heuristic only. Train the ML classifier on your own data for production.")
    print()
    for entry in report["per_fixture"]:
        status = "HIT " if entry["hit"] else "MISS"
        print(f"[{status}] {entry['fixture']}")
        print(f"    expected: {entry['expected']}")
        print(f"    got:      {entry['predicted']} ({entry['confidence']:.2%})")
        print()
    print(f"Heuristic baseline hit rate: {report['hits']}/{report['n_fixtures']} "
          f"({report['accuracy']:.0%}).")
    print("Per-class accuracy:")
    for cls, stats in report["by_class"].items():
        acc = stats["accuracy"]
        acc_str = f"{acc:.0%}" if acc is not None else "n/a"
        print(f"  {cls:<14} {stats['hits']}/{stats['n']:<3} ({acc_str})")
    print("Target with trained ML classifier: >= 90%.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path,
                        help="Write the structured report to this path.")
    parser.add_argument("--check", type=Path,
                        help="Compare aggregate accuracy against an expected-results file. "
                             "Exits non-zero on mismatch.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress the human-readable report.")
    args = parser.parse_args()

    fixtures_dir = Path(__file__).parent
    report = run(fixtures_dir)

    if not args.quiet:
        print_report(report)

    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"\nReport written to {args.json}")

    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        if expected.get("accuracy") != report["accuracy"]:
            print(f"\n[FAIL] accuracy {report['accuracy']} != expected {expected.get('accuracy')}",
                  file=sys.stderr)
            return 1
        if not args.quiet:
            print(f"\n[OK] accuracy matches expected ({report['accuracy']}).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
