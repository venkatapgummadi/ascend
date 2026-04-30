# IEEE Access — Pre-Resubmission Checklist

This document is for the manuscript author. It maps every reviewer-blocking issue identified in the April 2026 submitted PDF to its resolution and tells you what to change in the LaTeX source before resubmission.

> **Reviewer-blocker summary:** the submitted PDF contains 12+ unresolved `\cite{?}` references rendered as `[?]`. IEEE Access editorial staff routinely return papers with broken citations without sending them to reviewers. Fix this first, no matter what else you do.

---

## 1. Unresolved citations — `[?]` resolution table

Each row below maps a `[?]` occurrence in the submitted PDF to the BibTeX entry in [`references.bib`](./references.bib) that should replace it.

| ID | PDF location (section / sentence fragment) | BibTeX key | What to cite |
|----|--------------------------------------------|-----------|--------------|
| A  | §I "Humble and Farley [?] and Chen [?] identify configuration drift…" | `humble2010continuous` | Continuous Delivery (book) |
| B  | §I "…and Chen [?] identify configuration drift…" | `chen2015continuous` | IEEE Software 2015 |
| C  | §II.D "…research area termed 'Compliance-as-Code' or 'Policy-as-Code' [?]." | `sandall2018opa` | Open Policy Agent / Rego |
| D  | §II.D "Rahman et al. [?] constructed a defect taxonomy for IaC…" | `rahman2020source` | IST 2019 |
| E  | §II.D "In a complementary study on security smells in IaC, Rahman et al. [?]…" | `rahman2019seven` | ICSE 2019 (The Seven Sins) |
| F  | §II.D "Souppaya et al. [?] in the NIST Secure Software Development Framework…" | `souppaya2022ssdf` | NIST SP 800-218 |
| G  | §II.E "Schermann et al. [?] documented multi-track deployment patterns…" | `schermann2018doing` | IST 2018 |
| H  | §II.E "Savor et al. [?] described Facebook's multi-track deployment…" | `savor2016continuous` | ICSE-C 2016 |
| I  | §II.E "…Humble and Farley [?] and Chen [?]…" (second occurrence) | `humble2010continuous` | reuse |
| J  | §II.E "Chen [?] formalized continuous delivery architecture…" | `chen2015continuous` | reuse |
| K  | §VIII.G "large effect sizes (Cohen's d > 0.8 [?])…" | `cohen1988statistical` | Cohen 1988 (book) |
| L  | §IX "…the Hawthorne effect [?]." | `landsberger1958hawthorne` | Landsberger 1958 |
| M  | §X.A "remediation costs increase by a factor of 10–100x at each lifecycle stage [?]" | `boehm1981software` | Boehm 1981 |
| N  | §X.A "findings from Forsgren et al. [?]…" | `forsgren2018accelerate` | Accelerate (DORA) book |

**To apply** (for each row, in `main.tex`):

1. Locate the unresolved `\cite{...}` (the placeholder will be `\cite{?}` or `\cite{undefined-key}`).
2. Replace with `\cite{<bibtex-key>}` from the table above.
3. Either move the bibliography to use `\bibliography{references}` with `\bibliographystyle{IEEEtran}`, or copy the corresponding `\bibitem` entries from `references.bib` into the embedded thebibliography environment.

After fixing, run:

```bash
cd docs/paper
pdflatex main.tex
pdflatex main.tex      # second pass for cross-refs
grep -n '\[?\]' main.aux main.bbl 2>/dev/null && echo "STILL HAVE UNRESOLVED CITES" || echo "OK"
```

---

## 2. Code/paper alignment claims

A reviewer browsing the GitHub repo will compare paper claims to the implementation. The following gaps exist *as of April 2026*. Each is either resolvable in code, defendable as a future-work item in the paper, or both.

| Paper claim (location) | Repo state today | Recommended action |
|------------------------|------------------|--------------------|
| §VII.A "MLP risk scorer" trained on drift signals | `DriftDetector` uses a fixed weighted sum (semantic 0.50, config 0.25, embedding 0.25) | Either (a) provide an MLP variant in `ai-sync/ascend_sync/drift_scorer.py` or (b) reword §VII.A to say "weighted linear combination, replaceable with an MLP." Option (b) is honest and faster. |
| §VII.B "trained on 100,000 historical merge conflict resolutions" | `ConflictClassifier` ships a heuristic; no model included | Reword to: "shipped baseline classifier is heuristic; production deployments train the sklearn variant on organisation-specific data, with our reference deployment trained on 100,000 anonymised resolutions." This matches what `ai-sync/README.md` already states. |
| §VII.C "10,000 random token inputs were tested" | Verifier uses up to 100 by default (`property_tests=100`) | Either bump `property_tests=10000` and run the example, or change the case-study text to "100 sampled inputs from the property space" (recommended, faster). |
| §VII.D Eq. 6 "fine-tune via binary cross-entropy + L2" | No training code in repo | Acceptable as long as paper says "the framework supports continuous learning via the loss in Eq. 6; training pipeline is out of scope for this paper." |
| §VIII.A "12 enterprise repositories, 26 weeks" | Anonymised raw data not in repo (and likely cannot be released) | Add a `docs/paper/EVALUATION.md` documenting the experimental design + describing why per-repository telemetry is not released (NDA / data protection). This is standard practice in IEEE Access industrial papers. |
| §VIII.G p < 0.001, Cohen's d > 2.0 | No analysis script | Add `evaluation/statistics.py` that, given an aggregate CSV (which CAN be released after k-anonymisation), reproduces the t-test and effect-size numbers. Most reviewers accept this as "reproducible methodology" even if raw inputs are private. |
| §IV.A GitHub Actions snippet | Matches `platforms/github-actions/.github/workflows/ascend-full.yml` | OK |
| §IV.B GitLab CI snippet | Matches `platforms/gitlab-ci/.gitlab-ci.yml` | OK |
| §V.E Table II detection percentages | No corresponding script | Add a note in EVALUATION.md that detection rates are computed against a labelled vulnerability corpus (NIST SARD or similar). State the corpus. |

---

## 3. Repository hygiene the reviewer will audit

These are quick wins that reviewers consistently flag for IEEE Access industrial papers:

- [ ] **DOI for the artefact.** Mint a Zenodo DOI for the repo and paste it into `CITATION.cff` (`identifiers: - type: doi`). Reviewers want a citable, archived snapshot.
- [ ] **License headers.** Each non-trivial source file should carry `# SPDX-License-Identifier: MIT` (Python) or the equivalent `// SPDX-License-Identifier: MIT` (JS/TS). Currently absent.
- [ ] **`requirements.txt` next to `pyproject.toml`.** Not strictly required, but some reviewers run `pip install -r requirements.txt` blindly.
- [ ] **`Makefile` at repo root.** Single command (`make repro`) to reproduce the example_sync.py output and the conflict-fixtures hit rate.
- [ ] **README "Reproducing the paper's results" section.** Tell reviewers the exact commands.
- [ ] **CHANGELOG entry tagging this preprint.** Cite the Zenodo DOI once minted.

---

## 4. Issues you can dismiss safely

A reviewer might raise these; here is how to respond.

- **"Why not OWASP Top 10 2021/2023 alignment?"** Already aligned via Semgrep `p/owasp-top-ten`. State this explicitly in §V.A.
- **"Why MIT licence and not Apache 2.0?"** Either is acceptable for IEEE Access artefact policies; MIT is fine. Cite [PSL/PSF guidance](https://www.psfoundation.org/) if pressed.
- **"Why no comparison with Snyk / Dependabot baseline?"** ASCEND *integrates* these tools rather than replacing them — clarify in §I if the reviewer misreads positioning.

---

## 5. Pre-resubmission verification commands

Run these before regenerating the PDF:

```bash
# Verify all bibliography keys resolve
cd docs/paper
grep -oE '\\cite\{[^}]+\}' main.tex | sort -u | \
  while IFS= read -r cite; do
    key=$(echo "$cite" | sed 's/\\cite{\(.*\)}/\1/')
    grep -q "@.*{$key," references.bib || echo "MISSING: $key"
  done

# Compile and look for [?]
pdflatex main.tex >/dev/null
pdflatex main.tex >/dev/null
grep -c "{??}" main.aux 2>/dev/null && echo "STILL HAVE UNRESOLVED CITES" || echo "OK"

# Verify CITATION.cff parses
python3 -c "import yaml; yaml.safe_load(open('../../CITATION.cff'))" && echo "CITATION.cff OK"
```

---

## 6. Submission packet

When you resubmit to IEEE Access, the submission packet should contain:

- `main.pdf` — the compiled paper, with all `[?]` resolved.
- `main.tex` — the source.
- `references.bib` — this file (or the embedded `\bibitem` form).
- `IEEEtran.cls` — IEEE document class (download from IEEE if not bundled).
- A **cover letter** that:
  - Acknowledges the prior `[?]` issue and confirms it is resolved.
  - Lists which referee comments (if any) were addressed since the first submission.
  - Provides the GitHub permalink and (once minted) the Zenodo DOI for the artefact.

---

## 7. Reproducibility statement to include in the paper

Add or update this paragraph in §VIII or §XI:

> **Reproducibility.** The ASCEND framework, including platform configurations for all four CI/CD systems, the AI synchronization module source, the conflict-fixtures benchmark suite, and the experimental analysis scripts, is openly available at `https://github.com/venkatapgummadi/ascend` under the MIT licence. An archived snapshot is deposited on Zenodo with DOI <to-be-minted>. Per-repository telemetry from the 26-week study cannot be released due to organisational data-handling agreements; the aggregate metrics presented in Tables V–IX are provided in `evaluation/aggregate-metrics.csv` and the statistical analysis is reproduced by `evaluation/statistics.py`.
