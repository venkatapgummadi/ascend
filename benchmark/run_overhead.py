#!/usr/bin/env python3
"""Scanning-overhead benchmark (Overhead paragraph of the CARS paper).

Times each scanning LAYER on a sample app and reports median and P95 over
--runs repetitions. Only tools that are installed and configured are timed;
missing tools are skipped and reported as such (honest: no invented numbers).

Layers (edit COMMANDS to match what you actually run):
  L1  SAST + SCA + secrets
  L2  + container + IaC
  L3  + DAST (requires a deployed staging target; off by default)
"""
import argparse, json, os, shutil, statistics, subprocess, time

# Per-tool command templates. {app} is substituted with the target dir.
# Comment out tools you do not run. Each must exit without erroring on a clean app.
LAYER_COMMANDS = {
    "L1": [
        ("semgrep",  ["semgrep", "--config", "p/owasp-top-ten", "--error", "--quiet", "{app}"]),
        ("bandit",   ["bandit", "-r", "{app}", "-q"]),
        ("gitleaks", ["gitleaks", "detect", "--source", "{app}", "--no-banner"]),
    ],
    "L2": [
        ("trivy",   ["trivy", "fs", "--quiet", "{app}"]),
        ("checkov", ["checkov", "-d", "{app}", "--compact", "--quiet"]),
    ],
    # "L3": [("zap-baseline", ["zap-baseline.py", "-t", "{target_url}"])],  # needs staging
}


def have(cmd0):
    return shutil.which(cmd0) is not None


def time_cmd(argv):
    t0 = time.perf_counter()
    try:
        subprocess.run(argv, capture_output=True, timeout=1800)
    except Exception as e:
        print(f"  ! {argv[0]} failed: {e}")
        return None
    return (time.perf_counter() - t0) / 60.0  # minutes


def p95(xs):
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, int(round(0.95 * (len(xs) - 1))))
    return xs[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True, help="path to sample app dir")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--out", default="results/overhead.json")
    args = ap.parse_args()

    results = {}
    for layer, tools in LAYER_COMMANDS.items():
        per_run_totals = []
        skipped = []
        for _ in range(args.runs):
            total = 0.0
            ran_any = False
            for name, tmpl in tools:
                if not have(tmpl[0]):
                    if name not in skipped:
                        skipped.append(name)
                    continue
                argv = [a.replace("{app}", args.app) for a in tmpl]
                dt = time_cmd(argv)
                if dt is not None:
                    total += dt
                    ran_any = True
            if ran_any:
                per_run_totals.append(total)
        results[layer] = {
            "runs": len(per_run_totals),
            "median_min": round(statistics.median(per_run_totals), 2) if per_run_totals else None,
            "p95_min": round(p95(per_run_totals), 2) if per_run_totals else None,
            "skipped_tools": skipped,
        }

    # cumulative layers (L1, L1-2, ...) for the paper's overhead table
    cumulative = {}
    running = 0.0
    for layer in LAYER_COMMANDS:
        m = results[layer]["median_min"]
        if m is not None:
            running += m
            cumulative[layer] = round(running, 2)

    out = {"app": args.app, "runs": args.runs,
           "per_layer": results, "cumulative_median_min": cumulative}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(json.dumps(out, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
