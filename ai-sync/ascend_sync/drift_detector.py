"""
AST-based drift detection.

Compares code states across deployment tracks using:
  1. Python AST differencing (semantic changes only — ignores whitespace/comments)
  2. Configuration file fingerprinting
  3. Code embedding distance (when an embedding provider is configured)

Produces a risk score r in [0, 1]; values above the configured threshold
trigger the synchronization workflow.
"""

from __future__ import annotations

import ast
import hashlib
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """Result of a drift detection run between two branches/commits."""

    source_ref: str
    target_ref: str
    risk_score: float
    semantic_changes: int
    config_changes: int
    embedding_distance: float
    affected_files: list[str] = field(default_factory=list)
    threshold_exceeded: bool = False
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "risk_score": round(self.risk_score, 4),
            "semantic_changes": self.semantic_changes,
            "config_changes": self.config_changes,
            "embedding_distance": round(self.embedding_distance, 4),
            "affected_files": self.affected_files,
            "threshold_exceeded": self.threshold_exceeded,
            "explanation": self.explanation,
        }


class DriftDetector:
    """
    Detects semantic drift between two code states.

    Parameters
    ----------
    threshold : float
        Risk score above which drift is reported. Default 0.30.
    weight_semantic, weight_config, weight_embedding : float
        Weights for combining the three signal components into a risk score.
    """

    def __init__(
        self,
        threshold: float = 0.30,
        weight_semantic: float = 0.50,
        weight_config: float = 0.25,
        weight_embedding: float = 0.25,
    ) -> None:
        self.threshold = threshold
        self.w_sem = weight_semantic
        self.w_cfg = weight_config
        self.w_emb = weight_embedding

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def compare_trees(
        self,
        source_root: Path,
        target_root: Path,
        source_ref: str = "source",
        target_ref: str = "target",
    ) -> DriftReport:
        """Compare two filesystem trees and produce a drift report."""
        source_files = self._collect_python_files(source_root)
        target_files = self._collect_python_files(target_root)

        semantic_changes = 0
        affected: list[str] = []

        for rel_path in sorted(set(source_files) | set(target_files)):
            src = source_files.get(rel_path)
            tgt = target_files.get(rel_path)
            if src is None or tgt is None:
                # one side missing the file — count as change
                semantic_changes += 1
                affected.append(rel_path)
                continue
            diff_count = self._semantic_diff(src, tgt)
            if diff_count > 0:
                semantic_changes += diff_count
                affected.append(rel_path)

        config_changes = self._config_diff(source_root, target_root)
        embedding_distance = self._embedding_distance(source_root, target_root)

        # Normalize each component to [0, 1] via bounded scaling
        sem_norm = min(1.0, semantic_changes / 20.0)
        cfg_norm = min(1.0, config_changes / 10.0)
        emb_norm = min(1.0, embedding_distance)

        risk = self.w_sem * sem_norm + self.w_cfg * cfg_norm + self.w_emb * emb_norm
        risk = max(0.0, min(1.0, risk))

        exceeded = risk > self.threshold
        explanation = self._build_explanation(sem_norm, cfg_norm, emb_norm, risk)

        logger.info(
            "drift: source=%s target=%s risk=%.3f sem=%d cfg=%d emb=%.3f",
            source_ref, target_ref, risk, semantic_changes, config_changes, embedding_distance,
        )

        return DriftReport(
            source_ref=source_ref,
            target_ref=target_ref,
            risk_score=risk,
            semantic_changes=semantic_changes,
            config_changes=config_changes,
            embedding_distance=embedding_distance,
            affected_files=affected,
            threshold_exceeded=exceeded,
            explanation=explanation,
        )

    # -------------------------------------------------------------------------
    # File collection
    # -------------------------------------------------------------------------

    def _collect_python_files(self, root: Path) -> dict[str, Path]:
        out: dict[str, Path] = {}
        for p in root.rglob("*.py"):
            rel = str(p.relative_to(root))
            out[rel] = p
        return out

    # -------------------------------------------------------------------------
    # Semantic AST diff (Python)
    # -------------------------------------------------------------------------

    def _semantic_diff(self, left: Path, right: Path) -> int:
        """Return a count of semantic differences between two Python files."""
        try:
            left_tree = ast.parse(left.read_text(encoding="utf-8", errors="replace"))
            right_tree = ast.parse(right.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            # Fallback to line count diff if either file is unparseable
            return self._line_diff(left, right)

        left_sig = self._ast_signature(left_tree)
        right_sig = self._ast_signature(right_tree)

        # Simple difference count — could be extended to a proper tree edit distance
        return sum(1 for k in set(left_sig) | set(right_sig) if left_sig.get(k) != right_sig.get(k))

    def _ast_signature(self, tree: ast.AST) -> dict[str, str]:
        """Build a name -> hash signature for each function/class."""
        sig: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                try:
                    src = ast.unparse(node)
                except Exception:
                    src = repr(ast.dump(node))
                sig[node.name] = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
        return sig

    def _line_diff(self, left: Path, right: Path) -> int:
        """Approximate line-level diff count as a fallback."""
        a = left.read_text(encoding="utf-8", errors="replace").splitlines()
        b = right.read_text(encoding="utf-8", errors="replace").splitlines()
        return abs(len(a) - len(b)) + sum(1 for x, y in zip(a, b) if x != y)

    # -------------------------------------------------------------------------
    # Configuration diff
    # -------------------------------------------------------------------------

    _CONFIG_EXTENSIONS = {".yml", ".yaml", ".json", ".toml", ".ini", ".env"}

    def _config_diff(self, source_root: Path, target_root: Path) -> int:
        """Count differing configuration files (shallow — hash-based)."""
        changes = 0
        for ext in self._CONFIG_EXTENSIONS:
            for src_path in source_root.rglob(f"*{ext}"):
                rel = src_path.relative_to(source_root)
                tgt_path = target_root / rel
                if not tgt_path.exists():
                    changes += 1
                    continue
                if self._file_hash(src_path) != self._file_hash(tgt_path):
                    changes += 1
        return changes

    def _file_hash(self, path: Path) -> str:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    # -------------------------------------------------------------------------
    # Embedding distance (optional; stubbed for offline use)
    # -------------------------------------------------------------------------

    def _embedding_distance(self, source_root: Path, target_root: Path) -> float:
        """
        Placeholder implementation. Production deployments should replace this
        with a real code embedding model (e.g., CodeBERT, GraphCodeBERT, Voyage).
        """
        # Lightweight proxy: sha-based content distance
        src_hashes = self._tree_hash_set(source_root)
        tgt_hashes = self._tree_hash_set(target_root)
        if not src_hashes and not tgt_hashes:
            return 0.0
        union = src_hashes | tgt_hashes
        if not union:
            return 0.0
        sym_diff = src_hashes.symmetric_difference(tgt_hashes)
        return len(sym_diff) / len(union)

    def _tree_hash_set(self, root: Path) -> set[str]:
        out: set[str] = set()
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in {".py", ".js", ".ts", ".go", ".java"}:
                out.add(self._file_hash(p))
        return out

    # -------------------------------------------------------------------------
    # Explanation
    # -------------------------------------------------------------------------

    def _build_explanation(
        self, sem: float, cfg: float, emb: float, total: float,
    ) -> str:
        parts: list[str] = []
        if total > self.threshold:
            parts.append(f"Risk {total:.2f} > threshold {self.threshold:.2f}. ")
        else:
            parts.append(f"Risk {total:.2f} <= threshold {self.threshold:.2f}. ")
        parts.append(f"Components: semantic={sem:.2f}, config={cfg:.2f}, embedding={emb:.2f}.")
        return "".join(parts)


def iter_reports(
    detector: DriftDetector,
    branches: Iterable[tuple[Path, str]],
) -> Iterable[DriftReport]:
    """Pairwise drift comparison across a set of (path, ref) tuples."""
    seq = list(branches)
    for i, (src_path, src_ref) in enumerate(seq):
        for tgt_path, tgt_ref in seq[i + 1 :]:
            yield detector.compare_trees(src_path, tgt_path, src_ref, tgt_ref)
