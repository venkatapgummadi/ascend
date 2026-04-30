"""Tests for PROrchestrator.

Covers PR-body construction (deterministic), title formatting, and the
HTTP layer with a mocked requests session. We avoid real network calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ascend_sync.conflict_classifier import Conflict, ConflictType
from ascend_sync.llm_resolver import Resolution
from ascend_sync.pr_orchestrator import PROrchestrator, PRResult
from ascend_sync.verifier import VerificationResult


@pytest.fixture
def conflict() -> Conflict:
    return Conflict(file_path="auth.py", ours="def f(): pass", theirs="def g(): pass")


@pytest.fixture
def resolution() -> Resolution:
    return Resolution(
        resolved_code="def f(): pass\ndef g(): pass\n",
        provider="local",
        model="stub",
        confidence=0.85,
    )


@pytest.fixture
def verification() -> VerificationResult:
    return VerificationResult(
        is_valid=True,
        parse_ok=True,
        signatures_preserved=True,
        security_patterns_preserved=True,
        property_tests_passed=4,
        property_tests_total=4,
    )


def test_build_title_includes_conflict_type_and_sha():
    orch = PROrchestrator(github_token="ghp_test")
    title = orch._build_title(ConflictType.SEMANTIC, "abcdef1234567890")
    assert "[AI-Sync]" in title
    assert "semantic" in title
    assert "abcdef1" in title  # sha truncated to 7 chars


def test_build_title_without_sha():
    orch = PROrchestrator(github_token="ghp_test")
    title = orch._build_title(ConflictType.STRUCTURAL, None)
    assert "[AI-Sync]" in title
    assert "structural" in title


def test_build_body_renders_all_sections(conflict, resolution, verification):
    orch = PROrchestrator(github_token="ghp_test")
    body = orch._build_body(conflict, resolution, verification, ConflictType.SEMANTIC, "abc123")
    assert "auth.py" in body
    assert "semantic" in body
    assert "85.00%" in body  # confidence rendered as percent
    assert "abc123" in body
    assert "Parses: **True**" in body
    assert "Signatures preserved: **True**" in body
    assert "4/4" in body  # property test ratio
    assert "ASCEND" in body


def test_build_body_includes_failure_reasons():
    orch = PROrchestrator(github_token="ghp_test")
    conflict = Conflict(file_path="x.py", ours="", theirs="")
    res = Resolution(resolved_code="", provider="local", model="stub", confidence=0.0)
    failed = VerificationResult(
        is_valid=False, parse_ok=False, signatures_preserved=False,
        security_patterns_preserved=True, failure_reasons=["did not parse"],
    )
    body = orch._build_body(conflict, res, failed, ConflictType.SYNTACTIC, None)
    assert "Verification Failures" in body
    assert "did not parse" in body


def test_headers_use_bearer_and_api_version():
    orch = PROrchestrator(github_token="ghp_test")
    h = orch._headers()
    assert h["Authorization"] == "Bearer ghp_test"
    assert h["Accept"] == "application/vnd.github+json"
    assert h["X-GitHub-Api-Version"] == "2022-11-28"


def test_default_labels_applied():
    orch = PROrchestrator(github_token="t")
    assert "ai-sync" in orch.default_labels
    assert "automated" in orch.default_labels


def test_no_token_warns_but_does_not_raise(caplog):
    import logging
    caplog.set_level(logging.WARNING)
    orch = PROrchestrator(github_token="")
    assert orch.github_token == ""
    assert any("GITHUB_TOKEN" in record.message for record in caplog.records)


def test_create_pr_calls_api_and_returns_result(conflict, resolution, verification):
    orch = PROrchestrator(github_token="ghp_test", default_labels=[], default_reviewers=[])
    with patch("ascend_sync.pr_orchestrator.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            ok=True,
            json=lambda: {"html_url": "https://x/y/pull/42", "number": 42},
            raise_for_status=lambda: None,
        )
        result = orch.create_pr(
            repo="org/repo",
            base_branch="main",
            head_branch="ai-sync/fix",
            conflict=conflict,
            resolution=resolution,
            verification=verification,
            conflict_type=ConflictType.SEMANTIC,
            hotfix_sha="deadbeef",
        )
    assert isinstance(result, PRResult)
    assert result.pr_number == 42
    assert "pull/42" in result.pr_url
    assert result.branch_name == "ai-sync/fix"
    # The mock should have been called once (no labels/reviewers configured → no extra calls)
    assert mock_post.call_count == 1


def test_api_base_strips_trailing_slash():
    orch = PROrchestrator(github_token="t", api_base="https://github.example.com/api/v3/")
    assert orch.api_base == "https://github.example.com/api/v3"
