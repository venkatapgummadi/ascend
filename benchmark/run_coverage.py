#!/usr/bin/env python3
"""Detection-coverage benchmark (Table II of the CARS paper).

Computes per-category and combined true-positive rate of single-tool vs.
multi-tool SAST on a LABELED benchmark (OWASP Benchmark), plus the marginal
contribution of each added tool. Inputs are public; nothing here depends on
private telemetry.

Pipeline:
  1) You run each scanner on the OWASP Benchmark sources and export SARIF, one
     file per tool, into --sarif-dir (e.g. sonarqube.sarif, semgrep.sarif,
     codeql.sarif). Example for Semgrep:
        semgrep --config p/owasp-top-ten --sarif -o sarif/semgrep.sarif <bench>
  2) This script joins SARIF findings (by file + CWE) against the benchmark's
     expectedresults CSV (true/false label + CWE per test case) and computes TP
     rates per category defined in benchmarks.yaml.

A "true positive" = a benchmark test case labeled vulnerable (real=true) whose
file is flagged by the tool with a CWE that maps to the same category.
"""
import argparse, csv, json, os, glob, itertools
from collections import defaultdict

import yaml


def load_config(path="benchmarks.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def load_expected(bench_dir, fname):
    """Return list of {test_name, file, cwe, real(bool)} from OWASP Benchmark."""
    p = os.path.join(bench_dir, fname)
    rows = []
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            # OWASP Benchmark columns: # test name, category, real, cwe, ...
            name = (r.get("# test name") or r.get("test name") or r.get("name") or "").strip()
            real = str(r.get(" real vulnerability") or r.get("real vulnerability")
                       or r.get("real") or "").strip().lower() in ("true", "1", "yes")
            try:
                cwe = int(str(r.get(" cwe") or r.get("cwe") or "0").strip())
            except ValueError:
                cwe = 0
            rows.append({"test": name, "cwe": cwe, "real": real})
    return rows


def cwe_to_category(category_map):
    inv = {}
    for cat, cwes in category_map.items():
        for c in cwes:
            inv[int(c)] = cat
    return inv


def load_sarif_hits(sarif_dir):
    """tool -> set of (basename_lower, cwe) flagged."""
    hits = {}
    for path in glob.glob(os.path.join(sarif_dir, "*.sarif")) + \
                glob.glob(os.path.join(sarif_dir, "*.json")):
        tool = os.path.splitext(os.path.basename(path))[0]
        flagged = set()
        try:
            doc = json.load(open(path))
        except Exception as e:
            print(f"! skip {path}: {e}")
            continue
        for run in doc.get("runs", []):
            # build ruleId -> cwe map from rule metadata when present
            rule_cwe = {}
            for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
                cwe = _extract_cwe(rule)
                if cwe:
                    rule_cwe[rule.get("id")] = cwe
            for res in run.get("results", []):
                cwe = _extract_cwe(res) or rule_cwe.get(res.get("ruleId"), 0)
                for loc in res.get("locations", []):
                    uri = (loc.get("physicalLocation", {})
                              .get("artifactLocation", {}).get("uri", ""))
                    if uri:
                        flagged.add((os.path.basename(uri).lower(), cwe))
        hits[tool] = flagged
    return hits


def _extract_cwe(obj):
    """Best-effort CWE extraction from SARIF tags/properties."""
    tags = (obj.get("properties", {}) or {}).get("tags", []) or []
    for t in tags:
        s = str(t).lower()
        if "cwe" in s:
            digits = "".join(ch for ch in s if ch.isdigit())
            if digits:
                return int(digits)
    # some tools put cwe in properties.cwe or security-severity
    props = obj.get("properties", {}) or {}
    if "cwe" in props:
        digits = "".join(ch for ch in str(props["cwe"]) if ch.isdigit())
        if digits:
            return int(digits)
    return 0


def tp_rate(expected, inv_cat, flagged_files_by_cat):
    """Per-category TP rate for one tool given the set of flagged categories
    keyed by test/file. We approximate test->file via the test name appearing
    in a flagged file (OWASP Benchmark test name == servlet file stem)."""
    total = defaultdict(int)      # real vulns per category
    found = defaultdict(int)
    for row in expected:
        if not row["real"]:
            continue
        cat = inv_cat.get(row["cwe"])
        if not cat:
            continue
        total[cat] += 1
        # a test is "found" if any flagged file basename contains the test stem
        stem = row["test"].lower()
        if any(stem in f for (f, c) in flagged_files_by_cat
               if inv_cat.get(c) == cat or c == 0):
            found[cat] += 1
    return {cat: (100.0 * found[cat] / total[cat] if total[cat] else 0.0,
                  found[cat], total[cat]) for cat in total}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="benchmarks.yaml")
    ap.add_argument("--benchmark", required=True, help="OWASP Benchmark dir")
    ap.add_argument("--sarif-dir", required=True, help="dir of <tool>.sarif files")
    ap.add_argument("--out", default="results/coverage.json")
    args = ap.parse_args()

    cfg = load_config(args.config)["sast_benchmark"]
    inv = cwe_to_category(cfg["category_map"])
    expected = load_expected(args.benchmark, cfg["expected_results"])
    hits = load_sarif_hits(args.sarif_dir)
    if not hits:
        raise SystemExit("No SARIF files found in --sarif-dir. Run scanners first.")

    per_tool = {tool: tp_rate(expected, inv, flagged) for tool, flagged in hits.items()}

    # Combined (union of all tools) and marginal value of adding tools in order
    tools = sorted(hits)
    union = set().union(*hits.values())
    combined = tp_rate(expected, inv, union)

    # marginal: greedily add tools, track overall TP rate
    marg = []
    acc = set()
    for t in tools:
        acc |= hits[t]
        overall = tp_rate(expected, inv, acc)
        cats = list(overall)
        ov = (sum(overall[c][1] for c in cats) /
              max(1, sum(overall[c][2] for c in cats)) * 100.0)
        marg.append({"after_adding": t, "overall_tp_pct": round(ov, 1)})

    out = {
        "benchmark": cfg["name"],
        "tools": tools,
        "per_tool": per_tool,
        "combined": combined,
        "marginal": marg,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(json.dumps(out, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
