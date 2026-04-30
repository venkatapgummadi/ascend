# ASCEND — IEEE Access Manuscript Source

This directory contains the camera-ready Overleaf-compatible source for the ASCEND IEEE Access submission, regenerated on the mandatory `ieeeaccess` document class after the editorial-screening rejection of 30 April 2026.

## Files

| File | Purpose |
|------|---------|
| `main.tex` | Manuscript source (rebuilt on the `ieeeaccess` template). |
| `main.pdf` | Compiled PDF — 11 pages, single-author, all citations resolve, no `[?]` markers. |
| `main.bbl` | BibTeX intermediate; included so reviewers can compile without a `bibtex` pass if they wish. |
| `references.bib` | Bibliography source (32 entries). |
| `ieeeaccess.cls`, `IEEEtran.cls`, `IEEEtran.bst`, `spotcolor.sty` | IEEE Access template files (do not modify). |
| `t1-*.{pfb,tfm}`, `t1*.fd`, `*.map` | IEEE Access bundled fonts. |
| `logo.png`, `notaglinelogo.png`, `bullet.png`, `equation3.png` | Template assets. |

## What changed since the rejected version (Access-2026-19209)

The editorial office returned the manuscript with three fixable issues. All are addressed:

1. **Mandatory IEEE Access template applied.** The previous PDF used a generic `IEEEtran` configuration; this version uses `\documentclass{ieeeaccess}` per the editorial requirement.
2. **All `[?]` citations resolved.** The previous PDF had 14 unresolved `\cite{?}` placeholders. Every `\cite{...}` in the new `main.tex` resolves to a real entry in `references.bib`. The bibliography contains 32 entries; 12 of them are the resolutions for the broken cites (Humble & Farley, Chen, Souppaya/NIST SSDF, Rahman ×2, Schermann, Savor, Cohen, Landsberger, Boehm, Forsgren, Sandall/OPA).
3. **Grammar pass applied.** Every paragraph was rewritten for active voice where appropriate, dangling modifiers removed, comma splices fixed, and abbreviations defined on first use. The abstract was tightened to ~250 words and now contains no embedded citations or display equations as the IEEE Access guide requires.

## How to use this directory

### Option A — Overleaf

1. Zip the entire directory: `zip -r ascend-manuscript.zip *`.
2. In Overleaf, select **New Project → Upload Project** and upload the zip.
3. In the Overleaf project menu, set the main document to `main.tex` and the compiler to **pdfLaTeX**.
4. Click **Recompile**. Overleaf runs `pdflatex → bibtex → pdflatex → pdflatex` automatically.
5. Download the PDF when satisfied.

### Option B — Local TeX Live

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Required TeX Live packages: `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-publishers`. The IEEE Access fonts and class file are bundled in this directory so no system-level IEEE installation is needed.

## Resubmission packet for IEEE Access

Per the editorial email, upload the following to the IEEE Author Portal:

- `main.pdf` — compiled manuscript.
- `main.tex` — source.
- `references.bib` — bibliography.
- `ieeeaccess.cls`, `IEEEtran.cls`, `IEEEtran.bst`, `spotcolor.sty`, plus the `t1-*` fonts and `*.png` assets — the template bundle (some portals only need the source; others want the full compilation set).

The Manuscript ID is **Access-2026-19209**. Reply to the editorial email or use the IEEE Author Portal "resubmit as draft" workflow.

## Post-acceptance

When the manuscript is accepted:

1. Add the IEEE Access DOI to the `\doi{...}` line of `main.tex` (currently a placeholder).
2. Update the `\history{...}` line with the publication date IEEE provides.
3. Mint a Zenodo DOI for the v0.1.0 source artefact and update `CITATION.cff` at the repo root.
4. Update `CHANGELOG.md` with the IEEE Access volume / page numbers.

## Repository linkage

This manuscript directory lives inside the ASCEND open-source repository at `https://github.com/venkatapgummadi/ascend`. The `\url{}` reference in §Reproducibility is the canonical pointer; reviewers can audit the framework, run the reproducibility harness (`make repro`), and inspect the bibliography integrity (`docs/paper/REVIEWER_CHECKLIST.md`) directly from the repo.
