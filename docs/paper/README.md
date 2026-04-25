# Research Paper

This folder contains the ASCEND research paper in both compiled PDF and LaTeX source forms.

## Files

- `ASCEND.pdf` - Compiled paper (13 pages).
- `main.tex` - LaTeX source.
- `IEEEtran.cls` - IEEE document class.
- `photo_placeholder.png` - Author bio photo (300x375 @ 300 DPI).

## Citation

See the repository root [`CITATION.cff`](../../CITATION.cff) for citation formats.

## Rebuilding the PDF

The bibliography is embedded in `main.tex` (no external `.bib` file), so only `pdflatex` passes are required:

```bash
cd docs/paper
pdflatex main.tex
pdflatex main.tex
pdflatex main.tex
```

Or with `latexmk`:

```bash
latexmk -pdf main.tex
```

## Submission target

The manuscript is under review at IEEE Access (https://ieeeaccess.ieee.org/), submitted April 2026. A preprint is also targeted for arXiv (cs.SE) and TechRxiv.

## Status

| Item            | State                                                             |
|-----------------|-------------------------------------------------------------------|
| Compilation     | Clean - no undefined references, no warnings                      |
| Page count      | 13                                                                |
| References      | 32, all archival publishers (IEEE / ACM / Springer / NIST / etc.) |
| Author metadata | ORCID 0009-0005-4435-0197 included                                |
| Author photo    | Real headshot, IEEE bio spec (1in x 1.25in @ 300 DPI)             |
