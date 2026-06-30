# Benchmark results — provenance

These JSON files are the **actual output** of the released harness on public
inputs. They are committed so the paper's numbers are traceable; regenerate them
any time with the workflows below (do not hand-edit).

| File | Produced by | Inputs |
|---|---|---|
| `coverage.json` | `.github/workflows/coverage-benchmark.yml` → `run_coverage.py` | CodeQL (Java) + Semgrep (`p/owasp-top-ten` + `p/java`) on **OWASP BenchmarkJava @ `b51dbd8`** |
| `overhead.json` | `.github/workflows/overhead-benchmark.yml` → `run_overhead.py` | L1 (Semgrep, Bandit, gitleaks) + L2 (Trivy, Checkov) on `examples/sample-python-app`, 5 runs |
| `sync.json` | `examples/conflict-fixtures/run_fixtures.py` | conflict-type classification on the 7 public fixtures |

## Headline figures (as reported in the CARS paper)

- **Detection coverage (overall TP rate):** CodeQL 97% · Semgrep 67% · combined 99%.
  Per category — Injection 100/86/100, Insecure config 100/0/100, Crypto 92/46/98.
  Complementarity: +2.2 pts from adding Semgrep to CodeQL (97.0→99.2).
- **Overhead:** L1 median 0.06 min (P95 0.07), L2 median 0.05 min (P95 0.14),
  cumulative 0.11 min — tool-startup-dominated on a small app.
- **Synchronization:** conflict-type classification baseline 5/7 (71%); resolution
  accept-rate awaits resolution-labeled fixtures.

To regenerate: run the two workflows from the Actions tab, then
`python gen_latex.py results/coverage.json results/overhead.json` for paste-ready
LaTeX rows.
