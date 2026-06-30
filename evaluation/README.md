# Evaluation

ASCEND's evaluation is reproducible from **public inputs only**. There is no
NDA-protected telemetry and no private per-repository dataset in the loop. Earlier
drafts reported a multi-organization pre/post field study; those numbers are
**withdrawn** because they cannot be independently reproduced. This directory now
documents the public benchmark that anyone can rerun.

## What is measured

| Metric | Source of ground truth | Script |
|---|---|---|
| Detection coverage (per-category + combined TP rate, tool complementarity) | OWASP Benchmark labeled test cases | `../benchmark/run_coverage.py` |
| Conflict resolution: auto-resolve rate + **conditional** accept-rate (95% CI) + by-type | Public `examples/conflict-fixtures/` (and optional mined public conflicts) | `../benchmark/run_sync.py` |
| Scanning overhead per layer (median, P95) | Bundled sample apps | `../benchmark/run_overhead.py` |

The conflict accept-rate is **conditional on auto-resolution** — it is the fraction
correct among conflicts the system chose to auto-resolve, not a general accuracy
figure. The auto-resolve rate is reported separately.

## Run it

```bash
make repro          # install -> test -> lint -> public benchmark -> latex rows
# or individually:
make eval-coverage  # detection coverage on OWASP Benchmark
make eval-sync      # conflict-resolution metrics on public fixtures
make eval-overhead  # per-layer scanning overhead
make eval-latex     # print LaTeX rows for the paper tables
```

## Honesty rules

- Report whatever the harness prints, including low numbers.
- Keep the "conditional on auto-resolution" wording on the accept-rate.
- Pin and record: OWASP Benchmark version, scanner versions, fixture commit, any
  public training corpus (shown disjoint from evaluation), and hardware/OS for
  overhead. See `../benchmark/ground_truth_rules.md`.

## Note on the old manuscript
The IEEE Access manuscript under `docs/paper/` describes a field study that is no
longer part of this project. See `docs/paper/README.md` for its superseded status
and the current (public-benchmark) paper.
