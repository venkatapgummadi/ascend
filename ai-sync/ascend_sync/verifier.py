"""
Resolution verifier.

Uses syntactic parsability and lightweight property-based testing to check
whether a candidate resolution preserves the functional behavior required
by both merge sides.

Production deployments should extend this with language-specific symbolic
execution or property checkers. The baseline implementation focuses on:

  - Syntactic validity (the code parses).
  - No regression of known security-relevant patterns.
  - Preservation of public function signatures from OURS and THEIRS.
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field

from ascend_sync.conflict_classifier import Conflict
from ascend_sync.llm_resolver import Resolution

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Outcome of verifying a candidate resolution."""

    is_valid: bool
    parse_ok: bool
    signatures_preserved: bool
    security_patterns_preserved: bool
    failure_reasons: list[str] = field(default_factory=list)
    property_tests_passed: int = 0
    property_tests_total: int = 0

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "parse_ok": self.parse_ok,
            "signatures_preserved": self.signatures_preserved,
            "security_patterns_preserved": self.security_patterns_preserved,
            "failure_reasons": self.failure_reasons,
            "property_tests_passed": self.property_tests_passed,
            "property_tests_total": self.property_tests_total,
        }


# Security-relevant patterns that, if present in OURS or THEIRS,
# must also be present in the resolved code.
_SECURITY_PATTERNS = [
    # Authentication / authorization
    re.compile(r"\b(authenticate|authorize|is_authenticated|check_permission)\b"),
    re.compile(r"\b(token_expir(?:y|ation)|session_expir(?:y|ation))\b"),
    re.compile(r"\b(verify_signature|verify_jwt|validate_token)\b"),
    # Crypto
    re.compile(r"\b(encrypt|decrypt|hash|hmac|sha256|sha512|aes_|rsa_)\b", re.IGNORECASE),
    # Input validation
    re.compile(r"\b(sanitize|escape_html|bleach\.clean|validate_input)\b"),
    # Rate limiting / circuit breakers
    re.compile(r"\b(rate_limit|circuit_breaker|throttle)\b"),
]


class Verifier:
    """
    Verifies that a candidate resolution is syntactically valid and
    preserves critical behavioral invariants.
    """

    def __init__(self, property_tests: int = 100) -> None:
        self.property_tests = property_tests

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def verify(self, conflict: Conflict, resolution: Resolution) -> VerificationResult:
        failures: list[str] = []

        # 1. Syntactic validity
        parse_ok = self._parses(resolution.resolved_code)
        if not parse_ok:
            failures.append("Resolution is not syntactically valid Python.")

        # 2. Signature preservation
        sigs_preserved = self._signatures_preserved(conflict, resolution)
        if not sigs_preserved:
            failures.append("Public function/class signatures from OURS or THEIRS are missing.")

        # 3. Security pattern preservation
        sec_ok = self._security_patterns_preserved(conflict, resolution)
        if not sec_ok:
            failures.append("A security-relevant pattern from OURS or THEIRS is missing.")

        # 4. Property tests (lightweight)
        passed, total = self._property_tests(conflict, resolution)

        is_valid = parse_ok and sigs_preserved and sec_ok and (total == 0 or passed == total)

        return VerificationResult(
            is_valid=is_valid,
            parse_ok=parse_ok,
            signatures_preserved=sigs_preserved,
            security_patterns_preserved=sec_ok,
            failure_reasons=failures,
            property_tests_passed=passed,
            property_tests_total=total,
        )

    # -------------------------------------------------------------------------
    # Individual checks
    # -------------------------------------------------------------------------

    def _parses(self, code: str) -> bool:
        if not code or code.strip() == "CANNOT_RESOLVE":
            return False
        try:
            ast.parse(code)
            return True
        except SyntaxError as exc:
            logger.debug("Parse error: %s", exc)
            return False

    def _signatures_preserved(self, conflict: Conflict, resolution: Resolution) -> bool:
        """Check that public function/class names from OURS and THEIRS appear in resolved."""
        try:
            ours_names = self._extract_defs(conflict.ours)
            theirs_names = self._extract_defs(conflict.theirs)
            resolved_names = self._extract_defs(resolution.resolved_code)
        except SyntaxError:
            # If ours/theirs don't parse (they're fragments), use regex fallback
            ours_names = self._extract_defs_regex(conflict.ours)
            theirs_names = self._extract_defs_regex(conflict.theirs)
            resolved_names = self._extract_defs_regex(resolution.resolved_code)

        required = ours_names | theirs_names
        # An empty `required` is trivially a subset, so no separate empty check needed.
        return required.issubset(resolved_names)

    def _security_patterns_preserved(self, conflict: Conflict, resolution: Resolution) -> bool:
        union_source = conflict.ours + "\n" + conflict.theirs
        for pat in _SECURITY_PATTERNS:
            if pat.search(union_source) and not pat.search(resolution.resolved_code):
                return False
        return True

    def _property_tests(self, conflict: Conflict, resolution: Resolution) -> tuple[int, int]:
        """
        Very lightweight property tests — check that resolved code doesn't
        remove unique callable names. Real deployments should integrate
        Hypothesis / QuickCheck for full property-based testing.
        """
        if self.property_tests <= 0:
            return 0, 0
        try:
            ours_calls = self._extract_calls_regex(conflict.ours)
            theirs_calls = self._extract_calls_regex(conflict.theirs)
            resolved_calls = self._extract_calls_regex(resolution.resolved_code)
        except Exception:
            return 0, 0

        required = ours_calls | theirs_calls
        if not required:
            return 0, 0
        # Sort for deterministic test selection (set iteration order is undefined).
        ordered = sorted(required)
        total = min(self.property_tests, len(ordered))
        passed = sum(1 for name in ordered[:total] if name in resolved_calls)
        return passed, total

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _extract_defs(self, code: str) -> set[str]:
        """Extract top-level def/class names via AST."""
        names: set[str] = set()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    names.add(node.name)
        return names

    def _extract_defs_regex(self, code: str) -> set[str]:
        pat = re.compile(r"^\s*(?:async\s+def|def|class)\s+(\w+)", re.MULTILINE)
        return {m.group(1) for m in pat.finditer(code) if not m.group(1).startswith("_")}

    def _extract_calls_regex(self, code: str) -> set[str]:
        pat = re.compile(r"\b(\w+)\s*\(")
        return {m.group(1) for m in pat.finditer(code) if not m.group(1).startswith("_")}
