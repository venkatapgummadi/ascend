# Evaluation — Reproducibility harness for the ASCEND paper

This directory holds the analysis pipeline behind §VIII (Tables V–IX) of the ASCEND IEEE Access submission.

## What's here

| File | Purpose |
|------|---------|
| `statistics.py` | Welch's t-test + Cohen's d on the five primary outcome variables. Reproduces the methodology of Table IX. |
| `aggregate-metrics.csv` | **SYNTHETIC schema-demonstration data only.** 12 repos × 26 weeks of plausibly-shaped values, deterministically generated, used to exercise `statistics.py` end-to-end. Does NOT replicate the paper's numbers. |
| `expected-synthetic-output.json` | The output `statistics.py` produces against the synthetic CSV. CI uses this to assert the script is deterministic and unbroken. |
| `paper-table9.json` | The **actual** numbers reported in Table IX of the paper. Regenerating these requires the real (NDA-protected) per-repository telemetry, which is not — and cannot be — released in this repository. |
| `requirements.txt` | Pinned numpy / scipy / pandas so the analysis is bit-exact. |

## How to run

```bash
pip install -r requirements.txt
python statistics.py --input aggregate-metrics.csv --output out.json
diff <(python -m json.tool expected-synthetic-output.json) <(python -m json.tool out.json)
```

If the diff is empty, the analysis pipeline is reproducing its expected output bit-for-bit. (This verifies the *machinery*, not the paper's numbers.)

## Reproducing the actual paper numbers

The 26-week, 12-repository telemetry came from three participating organisations under data-sharing agreements that prohibit redistribution. To reproduce `paper-table9.json` you need to:

1. Collect per-week, per-repository scan and CI/CD logs in the schema documented in [`docs/paper/EVALUATION.md`](../docs/paper/EVALUATION.md) §3 (Variables).
2. Apply the k-anonymisation pipeline described in EVALUATION.md §4 (Anonymisation pipeline). Cells with k < 5 must be suppressed.
3. Save the result as a CSV with the same columns as `aggregate-metrics.csv` (minus the leading comment line, plus your real values).
4. Run `python statistics.py --input <your.csv> --output <yours.json>`.
5. Compare against `paper-table9.json`.

If a reviewer requires per-repository disaggregation for their evaluation, please contact the corresponding author. The participating organisations have indicated willingness to grant restricted-access reproductions under suitable data-handling agreements.

## Why the data is not in the repository

This is standard practice for empirical software engineering papers in IEEE Access where the dataset originates from named industrial partners. See e.g. Forsgren et al. (2018) on the same data-handling pattern. The participating organisations declined to release per-repository telemetry because:

1. Repository names alone identify projects covered by NDA.
2. Vulnerability counts disaggregated by stack and week may reveal exploitable security postures during the baseline window.
3. Internal data-protection officers required k-anonymisation that, after suppression, leaves the public dataset insufficient for full reproduction.

The methodology — preregistered metrics, schema, statistical tests, and analysis script — is fully open. The aggregate-CSV → results.json pipeline is deterministic and inspectable.
