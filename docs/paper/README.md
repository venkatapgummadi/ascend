# Research Paper

This folder contains the ASCEND research paper in both compiled PDF and LaTeX source forms.

## Files

- `ASCEND.pdf` — Compiled paper.
- `main.tex` — LaTeX source.
- `IEEEtran.cls` — IEEE transaction class file (upstream copy from IEEE).

## Citation

See the repository root [`CITATION.cff`](../../CITATION.cff) for citation formats (BibTeX, APA, Chicago).

## Rebuilding the PDF

```bash
cd docs/paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or with `latexmk`:

```bash
cd docs/paper
latexmk -pdf main.tex
```

## Submission venues considered

- IEEE International Conference on Smart Computing (SMARTCOMP)
- IEEE International Conference on Services Computing (SCC)
- IEEE Secure Development Conference (SecDev)
- IEEE Software magazine (industrial experience reports)

## Abstract

The rapid adoption of DevOps methodologies and continuous integration/continuous deployment (CI/CD) pipelines has accelerated software delivery cycles while simultaneously introducing critical challenges in maintaining code quality and security throughout the software development lifecycle. This paper presents ASCEND (Automated Scanning, Compliance ENforcement, and Deployment), a comprehensive four-layer framework that integrates automated security scanning directly into CI/CD pipelines with build-gating mechanisms, multi-track deployment orchestration, and AI-powered post-deployment code synchronization.
