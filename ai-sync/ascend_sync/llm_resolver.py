"""
LLM-based merge conflict resolver.

Produces candidate resolutions conditioned on (c_ours, c_theirs, c_base, H),
where H is historical context. Supports multiple providers (OpenAI, Anthropic,
or a local stub for offline testing).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Literal

from tenacity import retry, stop_after_attempt, wait_exponential

from ascend_sync.conflict_classifier import Conflict, ConflictType

logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "local"]


@dataclass
class Resolution:
    """A candidate conflict resolution with associated metadata."""

    resolved_code: str
    provider: str
    model: str
    confidence: float
    reasoning: str = ""
    preserves_invariants: list[str] | None = None

    def to_dict(self) -> dict:
        return {
            "resolved_code": self.resolved_code,
            "provider": self.provider,
            "model": self.model,
            "confidence": round(self.confidence, 4),
            "reasoning": self.reasoning,
            "preserves_invariants": self.preserves_invariants or [],
        }


class LLMResolver:
    """
    LLM-backed resolver that generates candidate resolutions.

    Parameters
    ----------
    provider : "openai" | "anthropic" | "local"
        Which backend to use.
    model : str
        Model name (e.g., "gpt-4o-mini", "claude-opus-4-6").
    max_candidates : int
        How many candidate resolutions to generate per conflict.
    temperature : float
        Sampling temperature.
    """

    def __init__(
        self,
        provider: Provider = "local",
        model: str = "stub-model",
        max_candidates: int = 3,
        temperature: float = 0.2,
    ) -> None:
        self.provider = provider
        self.model = model
        self.max_candidates = max_candidates
        self.temperature = temperature
        self._client = self._init_client()

    # -------------------------------------------------------------------------
    # Client initialization
    # -------------------------------------------------------------------------

    def _init_client(self):
        if self.provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except ImportError as exc:
                raise RuntimeError("openai extra not installed. Run: pip install 'ascend-sync[openai]'") from exc
            return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        if self.provider == "anthropic":
            try:
                import anthropic  # type: ignore
            except ImportError as exc:
                raise RuntimeError("anthropic extra not installed. Run: pip install 'ascend-sync[anthropic]'") from exc
            return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        if self.provider == "local":
            return None
        raise ValueError(f"Unknown provider: {self.provider}")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def resolve(
        self,
        conflict: Conflict,
        conflict_type: ConflictType,
        historical_context: str = "",
    ) -> list[Resolution]:
        """Produce up to `max_candidates` resolution candidates."""
        prompt = self._build_prompt(conflict, conflict_type, historical_context)

        if self.provider == "local":
            return [self._local_stub_resolution(conflict, conflict_type)]

        candidates: list[Resolution] = []
        for i in range(self.max_candidates):
            try:
                candidate = self._call_llm(prompt, variant_index=i)
                candidates.append(candidate)
            except Exception as exc:
                logger.warning("LLM call %d failed: %s", i, exc)

        return candidates

    # -------------------------------------------------------------------------
    # Prompt construction
    # -------------------------------------------------------------------------

    _SYSTEM_PROMPT = """You are an expert software engineer assisting with merge conflict resolution.
Your job is to produce a single valid code resolution for a three-way merge conflict.

Rules:
1. Preserve all security-relevant invariants from both branches.
2. If either branch contains a security fix (CVE-related, authentication, authorization,
   input validation, or cryptographic code), that fix MUST be preserved.
3. Prefer additive composition over choosing one side arbitrarily.
4. Output ONLY the resolved code block — no explanation, no markdown fences.
5. If resolution is impossible without human judgment, output exactly: `CANNOT_RESOLVE`
"""

    _USER_PROMPT_TEMPLATE = """Conflict file: {file_path}
Conflict type: {conflict_type}

=== BASE (common ancestor) ===
{base}

=== OURS ===
{ours}

=== THEIRS ===
{theirs}

=== HISTORICAL CONTEXT ===
{historical_context}

Produce the resolved code that preserves invariants from both OURS and THEIRS."""

    def _build_prompt(
        self,
        conflict: Conflict,
        conflict_type: ConflictType,
        historical_context: str,
    ) -> str:
        return self._USER_PROMPT_TEMPLATE.format(
            file_path=conflict.file_path,
            conflict_type=conflict_type.value,
            base=conflict.base or "(no base available)",
            ours=conflict.ours,
            theirs=conflict.theirs,
            historical_context=historical_context or "(none)",
        )

    # -------------------------------------------------------------------------
    # LLM calls
    # -------------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_llm(self, prompt: str, variant_index: int = 0) -> Resolution:
        if self.provider == "openai":
            return self._call_openai(prompt, variant_index)
        if self.provider == "anthropic":
            return self._call_anthropic(prompt, variant_index)
        raise RuntimeError(f"_call_llm invoked with provider={self.provider}")

    def _call_openai(self, prompt: str, variant_index: int) -> Resolution:
        response = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature + 0.1 * variant_index,
            messages=[
                {"role": "system", "content": self._SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        code = response.choices[0].message.content.strip()
        confidence = self._estimate_confidence(code)
        return Resolution(
            resolved_code=code,
            provider=self.provider,
            model=self.model,
            confidence=confidence,
        )

    def _call_anthropic(self, prompt: str, variant_index: int) -> Resolution:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=self.temperature + 0.1 * variant_index,
            system=self._SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        code = response.content[0].text.strip()
        confidence = self._estimate_confidence(code)
        return Resolution(
            resolved_code=code,
            provider=self.provider,
            model=self.model,
            confidence=confidence,
        )

    # -------------------------------------------------------------------------
    # Offline stub
    # -------------------------------------------------------------------------

    def _local_stub_resolution(self, conflict: Conflict, conflict_type: ConflictType) -> Resolution:
        """
        Offline deterministic fallback. Produces the union of both sides
        as a conservative placeholder. Real deployments should use a real LLM.
        """
        resolved = "\n".join([
            "# [ASCEND AI-Sync — LOCAL STUB] Merge both sides.",
            "# Production deployment should use provider='openai' or 'anthropic'.",
            conflict.ours.rstrip(),
            conflict.theirs.rstrip(),
        ])
        return Resolution(
            resolved_code=resolved,
            provider="local",
            model="stub-model",
            confidence=0.50,
            reasoning="Local stub produces union of both sides.",
        )

    def _estimate_confidence(self, code: str) -> float:
        """Very rough heuristic — real confidence comes from verifier downstream."""
        if not code or code.strip() == "CANNOT_RESOLVE":
            return 0.0
        length_score = min(1.0, len(code) / 500)
        return max(0.5, 0.7 + 0.3 * length_score)
