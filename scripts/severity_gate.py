#!/usr/bin/env python3
"""ASCEND severity veto.

Fail a CI job when scanner findings exceed the Layer 1 / Layer 2 policy.
Stdlib only so Bamboo, Jenkins, and other agents do not need extra packages.

Supported inputs
----------------
* SARIF 2.1.0 (Trivy, Checkov, Snyk, CodeQL, Semgrep --sarif)
* Semgrep JSON (``--json``)
* Bandit JSON (``-f json``)
* Gitleaks JSON (``-f json``)

Usage
-----
    python3 scripts/severity_gate.py --layer 1 \\
        --semgrep semgrep-report.json \\
        --bandit bandit-report.json \\
        --gitleaks gitleaks-report.json

    python3 scripts/severity_gate.py --layer 2 \\
        --sarif trivy.sarif checkov.sarif

    python3 scripts/severity_gate.py --layer 1 --mode warning-only \\
        --semgrep semgrep-report.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

CRITICAL = "critical"
HIGH = "high"
ERROR = "error"  # Semgrep ERROR-level (treated as critical for QG1)

Finding = Tuple[str, str, str]  # severity, tool, location


def _load_json(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return json.loads(text)


def parse_sarif(path: Path) -> List[Finding]:
    data = _load_json(path)
    if not data:
        return []
    findings: List[Finding] = []
    tool_name = path.stem
    for run in data.get("runs") or []:
        driver = ((run.get("tool") or {}).get("driver") or {}).get("name") or tool_name
        for result in run.get("results") or []:
            sev = _sarif_severity(result)
            loc = _first_location(result) or str(path)
            findings.append((sev, str(driver), loc))
    return findings


def _sarif_severity(result: dict) -> str:
    props = result.get("properties") or {}
    raw = str(
        props.get("severity")
        or props.get("security-severity")
        or result.get("level")
        or "warning"
    ).strip().lower()
    if raw in ("critical", "error", "fail", "failed"):
        return CRITICAL
    try:
        score = float(raw)
        if score >= 9.0:
            return CRITICAL
        if score >= 7.0:
            return HIGH
        return "note"
    except ValueError:
        pass
    if raw in ("high", "warning"):
        return HIGH
    if raw in ("medium", "note", "low", "info", "none"):
        return HIGH if raw == "medium" else "note"
    return HIGH


def _first_location(result: dict) -> str:
    for loc in result.get("locations") or []:
        phys = (loc.get("physicalLocation") or {}).get("artifactLocation") or {}
        uri = phys.get("uri")
        region = (loc.get("physicalLocation") or {}).get("region") or {}
        line = region.get("startLine")
        if uri and line:
            return f"{uri}:{line}"
        if uri:
            return str(uri)
    msg = (result.get("message") or {}).get("text")
    return (msg or "")[:120]


def parse_semgrep(path: Path) -> List[Finding]:
    data = _load_json(path)
    if not data:
        return []
    findings: List[Finding] = []
    for item in data.get("results") or []:
        extra = item.get("extra") or {}
        sev = str(extra.get("severity") or "WARNING").upper()
        mapped = CRITICAL if sev in ("ERROR", "CRITICAL") else HIGH if sev in ("WARNING", "HIGH") else "note"
        loc = f"{item.get('path', path.name)}:{item.get('start', {}).get('line', '?')}"
        findings.append((mapped, "semgrep", loc))
    return findings


def parse_bandit(path: Path) -> List[Finding]:
    data = _load_json(path)
    if not data:
        return []
    findings: List[Finding] = []
    for item in data.get("results") or []:
        sev = str(item.get("issue_severity") or "MEDIUM").upper()
        mapped = CRITICAL if sev == "HIGH" else HIGH if sev == "MEDIUM" else "note"
        loc = f"{item.get('filename', path.name)}:{item.get('line_number', '?')}"
        findings.append((mapped, "bandit", loc))
    return findings


def parse_gitleaks(path: Path) -> List[Finding]:
    data = _load_json(path)
    if data is None:
        return []
    items = data if isinstance(data, list) else data.get("leaks") or data.get("findings") or []
    findings: List[Finding] = []
    for item in items:
        file_name = item.get("File") or item.get("file") or path.name
        line = item.get("StartLine") or item.get("line") or "?"
        findings.append((CRITICAL, "gitleaks", f"{file_name}:{line}"))
    return findings


PARSERS = {
    "sarif": parse_sarif,
    "semgrep": parse_semgrep,
    "bandit": parse_bandit,
    "gitleaks": parse_gitleaks,
}


def collect(kind: str, paths: Sequence[str], missing: str) -> List[Finding]:
    out: List[Finding] = []
    parser = PARSERS[kind]
    for raw in paths:
        path = Path(raw)
        if not path.is_file():
            if missing == "fail":
                raise FileNotFoundError(f"scanner report not found: {path}")
            print(f"[skip] {kind} report missing: {path}", file=sys.stderr)
            continue
        out.extend(parser(path))
    return out


def evaluate(
    findings: Iterable[Finding],
    *,
    critical_max: int,
    high_max: int,
) -> Tuple[Counter, List[str]]:
    counts: Counter = Counter()
    violations: List[str] = []
    for sev, tool, loc in findings:
        counts[sev] += 1
        counts[f"{tool}:{sev}"] += 1
    critical_n = counts[CRITICAL]
    high_n = counts[HIGH]
    if critical_n > critical_max:
        violations.append(
            f"critical findings {critical_n} exceed maximum {critical_max}"
        )
    if high_n > high_max:
        violations.append(f"high findings {high_n} exceed maximum {high_max}")
    return counts, violations


def default_thresholds(layer: int) -> Tuple[int, int]:
    """Layer 1 allows a small HIGH budget; Layer 2 does not."""
    if layer == 1:
        return int(os.environ.get("ASCEND_CRITICAL_THRESHOLD", "0")), int(
            os.environ.get("ASCEND_HIGH_THRESHOLD", "5")
        )
    return int(os.environ.get("ASCEND_CRITICAL_THRESHOLD", "0")), 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ASCEND Layer 1 / Layer 2 severity veto")
    p.add_argument("--layer", type=int, choices=(1, 2), required=True)
    p.add_argument(
        "--mode",
        choices=("enforce", "warning-only"),
        default=os.environ.get("ASCEND_MODE", "enforce"),
    )
    p.add_argument("--critical-max", type=int)
    p.add_argument("--high-max", type=int)
    p.add_argument("--sarif", nargs="*", default=[])
    p.add_argument("--semgrep", nargs="*", default=[])
    p.add_argument("--bandit", nargs="*", default=[])
    p.add_argument("--gitleaks", nargs="*", default=[])
    p.add_argument(
        "--missing",
        choices=("skip", "fail"),
        default="fail",
        help="what to do when a report path does not exist",
    )
    p.add_argument("--summary-json", type=Path)
    return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    crit_default, high_default = default_thresholds(args.layer)
    critical_max = args.critical_max if args.critical_max is not None else crit_default
    high_max = args.high_max if args.high_max is not None else high_default

    findings: List[Finding] = []
    try:
        findings.extend(collect("sarif", args.sarif, args.missing))
        findings.extend(collect("semgrep", args.semgrep, args.missing))
        findings.extend(collect("bandit", args.bandit, args.missing))
        findings.extend(collect("gitleaks", args.gitleaks, args.missing))
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not (
        args.sarif or args.semgrep or args.bandit or args.gitleaks
    ):
        print("error: provide at least one --sarif/--semgrep/--bandit/--gitleaks path", file=sys.stderr)
        return 2

    counts, violations = evaluate(
        findings, critical_max=critical_max, high_max=high_max
    )
    summary = {
        "layer": args.layer,
        "mode": args.mode,
        "critical": counts[CRITICAL],
        "high": counts[HIGH],
        "critical_max": critical_max,
        "high_max": high_max,
        "violations": violations,
        "by_tool": {k: v for k, v in sorted(counts.items()) if ":" in k},
    }
    print(
        f"QG{args.layer} {args.mode}: critical={counts[CRITICAL]}/{critical_max} "
        f"high={counts[HIGH]}/{high_max} findings={len(findings)}"
    )
    if args.summary_json:
        args.summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if not violations:
        print(f"PASS: Quality Gate {args.layer}")
        return 0

    for item in violations:
        print(f"FAIL: {item}", file=sys.stderr)
    if args.mode == "warning-only":
        print(f"WARNING-ONLY: Quality Gate {args.layer} would fail in enforce mode")
        return 0
    print(f"FAIL: Quality Gate {args.layer}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
