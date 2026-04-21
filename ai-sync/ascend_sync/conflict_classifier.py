"""
Merge conflict classifier.

Categorizes a three-way merge conflict (ours, theirs, base) into one of:

  - SYNTACTIC:      formatting / renaming / cosmetic
  - SEMANTIC:       logic changes in overlapping code
  - STRUCTURAL:     architectural refactoring (file moves, class reorgs)
  - CONFIGURATION:  environment-specific parameters

Ships a baseline feature-based classifier. Production deployments should
retrain on organization-specific merge conflict history via `train.py`.
"""

from __future__ import annotations

import json
import logging
import pickle
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    CONFIGURATION = "configuration"


@dataclass
class Conflict:
    """A single merge conflict region."""

    file_path: str
    ours: str
    theirs: str
    base: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class Classification:
    conflict_type: ConflictType
    confidence: float
    features: dict = None

    def to_dict(self) -> dict:
        return {
            "conflict_type": self.conflict_type.value,
            "confidence": round(self.confidence, 4),
            "features": self.features or {},
        }


class ConflictClassifier:
    """
    Feature-based conflict classifier.

    The baseline implementation uses hand-engineered features; the trained
    sklearn model (when available at `model_path`) is loaded automatically.
    """

    # Feature extraction regex patterns
    _WHITESPACE_ONLY_DIFF = re.compile(r"^\s*$")
    _IMPORT_LINE = re.compile(r"^\s*(import|from)\s+\w+", re.MULTILINE)
    _CLASS_DEF = re.compile(r"^\s*class\s+\w+", re.MULTILINE)
    _FUNC_DEF = re.compile(r"^\s*(def|async\s+def)\s+\w+", re.MULTILINE)
    _CONFIG_KEYS = re.compile(
        r"^\s*[\w_-]+\s*[:=]\s*[\"']?\S", re.MULTILINE
    )
    _CONFIG_FILE_EXTENSIONS = (".yml", ".yaml", ".json", ".toml", ".ini", ".env", ".conf", ".properties", ".config")
    _CONFIG_BASENAME_TOKENS = ("dockerfile", ".env", "makefile", ".editorconfig")

    def __init__(self, model_path: Path | None = None, confidence_threshold: float = 0.85) -> None:
        self.confidence_threshold = confidence_threshold
        self._model = None
        if model_path and Path(model_path).exists():
            try:
                with open(model_path, "rb") as f:
                    self._model = pickle.load(f)
                logger.info("Loaded trained classifier from %s", model_path)
            except Exception as exc:
                logger.warning("Failed to load model from %s: %s. Falling back to heuristics.", model_path, exc)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def classify(self, conflict: Conflict) -> Classification:
        features = self._extract_features(conflict)
        if self._model is not None:
            try:
                return self._classify_with_model(features)
            except Exception as exc:
                logger.warning("Model classification failed, falling back to heuristics: %s", exc)
        return self._classify_heuristic(conflict, features)

    def classify_batch(self, conflicts: list[Conflict]) -> list[Classification]:
        return [self.classify(c) for c in conflicts]

    # -----------------------------------------------------------------------
    # Feature extraction
    # -----------------------------------------------------------------------

    def _extract_features(self, conflict: Conflict) -> dict:
        ours, theirs = conflict.ours, conflict.theirs
        path_lower = conflict.file_path.lower()
        is_config_file = (
            path_lower.endswith(self._CONFIG_FILE_EXTENSIONS)
            or any(tok in path_lower for tok in self._CONFIG_FILE_EXTENSIONS)
            or any(tok in path_lower for tok in self._CONFIG_BASENAME_TOKENS)
        )
        return {
            "is_config_file": is_config_file,
            "whitespace_only_diff": self._is_whitespace_only_diff(ours, theirs),
            "has_import_diff": self._has_import_difference(ours, theirs),
            "has_class_changes": self._has_class_definitions_diff(ours, theirs),
            "has_function_changes": self._has_function_definitions_diff(ours, theirs),
            "config_keys_diff": is_config_file and self._config_keys_diff(ours, theirs),
            "lines_ours": len(ours.splitlines()),
            "lines_theirs": len(theirs.splitlines()),
            "size_ratio": self._size_ratio(ours, theirs),
            "shared_token_ratio": self._shared_token_ratio(ours, theirs),
        }

    def _has_class_definitions_diff(self, a: str, b: str) -> bool:
        return set(self._CLASS_DEF.findall(a)) != set(self._CLASS_DEF.findall(b))

    def _has_function_definitions_diff(self, a: str, b: str) -> bool:
        return set(self._FUNC_DEF.findall(a)) != set(self._FUNC_DEF.findall(b))

    def _is_whitespace_only_diff(self, a: str, b: str) -> bool:
        return re.sub(r"\s+", "", a) == re.sub(r"\s+", "", b)

    def _has_import_difference(self, a: str, b: str) -> bool:
        return set(self._IMPORT_LINE.findall(a)) != set(self._IMPORT_LINE.findall(b))

    def _config_keys_diff(self, a: str, b: str) -> bool:
        a_keys = {m.group(0).split(":")[0].split("=")[0].strip() for m in self._CONFIG_KEYS.finditer(a)}
        b_keys = {m.group(0).split(":")[0].split("=")[0].strip() for m in self._CONFIG_KEYS.finditer(b)}
        return a_keys != b_keys

    def _size_ratio(self, a: str, b: str) -> float:
        la, lb = len(a), len(b)
        if max(la, lb) == 0:
            return 1.0
        return min(la, lb) / max(la, lb)

    def _shared_token_ratio(self, a: str, b: str) -> float:
        tokens_a = set(re.findall(r"\w+", a))
        tokens_b = set(re.findall(r"\w+", b))
        if not tokens_a and not tokens_b:
            return 1.0
        return len(tokens_a & tokens_b) / max(len(tokens_a | tokens_b), 1)

    # -----------------------------------------------------------------------
    # Heuristic fallback
    # -----------------------------------------------------------------------

    def _classify_heuristic(self, conflict: Conflict, features: dict) -> Classification:
        if features["whitespace_only_diff"]:
            return Classification(ConflictType.SYNTACTIC, 0.97, features)
        if features["is_config_file"] and features["config_keys_diff"]:
            return Classification(ConflictType.CONFIGURATION, 0.92, features)
        if features["has_import_diff"] and not features["has_function_changes"]:
            return Classification(ConflictType.SYNTACTIC, 0.82, features)
        if features["size_ratio"] < 0.5 and features["has_class_changes"]:
            return Classification(ConflictType.STRUCTURAL, 0.78, features)
        if features["has_class_changes"] and not features["has_function_changes"]:
            return Classification(ConflictType.STRUCTURAL, 0.65, features)
        if features["has_function_changes"] and features["shared_token_ratio"] > 0.4:
            return Classification(ConflictType.SEMANTIC, 0.80, features)
        return Classification(ConflictType.SEMANTIC, 0.60, features)

    # -----------------------------------------------------------------------
    # Model-backed classification
    # -----------------------------------------------------------------------

    def _classify_with_model(self, features: dict) -> Classification:
        import numpy as np

        feature_vector = np.array([
            int(features["is_config_file"]),
            int(features["whitespace_only_diff"]),
            int(features["has_import_diff"]),
            int(features["has_class_changes"]),
            int(features["has_function_changes"]),
            int(features["config_keys_diff"]),
            features["lines_ours"],
            features["lines_theirs"],
            features["size_ratio"],
            features["shared_token_ratio"],
        ]).reshape(1, -1)

        probs = self._model.predict_proba(feature_vector)[0]
        classes = list(self._model.classes_)
        best_idx = int(probs.argmax())
        best_label = classes[best_idx]
        try:
            conflict_type = ConflictType(best_label)
        except ValueError:
            logger.warning("Unknown label from model: %s, defaulting to SEMANTIC", best_label)
            conflict_type = ConflictType.SEMANTIC
        return Classification(
            conflict_type=conflict_type,
            confidence=float(probs[best_idx]),
            features=features,
        )


def load_conflicts_from_jsonl(path: Path) -> list[Conflict]:
    out: list[Conflict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            out.append(Conflict(
                file_path=rec.get("file_path", ""),
                ours=rec["ours"],
                theirs=rec["theirs"],
                base=rec.get("base", ""),
            ))
    return out
