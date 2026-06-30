# Ground-truth and acceptance rules

These are the rules the harness applies. State them verbatim in the paper so the
numbers are interpretable and reproducible.

## Detection coverage (Table II)
- **Ground truth:** OWASP Benchmark `expectedresults-*.csv`. Each test case has a
  CWE and a boolean `real` label. Only `real = true` cases count toward the
  denominator of a category.
- **Category mapping:** CWE → category is fixed in `benchmarks.yaml`
  (`category_map`). Report this mapping in an appendix or footnote.
- **True positive:** a `real = true` test case is "detected" by a tool if the tool
  emits a SARIF result whose file basename matches the test stem and whose CWE
  maps to that category (CWE `0`/unknown is allowed to match, since some tools do
  not emit CWE tags — note this limitation in the paper).
- **Combined / marginal:** combined = union of detected test cases across tools.
  Marginal = overall TP rate after greedily adding tools in alphabetical order.
- **Honesty:** report whatever rate results, including low ones. Do not curate the
  benchmark subset to inflate coverage.

### Adapters
- **SonarQube:** export issues via the web API, convert to SARIF (or adapt
  `load_sarif_hits`). Tag each issue with its CWE.
- **CodeQL:** `codeql database analyze ... --format=sarif-latest`. CWEs appear in
  rule `properties.tags` as `cwe-NNN` — already parsed.

## Synchronization (Section V)
- **Inputs:** the repo's public `examples/conflict-fixtures/` (ground-truth
  resolution included) and, optionally, conflicts mined deterministically from the
  public repos in `benchmarks.yaml` (`mined_repos`, pinned commit range).
- **Disjointness:** if you train the classifier, the training corpus named in
  `benchmarks.yaml` (`training_corpus`) must NOT include the evaluation fixtures or
  mined repos. State the corpus and the disjointness in the paper. This is what
  removes the train/test leakage Reviewer 1 flagged.
- **Auto-resolve decision:** resolver confidence `>= tau` (default 0.85).
- **Acceptance (AST-equivalence):** a proposed resolution is "correct" iff it is
  AST-equivalent to the ground-truth resolution. For Python, equal `ast.dump`
  (ignores whitespace/comments). For other languages, normalized-text equality
  (document this is stricter than true semantic equivalence).
- **Reported metrics:** auto-resolve rate `r`, conditional accept-rate `a` (with
  95% bootstrap CI), and per-type breakdown. `a` is **conditional on
  auto-resolution** — never report it as overall accuracy.

## Overhead
- Wall-clock minutes per layer over `--runs` repetitions; report median and P95.
- Only installed tools are timed; skipped tools are listed, not estimated.
- Hardware matters: report CPU/RAM and tool versions alongside the numbers.

## Reproducibility checklist for the paper
- [ ] OWASP Benchmark version/commit pinned
- [ ] Scanner versions pinned (semgrep, bandit, trivy, checkov, ...)
- [ ] Fixture commit hash recorded
- [ ] If trained: public training corpus named and shown disjoint from eval
- [ ] Hardware + OS recorded for overhead numbers
- [ ] `gen_latex.py` output pasted verbatim (no hand-editing of values)
