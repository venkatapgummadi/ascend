#!/usr/bin/env python3
"""Synchronization benchmark (Section V of the CARS paper).

Reports, on PUBLIC inputs only:
  * auto-resolve rate r%  = fraction of conflicts the system chose to auto-resolve
                            (resolver confidence >= tau)
  * conditional accept-rate a% = among AUTO-RESOLVED conflicts, fraction whose
                            proposed resolution matches the ground-truth
                            resolution under an AST-equivalence rule
  * 95% bootstrap CI on a%
  * breakdown by conflict type

IMPORTANT: a% is CONDITIONAL on auto-resolution. We do NOT claim accuracy on the
escalated subset. This is stated in the paper and must stay stated.

Resolver plug-in:
  By default we try to import the repo's resolver (`ascend_sync`). If it is not
  importable, a transparent heuristic stub is used so the harness still runs end
  to end; replace it with the real resolver before reporting numbers.

Fixture schema (tolerant): each *.json fixture should provide the three sides and
the ground-truth resolution. Recognized keys (first match wins):
  base:     base | ancestor | o_base
  ours:     ours | a | left
  theirs:   theirs | b | right
  expected: expected | resolution | merged | truth
  type:     type | conflict_type   (optional; else inferred)
  lang:     lang | language        (optional; default 'py')
"""
import argparse, ast, glob, json, os, random, statistics
from collections import defaultdict

# ---------------- resolver plug-in ----------------
def get_resolver():
    """Return callable(base, ours, theirs, lang) -> (resolution_str, confidence)."""
    try:
        from ascend_sync.resolver import resolve  # type: ignore
        def _r(base, ours, theirs, lang):
            out = resolve(base=base, ours=ours, theirs=theirs, language=lang)
            return out["resolution"], float(out.get("confidence", 0.0))
        print("[resolver] using ascend_sync.resolver.resolve")
        return _r
    except Exception as e:
        print(f"[resolver] ascend_sync not importable ({e}); using heuristic stub")
        return _heuristic_resolver


def _heuristic_resolver(base, ours, theirs, lang):
    """Transparent baseline: if one side only adds lines on top of base, take it;
    else if both equal, take either; else low confidence. NOT a research model —
    replace with the real resolver before reporting."""
    if ours == theirs:
        return ours, 0.99
    if base and theirs.startswith(base) and not ours.startswith(base):
        return theirs, 0.86
    if base and ours.startswith(base) and not theirs.startswith(base):
        return ours, 0.86
    # union merge as last resort, low confidence
    return ours + "\n" + theirs, 0.40


# ---------------- acceptance test ----------------
def normalize(code):
    return "\n".join(l.rstrip() for l in code.strip().splitlines() if l.strip())


def ast_equivalent(a, b, lang):
    """True if a and b are equivalent. For Python, compare AST dumps (ignores
    formatting/comments). For other languages, fall back to normalized text."""
    if lang in ("py", "python"):
        try:
            return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
        except SyntaxError:
            return normalize(a) == normalize(b)
    return normalize(a) == normalize(b)


# ---------------- fixtures ----------------
def _pick(d, *keys, default=""):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def load_fixtures(fixtures_dir):
    items = []
    for p in sorted(glob.glob(os.path.join(fixtures_dir, "**", "*.json"), recursive=True)):
        try:
            d = json.load(open(p))
        except Exception as e:
            print(f"! skip {p}: {e}"); continue
        recs = d if isinstance(d, list) else [d]
        for r in recs:
            base = _pick(r, "base", "ancestor", "o_base")
            ours = _pick(r, "ours", "a", "left")
            theirs = _pick(r, "theirs", "b", "right")
            exp = _pick(r, "expected", "resolution", "merged", "truth")
            if not (ours and theirs and exp):
                continue
            items.append({
                "id": _pick(r, "id", "name", default=os.path.basename(p)),
                "base": base, "ours": ours, "theirs": theirs, "expected": exp,
                "type": _pick(r, "type", "conflict_type", default="unknown"),
                "lang": _pick(r, "lang", "language", default="py"),
            })
    return items


def bootstrap_ci(flags, n=10000, seed=0):
    """95% CI for the mean of a 0/1 list via bootstrap."""
    if not flags:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = []
    k = len(flags)
    for _ in range(n):
        s = sum(flags[rng.randrange(k)] for _ in range(k))
        means.append(100.0 * s / k)
    means.sort()
    lo = means[int(0.025 * n)]
    hi = means[int(0.975 * n)]
    return (round(lo, 1), round(hi, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--tau", type=float, default=0.85)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--out", default="results/sync.json")
    args = ap.parse_args()

    resolve = get_resolver()
    fixtures = load_fixtures(args.fixtures)
    if not fixtures:
        raise SystemExit(f"No fixtures found under {args.fixtures}")

    total = len(fixtures)
    auto = []                       # accepted flags on auto-resolved subset
    by_type = defaultdict(list)     # type -> accepted flags (auto subset)
    auto_count = 0
    for fx in fixtures:
        res, conf = resolve(fx["base"], fx["ours"], fx["theirs"], fx["lang"])
        if conf < args.tau:
            continue                # escalated; not counted in accept-rate
        auto_count += 1
        ok = 1 if ast_equivalent(res, fx["expected"], fx["lang"]) else 0
        auto.append(ok)
        by_type[fx["type"]].append(ok)

    accept_pct = 100.0 * sum(auto) / auto_count if auto_count else 0.0
    ci = bootstrap_ci(auto, n=args.bootstrap)
    out = {
        "tau": args.tau,
        "total_conflicts": total,
        "auto_resolved": auto_count,
        "auto_resolve_rate_pct": round(100.0 * auto_count / total, 1),
        "conditional_accept_rate_pct": round(accept_pct, 1),
        "accept_rate_95ci": ci,
        "by_type": {t: {"n": len(v),
                        "accept_pct": round(100.0 * sum(v) / len(v), 1) if v else 0.0}
                    for t, v in sorted(by_type.items())},
        "note": "accept-rate is CONDITIONAL on auto-resolution; not a general accuracy figure.",
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(json.dumps(out, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
