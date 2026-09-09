#!/usr/bin/env python3
"""Unit tests for scripts/severity_gate.py. Stdlib only."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import severity_gate as gate  # noqa: E402


def _write(payload, suffix: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    json.dump(payload, handle)
    handle.close()
    return Path(handle.name)


class SarifTests(unittest.TestCase):
    def test_trivy_error_is_critical(self):
        path = _write(
            {
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "Trivy"}},
                        "results": [
                            {
                                "level": "error",
                                "message": {"text": "CVE-2024-0001"},
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "Dockerfile"},
                                            "region": {"startLine": 4},
                                        }
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            ".sarif",
        )
        findings = gate.parse_sarif(path)
        self.assertEqual(findings[0][0], gate.CRITICAL)
        self.assertIn("Dockerfile:4", findings[0][2])

    def test_cvss_score_mapping(self):
        path = _write(
            {
                "runs": [
                    {
                        "results": [
                            {"properties": {"security-severity": "9.8"}},
                            {"properties": {"security-severity": "7.5"}},
                            {"properties": {"security-severity": "4.0"}},
                        ]
                    }
                ]
            },
            ".sarif",
        )
        sevs = [s for s, _, _ in gate.parse_sarif(path)]
        self.assertEqual(sevs, [gate.CRITICAL, gate.HIGH, "note"])


class SemgrepBanditGitleaksTests(unittest.TestCase):
    def test_semgrep_error_is_critical(self):
        path = _write(
            {
                "results": [
                    {
                        "path": "app.py",
                        "start": {"line": 12},
                        "extra": {"severity": "ERROR"},
                    },
                    {
                        "path": "app.py",
                        "start": {"line": 40},
                        "extra": {"severity": "WARNING"},
                    },
                ]
            },
            ".json",
        )
        findings = gate.parse_semgrep(path)
        self.assertEqual([s for s, _, _ in findings], [gate.CRITICAL, gate.HIGH])

    def test_bandit_high_is_critical(self):
        path = _write(
            {
                "results": [
                    {
                        "filename": "crypto.py",
                        "line_number": 3,
                        "issue_severity": "HIGH",
                    }
                ]
            },
            ".json",
        )
        self.assertEqual(gate.parse_bandit(path)[0][0], gate.CRITICAL)

    def test_gitleaks_any_hit_is_critical(self):
        path = _write(
            [{"File": ".env", "StartLine": 2, "RuleID": "generic-api-key"}],
            ".json",
        )
        self.assertEqual(gate.parse_gitleaks(path)[0][0], gate.CRITICAL)

    def test_empty_gitleaks_passes(self):
        path = _write([], ".json")
        self.assertEqual(gate.parse_gitleaks(path), [])


class EvaluateAndCliTests(unittest.TestCase):
    def test_layer1_allows_five_high(self):
        findings = [(gate.HIGH, "semgrep", "a.py:%s" % i) for i in range(5)]
        _, violations = gate.evaluate(findings, critical_max=0, high_max=5)
        self.assertEqual(violations, [])

    def test_layer1_fails_sixth_high(self):
        findings = [(gate.HIGH, "semgrep", "a.py:%s" % i) for i in range(6)]
        _, violations = gate.evaluate(findings, critical_max=0, high_max=5)
        self.assertTrue(violations)

    def test_one_critical_fails(self):
        _, violations = gate.evaluate(
            [(gate.CRITICAL, "gitleaks", ".env:1")],
            critical_max=0,
            high_max=5,
        )
        self.assertTrue(violations)

    def test_cli_enforce_fails(self):
        path = _write(
            {"results": [{"path": "x.py", "start": {"line": 1}, "extra": {"severity": "ERROR"}}]},
            ".json",
        )
        rc = gate.main(["--layer", "1", "--mode", "enforce", "--semgrep", str(path)])
        self.assertEqual(rc, 1)

    def test_cli_warning_only_does_not_fail(self):
        path = _write(
            {"results": [{"path": "x.py", "start": {"line": 1}, "extra": {"severity": "ERROR"}}]},
            ".json",
        )
        rc = gate.main(["--layer", "1", "--mode", "warning-only", "--semgrep", str(path)])
        self.assertEqual(rc, 0)

    def test_cli_clean_report_passes(self):
        path = _write({"results": []}, ".json")
        rc = gate.main(["--layer", "1", "--semgrep", str(path)])
        self.assertEqual(rc, 0)

    def test_layer2_high_max_defaults_to_zero(self):
        path = _write(
            {
                "runs": [
                    {
                        "tool": {"driver": {"name": "Checkov"}},
                        "results": [{"level": "warning", "message": {"text": "CKV_AWS_1"}}],
                    }
                ]
            },
            ".sarif",
        )
        rc = gate.main(["--layer", "2", "--sarif", str(path)])
        self.assertEqual(rc, 1)

    def test_missing_report_fails_closed(self):
        rc = gate.main(["--layer", "1", "--semgrep", "no-such-semgrep.json"])
        self.assertEqual(rc, 1)

    def test_missing_report_can_skip(self):
        rc = gate.main(
            ["--layer", "1", "--missing", "skip", "--semgrep", "no-such-semgrep.json"]
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
