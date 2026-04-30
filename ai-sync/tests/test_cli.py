"""Tests for the ascend-sync CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ascend_sync.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_version_command(runner: CliRunner) -> None:
    from ascend_sync import __version__
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_top_level_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "ASCEND" in result.output
    assert "detect-drift" in result.output
    assert "classify" in result.output
    assert "resolve" in result.output


def test_classify_command_on_fixture(runner: CliRunner, tmp_path: Path) -> None:
    """Smoke-test the classify command. We assert the command exits cleanly and
    emits structured output containing a recognised conflict_type — not a
    specific heuristic outcome (those are exercised in test_classifier.py)."""
    fixture = tmp_path / "c.json"
    fixture.write_text(json.dumps({
        "file_path": "config.yml",
        "ours": "timeout: 30\nretries: 3\n",
        "theirs": "timeout: 30\nretries: 5\nbackoff: 2\n",
    }))
    result = runner.invoke(main, ["classify", "--file", str(fixture)])
    assert result.exit_code == 0, result.output
    # Rich pretty-prints JSON with colour/wrap; locate the JSON object span.
    out = result.output
    start = out.find("{")
    end = out.rfind("}")
    assert start != -1 and end != -1, out
    payload = json.loads(out[start:end + 1])
    assert payload["conflict_type"] in {"syntactic", "semantic", "structural", "configuration"}
    assert "confidence" in payload


def test_resolve_command_runs_local_provider(runner: CliRunner, tmp_path: Path) -> None:
    fixture = tmp_path / "c.json"
    fixture.write_text(json.dumps({
        "file_path": "auth.py",
        "ours": "def authenticate(token):\n    return validate_token(token)\n",
        "theirs": "def authenticate(token):\n    return is_valid(token)\n",
    }))
    result = runner.invoke(
        main,
        ["resolve", "--file", str(fixture), "--provider", "local",
         "--candidates", "1", "--no-verify"],
    )
    assert result.exit_code == 0, result.output
    assert "Candidate 1" in result.output


def test_detect_drift_command_below_threshold(runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    (src / "m.py").write_text("def f(): return 1\n")
    (tgt / "m.py").write_text("def f(): return 1\n")
    out = tmp_path / "report.json"
    result = runner.invoke(
        main,
        ["detect-drift", "--source", str(src), "--target", str(tgt),
         "--threshold", "0.5", "--output", str(out)],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(out.read_text())
    assert payload["risk_score"] <= 0.5
    assert payload["threshold_exceeded"] is False


def test_detect_drift_exit_nonzero_when_threshold_exceeded(runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    # Make the trees diverge enough to trip a low threshold.
    for i in range(5):
        (src / f"m{i}.py").write_text(f"def f{i}(): return {i}\n")
        (tgt / f"m{i}.py").write_text(f"def f{i}(): return {i + 100}\n")
    result = runner.invoke(
        main,
        ["detect-drift", "--source", str(src), "--target", str(tgt),
         "--threshold", "0.0"],
    )
    assert result.exit_code == 1, result.output
