"""Tests for ConflictClassifier heuristics."""

from ascend_sync.conflict_classifier import Conflict, ConflictClassifier, ConflictType


def test_whitespace_only_diff_is_syntactic():
    conflict = Conflict(
        file_path="foo.py",
        ours="def f():\n    return 1",
        theirs="def f():\n  return 1",
    )
    result = ConflictClassifier().classify(conflict)
    assert result.conflict_type == ConflictType.SYNTACTIC
    assert result.confidence > 0.9


def test_config_file_key_diff_is_configuration():
    conflict = Conflict(
        file_path="config.yml",
        ours="timeout: 30\nretries: 3\n",
        theirs="timeout: 30\nretries: 5\nbackoff: 2\n",
    )
    result = ConflictClassifier().classify(conflict)
    assert result.conflict_type == ConflictType.CONFIGURATION


def test_function_changes_with_shared_tokens_is_semantic():
    conflict = Conflict(
        file_path="auth.py",
        ours="def authenticate(token):\n    return token is not None",
        theirs="def authenticate(token):\n    return validate_token(token)",
    )
    result = ConflictClassifier().classify(conflict)
    assert result.conflict_type == ConflictType.SEMANTIC


def test_import_only_diff_is_syntactic():
    conflict = Conflict(
        file_path="mod.py",
        ours="import os\nimport sys\n",
        theirs="import os\nimport sys\nimport logging\n",
    )
    result = ConflictClassifier().classify(conflict)
    assert result.conflict_type == ConflictType.SYNTACTIC


def test_batch_classify():
    conflicts = [
        Conflict(file_path="a.py", ours="x = 1", theirs="x = 2"),
        Conflict(file_path="b.yml", ours="a: 1", theirs="a: 2"),
    ]
    results = ConflictClassifier().classify_batch(conflicts)
    assert len(results) == 2
    assert all(isinstance(r.conflict_type, ConflictType) for r in results)
