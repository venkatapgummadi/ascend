#!/usr/bin/env python3
"""Turn results/*.json into LaTeX rows for the CARS paper's %%<<FILL>> spots.

Usage:
  python gen_latex.py results/coverage.json results/sync.json results/overhead.json
Pass whichever files you have; each produces the matching block.
"""
import json, sys, os


def emit_coverage(c):
    print("% ---- Table II: detection coverage (paste over the xx rows) ----")
    cats = list(c["combined"].keys())
    tools = c["tools"]
    for cat in cats:
        cells = []
        for t in tools:
            v = c["per_tool"].get(t, {}).get(cat)
            cells.append(f"{v[0]:.0f}" if v else "--")
        comb = c["combined"][cat][0]
        print(f"{cat:<14}& " + " & ".join(cells) + f" & {comb:.0f}\\\\")
    # overall
    def overall(d):
        num = sum(d[k][1] for k in d); den = sum(d[k][2] for k in d)
        return 100.0 * num / den if den else 0.0
    per_tool_overall = []
    for t in tools:
        d = c["per_tool"].get(t, {})
        per_tool_overall.append(f"{overall(d):.0f}" if d else "--")
    print(r"\midrule")
    print(f"Overall       & " + " & ".join(per_tool_overall) +
          f" & {overall(c['combined']):.0f}\\\\")
    print("\n% Complementarity sentence:")
    best = max((overall(c['per_tool'][t]), t) for t in tools)
    print(f"%  combined {overall(c['combined']):.0f}%, best single "
          f"{best[0]:.0f}% ({best[1]}); marginal: " +
          ", ".join(f"{m['after_adding']}->{m['overall_tp_pct']}%" for m in c["marginal"]))


def emit_sync(s):
    print("\n% ---- Synchronization paragraph ----")
    lo, hi = s["accept_rate_95ci"]
    print(f"% auto-resolve rate r = {s['auto_resolve_rate_pct']}% "
          f"({s['auto_resolved']}/{s['total_conflicts']}); "
          f"conditional accept-rate a = {s['conditional_accept_rate_pct']}% "
          f"(95\\% CI [{lo}, {hi}]).")
    bits = [f"{t} {v['accept_pct']:.0f}\\% (n={v['n']})" for t, v in s["by_type"].items()]
    print("% by type: " + "; ".join(bits))
    print("% NOTE: a% is conditional on auto-resolution; not a general accuracy figure.")


def emit_overhead(o):
    print("\n% ---- Overhead ----")
    for layer, d in o["per_layer"].items():
        print(f"% {layer}: median {d['median_min']} min, P95 {d['p95_min']} min"
              + (f"  (skipped: {', '.join(d['skipped_tools'])})" if d['skipped_tools'] else ""))
    if o.get("cumulative_median_min"):
        print("% cumulative median (min): " + ", ".join(
            f"{k}={v}" for k, v in o["cumulative_median_min"].items()))


def main():
    for path in sys.argv[1:]:
        if not os.path.exists(path):
            print(f"% (missing {path})"); continue
        d = json.load(open(path))
        name = os.path.basename(path)
        if "coverage" in name:
            emit_coverage(d)
        elif "sync" in name:
            emit_sync(d)
        elif "overhead" in name:
            emit_overhead(d)


if __name__ == "__main__":
    main()
