"""
Pull request orchestrator.

Given a verified resolution, opens a pull request on the configured source
control host (currently GitHub). Uses the REST API so it works with
self-hosted GitHub Enterprise as well.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ascend_sync.conflict_classifier import Conflict, ConflictType
from ascend_sync.llm_resolver import Resolution
from ascend_sync.verifier import VerificationResult

logger = logging.getLogger(__name__)


@dataclass
class PRResult:
    pr_url: str
    pr_number: int
    branch_name: str


class PROrchestrator:
    """
    Creates pull requests for AI-generated merge conflict resolutions.

    Parameters
    ----------
    github_token : str
        GitHub API token with `repo` scope.
    api_base : str
        API base URL. Defaults to public GitHub; set to your Enterprise URL
        for self-hosted deployments.
    default_labels : list[str]
        Labels to apply to created PRs.
    default_reviewers : list[str]
        GitHub usernames to request review from.
    """

    def __init__(
        self,
        github_token: str | None = None,
        api_base: str = "https://api.github.com",
        default_labels: list[str] | None = None,
        default_reviewers: list[str] | None = None,
    ) -> None:
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.api_base = api_base.rstrip("/")
        self.default_labels = default_labels or ["ai-sync", "automated"]
        self.default_reviewers = default_reviewers or []

        if not self.github_token:
            logger.warning("No GITHUB_TOKEN configured — PR creation will fail when called.")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_pr(
        self,
        repo: str,
        base_branch: str,
        head_branch: str,
        conflict: Conflict,
        resolution: Resolution,
        verification: VerificationResult,
        conflict_type: ConflictType,
        hotfix_sha: str | None = None,
    ) -> PRResult:
        """Open a PR with the resolved code."""
        title = self._build_title(conflict_type, hotfix_sha)
        body = self._build_body(conflict, resolution, verification, conflict_type, hotfix_sha)

        pr_data = self._create_pr_api(repo, title, body, head_branch, base_branch)
        pr_url = pr_data["html_url"]
        pr_number = pr_data["number"]

        self._apply_labels(repo, pr_number)
        self._request_reviewers(repo, pr_number)

        logger.info("Created PR #%d: %s", pr_number, pr_url)
        return PRResult(pr_url=pr_url, pr_number=pr_number, branch_name=head_branch)

    # -------------------------------------------------------------------------
    # GitHub API calls
    # -------------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def _create_pr_api(
        self, repo: str, title: str, body: str, head: str, base: str,
    ) -> dict[str, Any]:
        url = f"{self.api_base}/repos/{repo}/pulls"
        payload = {"title": title, "body": body, "head": head, "base": base}
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def _apply_labels(self, repo: str, pr_number: int) -> None:
        if not self.default_labels:
            return
        url = f"{self.api_base}/repos/{repo}/issues/{pr_number}/labels"
        resp = requests.post(url, headers=self._headers(),
                             json={"labels": self.default_labels}, timeout=30)
        if not resp.ok:
            logger.warning("Label application failed: %s", resp.text)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def _request_reviewers(self, repo: str, pr_number: int) -> None:
        if not self.default_reviewers:
            return
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_number}/requested_reviewers"
        resp = requests.post(url, headers=self._headers(),
                             json={"reviewers": self.default_reviewers}, timeout=30)
        if not resp.ok:
            logger.warning("Reviewer request failed: %s", resp.text)

    # -------------------------------------------------------------------------
    # PR body construction
    # -------------------------------------------------------------------------

    def _build_title(self, conflict_type: ConflictType, hotfix_sha: str | None) -> str:
        prefix = "[AI-Sync]"
        sha_str = f" ({hotfix_sha[:7]})" if hotfix_sha else ""
        return f"{prefix} Back-propagate {conflict_type.value} resolution{sha_str}"

    def _build_body(
        self,
        conflict: Conflict,
        resolution: Resolution,
        verification: VerificationResult,
        conflict_type: ConflictType,
        hotfix_sha: str | None,
    ) -> str:
        hotfix_section = f"- Hotfix SHA: `{hotfix_sha}`\n" if hotfix_sha else ""
        verification_section = (
            "## Verification\n"
            f"- Parses: **{verification.parse_ok}**\n"
            f"- Signatures preserved: **{verification.signatures_preserved}**\n"
            f"- Security patterns preserved: **{verification.security_patterns_preserved}**\n"
            f"- Property tests passed: **{verification.property_tests_passed}/{verification.property_tests_total}**\n"
        )
        failures = (
            "\n### Verification Failures\n" + "\n".join(f"- {r}" for r in verification.failure_reasons)
            if verification.failure_reasons else ""
        )
        return (
            f"## ASCEND AI Synchronization — Automated Merge Conflict Resolution\n\n"
            f"This pull request was generated by the ASCEND AI synchronization layer.\n\n"
            f"## Context\n"
            f"- File: `{conflict.file_path}`\n"
            f"- Conflict type: **{conflict_type.value}**\n"
            f"- Resolution provider: **{resolution.provider}** ({resolution.model})\n"
            f"- Resolution confidence: **{resolution.confidence:.2%}**\n"
            f"{hotfix_section}"
            f"\n{verification_section}"
            f"{failures}\n\n"
            f"## Action Required\n\n"
            f"AI sync proposes — humans dispose. Please review carefully before merging.\n\n"
            f"---\n"
            f"*Generated by [ASCEND](https://github.com/venkatapgummadi/ascend) AI Synchronization Module.*\n"
        )
