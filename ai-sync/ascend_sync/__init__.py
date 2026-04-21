"""
ASCEND AI Synchronization Module.

Layer 4 of the ASCEND DevSecOps framework: post-deployment code
synchronization via AST-based drift detection, ML-assisted conflict
classification, and LLM-based conflict resolution.
"""

from ascend_sync.conflict_classifier import ConflictClassifier, ConflictType
from ascend_sync.drift_detector import DriftDetector, DriftReport
from ascend_sync.llm_resolver import LLMResolver, Resolution
from ascend_sync.pr_orchestrator import PROrchestrator
from ascend_sync.verifier import VerificationResult, Verifier

__version__ = "0.1.0"
__author__ = "Venkata Pavan Kumar Gummadi"
__email__ = "venkata.p.gummadi@ieee.org"

__all__ = [
    "ConflictClassifier",
    "ConflictType",
    "DriftDetector",
    "DriftReport",
    "LLMResolver",
    "PROrchestrator",
    "Resolution",
    "VerificationResult",
    "Verifier",
]
