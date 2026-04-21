"""
Example end-to-end sync workflow.

Usage:
    python example_sync.py

Demonstrates:
  1. Drift detection between two branch checkouts.
  2. Conflict classification.
  3. LLM-backed resolution (local stub — no API keys required).
  4. Verification of the resolution.

Does NOT open a real pull request.
"""

import json
import tempfile
from pathlib import Path

from ascend_sync.conflict_classifier import Conflict, ConflictClassifier
from ascend_sync.drift_detector import DriftDetector
from ascend_sync.llm_resolver import LLMResolver
from ascend_sync.verifier import Verifier


def main() -> None:
    # -------------------------------------------------------------------------
    # Step 1: Set up two tree snapshots simulating a production vs. development
    # branch divergence after a hotfix.
    # -------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        production = tmp_path / "production"
        develop = tmp_path / "develop"

        (production / "app").mkdir(parents=True)
        (production / "app" / "auth.py").write_text(
            "def authenticate(token):\n"
            "    # hotfix: strict token expiry validation\n"
            "    if token_expiration(token) < now():\n"
            "        return False\n"
            "    return validate_token(token)\n",
            encoding="utf-8",
        )

        (develop / "app").mkdir(parents=True)
        (develop / "app" / "auth.py").write_text(
            "def authenticate(token):\n"
            "    # OAuth 2.0 device authorization flow\n"
            "    if is_device_flow(token):\n"
            "        return oauth_device_verify(token)\n"
            "    return validate_token(token)\n",
            encoding="utf-8",
        )

        # ---------------------------------------------------------------------
        # Step 2: Detect drift
        # ---------------------------------------------------------------------
        print("=== Step 1: Drift Detection ===")
        detector = DriftDetector(threshold=0.15)
        report = detector.compare_trees(production, develop, "production", "develop")
        print(json.dumps(report.to_dict(), indent=2))

        # ---------------------------------------------------------------------
        # Step 3: Classify the conflict
        # ---------------------------------------------------------------------
        print("\n=== Step 2: Conflict Classification ===")
        conflict = Conflict(
            file_path="app/auth.py",
            ours=(production / "app" / "auth.py").read_text(),
            theirs=(develop / "app" / "auth.py").read_text(),
        )
        classifier = ConflictClassifier()
        classification = classifier.classify(conflict)
        print(json.dumps(classification.to_dict(), indent=2))

        # ---------------------------------------------------------------------
        # Step 4: Resolve (local stub — no API calls)
        # ---------------------------------------------------------------------
        print("\n=== Step 3: LLM Resolution (local stub) ===")
        resolver = LLMResolver(provider="local", max_candidates=1)
        candidates = resolver.resolve(conflict, classification.conflict_type)
        for i, resolution in enumerate(candidates):
            print(f"Candidate {i + 1} (confidence {resolution.confidence:.2%}):")
            print(resolution.resolved_code)

        # ---------------------------------------------------------------------
        # Step 5: Verify
        # ---------------------------------------------------------------------
        print("\n=== Step 4: Verification ===")
        verifier = Verifier()
        for i, resolution in enumerate(candidates):
            result = verifier.verify(conflict, resolution)
            print(f"Candidate {i + 1}: {json.dumps(result.to_dict(), indent=2)}")


if __name__ == "__main__":
    main()
