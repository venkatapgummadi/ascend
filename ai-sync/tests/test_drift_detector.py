"""Tests for DriftDetector."""

from pathlib import Path

from ascend_sync.drift_detector import DriftDetector


def _write(dir_path: Path, rel: str, content: str) -> None:
    full = dir_path / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


def test_no_drift_when_identical(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    _write(a, "mod.py", "def f():\n    return 1\n")
    _write(b, "mod.py", "def f():\n    return 1\n")
    report = DriftDetector().compare_trees(a, b, "a", "b")
    assert report.semantic_changes == 0
    assert report.risk_score < 0.3


def test_drift_detected_when_logic_changes(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    _write(a, "auth.py", "def authenticate(token):\n    return True\n")
    _write(b, "auth.py", "def authenticate(token):\n    return validate_token(token)\n")
    report = DriftDetector(threshold=0.1).compare_trees(a, b, "a", "b")
    assert report.semantic_changes >= 1
    assert "auth.py" in report.affected_files


def test_whitespace_only_is_not_semantic_drift(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    _write(a, "mod.py", "def f():\n    return 1\n")
    _write(b, "mod.py", "def f():\n\treturn   1\n")
    # AST-level comparison should treat these as equivalent
    report = DriftDetector().compare_trees(a, b, "a", "b")
    assert report.semantic_changes == 0


def test_config_diff_counted(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    _write(a, "config.yml", "timeout: 30\n")
    _write(b, "config.yml", "timeout: 60\n")
    report = DriftDetector().compare_trees(a, b, "a", "b")
    assert report.config_changes >= 1
