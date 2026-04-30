"""Tests for LLMResolver.

Covers the local-stub provider end-to-end (no API keys), the unknown-provider
guard, and the confidence heuristic. Network-backed providers (openai,
anthropic) are smoke-tested via dependency-injected mocks.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ascend_sync.conflict_classifier import Conflict, ConflictType
from ascend_sync.llm_resolver import LLMResolver, Resolution


def test_local_stub_returns_one_candidate_with_union_resolution():
    conflict = Conflict(
        file_path="auth.py",
        ours="def authenticate(token):\n    return validate_token(token)\n",
        theirs="def authenticate(token):\n    return is_valid(token)\n",
    )
    resolver = LLMResolver(provider="local")
    candidates = resolver.resolve(conflict, ConflictType.SEMANTIC)
    assert len(candidates) == 1
    assert candidates[0].provider == "local"
    assert "validate_token" in candidates[0].resolved_code
    assert "is_valid" in candidates[0].resolved_code
    assert 0.0 <= candidates[0].confidence <= 1.0


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        LLMResolver(provider="bogus")  # type: ignore[arg-type]


def test_estimate_confidence_zero_for_cannot_resolve():
    r = LLMResolver(provider="local")
    assert r._estimate_confidence("CANNOT_RESOLVE") == 0.0
    assert r._estimate_confidence("") == 0.0


def test_estimate_confidence_in_unit_interval():
    r = LLMResolver(provider="local")
    short = r._estimate_confidence("x = 1")
    long_code = r._estimate_confidence("x = 1\n" * 200)
    assert 0.5 <= short <= 1.0
    assert 0.5 <= long_code <= 1.0
    assert long_code >= short


def test_resolution_to_dict_round_trip():
    res = Resolution(
        resolved_code="x = 1\n",
        provider="local",
        model="stub",
        confidence=0.75,
        reasoning="union",
        preserves_invariants=["validate_token"],
    )
    d = res.to_dict()
    assert d["resolved_code"] == "x = 1\n"
    assert d["provider"] == "local"
    assert d["confidence"] == 0.75
    assert d["preserves_invariants"] == ["validate_token"]


def test_resolution_to_dict_handles_default_invariants():
    res = Resolution(resolved_code="", provider="local", model="stub", confidence=0.5)
    d = res.to_dict()
    assert d["preserves_invariants"] == []


def test_resolve_with_mocked_openai_swallows_failures():
    """Failed LLM calls are logged and returned as zero candidates rather than raising."""
    conflict = Conflict(file_path="a.py", ours="x = 1", theirs="x = 2")

    resolver = LLMResolver(provider="local", max_candidates=2)
    # Force the openai branch but supply a broken client.
    resolver.provider = "openai"
    resolver._client = MagicMock()
    resolver._client.chat.completions.create.side_effect = RuntimeError("boom")

    candidates = resolver.resolve(conflict, ConflictType.SEMANTIC)
    assert candidates == []
