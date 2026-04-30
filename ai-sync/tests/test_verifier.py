"""Tests for Verifier."""

from ascend_sync.conflict_classifier import Conflict
from ascend_sync.llm_resolver import Resolution
from ascend_sync.verifier import Verifier


def test_verifier_flags_syntax_error():
    conflict = Conflict(file_path="a.py", ours="def f(): pass", theirs="def f(): pass")
    bad = Resolution(resolved_code="def f( pass", provider="local", model="stub", confidence=0.5)
    result = Verifier().verify(conflict, bad)
    assert not result.parse_ok
    assert not result.is_valid


def test_verifier_requires_security_pattern_preservation():
    conflict = Conflict(
        file_path="auth.py",
        ours="def authenticate(token):\n    return validate_token(token)\n",
        theirs="def authenticate(token):\n    return validate_token(token)\n",
    )
    missing = Resolution(
        resolved_code="def authenticate(token):\n    return True\n",
        provider="local", model="stub", confidence=0.5,
    )
    result = Verifier().verify(conflict, missing)
    assert not result.security_patterns_preserved
    assert not result.is_valid


def test_verifier_accepts_good_resolution():
    conflict = Conflict(
        file_path="a.py",
        ours="def add(x, y): return x + y\n",
        theirs="def add(x, y): return x + y  # commented\n",
    )
    good = Resolution(
        resolved_code="def add(x, y): return x + y\n",
        provider="local", model="stub", confidence=0.9,
    )
    result = Verifier().verify(conflict, good)
    assert result.parse_ok
    assert result.is_valid


def test_verifier_property_tests_are_deterministic():
    """Repeated runs must produce the same passed/total counts (sets ordering bug regression)."""
    from ascend_sync.verifier import Verifier

    conflict = Conflict(
        file_path="m.py",
        ours="def a(): foo(); bar(); baz()",
        theirs="def b(): qux(); quux(); corge()",
    )
    resolved = Resolution(
        resolved_code="def both(): foo(); bar(); baz(); qux(); quux(); corge()",
        provider="local", model="stub", confidence=0.9,
    )
    v = Verifier()
    runs = [v.verify(conflict, resolved) for _ in range(5)]
    counts = {(r.property_tests_passed, r.property_tests_total) for r in runs}
    assert len(counts) == 1, f"non-deterministic property test counts: {counts}"


def test_verifier_handles_empty_resolution():
    from ascend_sync.verifier import Verifier
    conflict = Conflict(file_path="a.py", ours="def f(): pass", theirs="def f(): pass")
    empty = Resolution(resolved_code="", provider="local", model="stub", confidence=0.0)
    result = Verifier().verify(conflict, empty)
    assert not result.parse_ok
    assert not result.is_valid


def test_verifier_to_dict_serializable():
    """Verification result round-trips through json."""
    import json

    from ascend_sync.verifier import Verifier
    conflict = Conflict(file_path="a.py", ours="def f(): pass", theirs="def g(): pass")
    res = Resolution(resolved_code="def f(): pass\ndef g(): pass\n",
                     provider="local", model="stub", confidence=0.9)
    out = Verifier().verify(conflict, res).to_dict()
    json.dumps(out)  # must not raise
    assert out["is_valid"] is True
