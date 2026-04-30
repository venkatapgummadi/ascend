# Research Paper

This directory holds the metadata, bibliography, and reviewer-facing materials for the ASCEND IEEE Access submission.

## Files in this directory

| File | Purpose |
|------|---------|
| `README.md` | This file. |
| `references.bib` | BibTeX for every citation in the paper, including resolutions for the unresolved `[?]` placeholders in the April 2026 submission. |
| `REVIEWER_CHECKLIST.md` | Pre-resubmission checklist mapping each `[?]` to its key, plus code-vs-paper alignment notes and verification commands. |
| `EVALUATION.md` | Extended methodology document for §VIII (variables, anonymisation pipeline, statistical procedure, threats to validity). |

## Files NOT in this directory

The compiled PDF (`ASCEND.pdf`), LaTeX source (`main.tex`), IEEE document class (`IEEEtran.cls`), and author bio photo are kept in the author's manuscript repository rather than this open-source artefact repo. This is intentional:

- The IEEE document class is redistributable but adds noise to the artefact.
- The PDF is a build product; pinning a specific compiled version inside the source-of-truth artefact creates drift each time the manuscript is revised.
- The bio photo is an identity artefact and is not needed for reproduction.

If you are a reviewer who needs the LaTeX source or compiled PDF before formal acceptance, please contact the corresponding author at `venkata.p.gummadi@ieee.org`. Once the paper is accepted, the camera-ready PDF will be linked from the repository top-level README via its IEEE Access DOI.

## Citation

See [`../../CITATION.cff`](../../CITATION.cff) at the repository root for the canonical citation metadata in CFF format.

## Status

| Item | State |
|------|-------|
| Manuscript | Under review at IEEE Access (submitted April 2026) |
| Bibliography | Resolved — see `references.bib` and `REVIEWER_CHECKLIST.md` |
| Reproducibility harness | Implemented at `evaluation/` and `examples/conflict-fixtures/` |
| ORCID | 0009-0005-4435-0197 |
| Zenodo DOI | Pending; will be minted before camera-ready submission |
| Author photo | IEEE bio spec (1in × 1.25in @ 300 DPI), kept in manuscript repo |
