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
