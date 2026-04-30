"""Reproduce Table IX of the ASCEND IEEE Access submission.

Reads `aggregate-metrics.csv`, runs Welch's t-test + Cohen's d on the five
primary outcome variables, and emits a `results.json` whose numbers should
match `expected-results.json` byte-for-byte.

Usage:
    python statistics.py --input aggregate-metrics.csv --output results.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# Five primary metrics tested (paper §VIII.G, Table IX).
# Each entry is (metric_name, csv_column, direction)
# direction = +1 means treatment expected > baseline; -1 means treatment expected < baseline.
PRIMARY_METRICS = [
    ("crit_vuln_reduction", "crit_vulns_preprod", -1),
    ("mttd_reduction", "mttd_h", -1),
    ("deploy_freq_increase", "deploy_freq_per_week", +1),
    ("failed_deploy_reduction", "failed_deploy_pct", -1),
    ("ai_resolution_accuracy", "ai_resol_accuracy_pct", +1),
]


@dataclass(frozen=True)
class Result:
    metric: str
    baseline_mean: float
    treatment_mean: float
    t_stat: float
    p_value: float
    cohens_d: float

    def to_dict(self) -> dict:
        def _safe(x: float, ndigits: int | None = None) -> float | None:
            import math
            if x is None or (isinstance(x, float) and not math.isfinite(x)):
                return None
            return round(x, ndigits) if ndigits is not None else x
        return {
            "metric": self.metric,
            "baseline_mean": _safe(self.baseline_mean, 3),
            "treatment_mean": _safe(self.treatment_mean, 3),
            "t": _safe(self.t_stat, 3),
            "p": _safe(float(f"{self.p_value:.3g}")) if self.p_value is not None else None,
            "cohens_d": _safe(self.cohens_d, 3),
        }


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d using pooled standard deviation."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)
    pooled = np.sqrt(((na - 1) * var_a + (nb - 1) * var_b) / (na + nb - 2))
    if pooled == 0:
        return float("nan")
    return float((np.mean(b) - np.mean(a)) / pooled)


def per_repo_means(df: pd.DataFrame, column: str) -> tuple[np.ndarray, np.ndarray]:
    """Reduce per-week records to one number per repo per period."""
    grouped = df.groupby(["repo_id", "period"])[column].mean().unstack("period")
    baseline = grouped["baseline"].dropna().to_numpy()
    treatment = grouped["treatment"].dropna().to_numpy()
    return baseline, treatment


def analyse(df: pd.DataFrame) -> list[Result]:
    out: list[Result] = []
    for metric_name, column, direction in PRIMARY_METRICS:
        baseline, treatment = per_repo_means(df, column)
        # Welch's t-test (unequal variances)
        t_stat, p_value = stats.ttest_ind(baseline, treatment, equal_var=False)
        d = cohens_d(baseline, treatment)
        # Report magnitudes consistent with paper's framing (always positive t and d
        # in the expected direction).
        out.append(
            Result(
                metric=metric_name,
                baseline_mean=float(np.mean(baseline)),
                treatment_mean=float(np.mean(treatment)),
                t_stat=abs(float(t_stat)),
                p_value=float(p_value),
                cohens_d=abs(d) * (1 if direction * (np.mean(treatment) - np.mean(baseline)) > 0 else -1),
            )
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    df = pd.read_csv(args.input, comment='#')
    required = {"repo_id", "period", "week"} | {col for _, col, _ in PRIMARY_METRICS}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"CSV missing required columns: {sorted(missing)}")

    results = analyse(df)
    payload = {
        "n_repositories": int(df["repo_id"].nunique()),
        "weeks_baseline": int(df.loc[df["period"] == "baseline", "week"].nunique()),
        "weeks_treatment": int(df.loc[df["period"] == "treatment", "week"].nunique()),
        "alpha_corrected": 0.01,
        "results": [r.to_dict() for r in results],
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} ({len(payload['results'])} metrics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
