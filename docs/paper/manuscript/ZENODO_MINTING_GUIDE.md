# Minting the Zenodo DOI for the ASCEND v1.0 Release

This guide covers the one-time process of getting a citable DOI from Zenodo for the ASCEND submission release. It takes roughly 10 minutes end-to-end. Do this before you submit the camera-ready version to IEEE Access; the placeholder `10.5281/zenodo.PENDING` in the manuscript must be replaced with the actual DOI Zenodo assigns.

## Why this matters

IEEE Access reviewers and editors increasingly expect software artifacts to carry a persistent identifier (DOI) so that the *exact* version of the code described in the paper can be cited and retrieved years from now, even if the GitHub repository moves, gets renamed, or is taken down. Zenodo is the standard CERN-operated, free, archival service for this. A single Zenodo DOI per paper release is the convention.

## Prerequisites

- A GitHub account that owns or admins the `venkatapgummadi/ascend` repository.
- A web browser. No CLI tools needed.

## Step 1 — Connect Zenodo to your GitHub account (one-time)

1. Open <https://zenodo.org/account/settings/github/> and sign in (you can sign in via GitHub).
2. Authorize Zenodo to read your GitHub repositories. Zenodo only needs read access to public-repository releases; it will not push or modify code.
3. On the resulting page, find `venkatapgummadi/ascend` in the repository list and toggle its switch **ON**. Zenodo is now watching for new GitHub Releases on that repo.

## Step 2 — Cut the v1.0 release on GitHub

1. From the IEEE Access manuscript directory, ensure the local clone is up to date and you are on the commit you want to archive (the commit whose PDF was submitted):
   ```powershell
   cd C:\dev\ascend
   git checkout main           # or whichever branch carries the submission state
   git pull --ff-only
   git log -1 --oneline        # note the commit SHA
   ```
2. On GitHub, navigate to <https://github.com/venkatapgummadi/ascend/releases/new>.
3. Set:
   - **Tag**: `v1.0`
   - **Target**: `main` (or the SHA from above)
   - **Release title**: `ASCEND v1.0 (IEEE Access submission, April 2026)`
   - **Description**: paste the relevant CHANGELOG entry, or the summary below:
     ```
     Submission release accompanying the ASCEND IEEE Access manuscript
     (Access-2026-19209). Includes the four-layer DevSecOps framework,
     reference configurations for GitHub Actions / GitLab CI/CD / Jenkins /
     Azure DevOps, the AI synchronization module (ai-sync/), the conflict-
     fixtures benchmark suite, and the experimental analysis pipeline
     (evaluation/). License: MIT.
     ```
4. Click **Publish release**.

Within 1--3 minutes Zenodo automatically detects the release and creates a deposit. You will receive a confirmation email.

## Step 3 — Retrieve the DOI

1. Open <https://zenodo.org/account/settings/github/> again.
2. Find the `ascend` row; the latest minted DOI is shown next to the version. It looks like `10.5281/zenodo.12345678`.
3. Click the DOI to open the deposit page. Verify:
   - Title, authors, and license are correct.
   - The ZIP attachment matches the v1.0 release.
   - The "Cite as" block shows a clean BibTeX-ready entry.
4. If anything is wrong, click **Edit** on the Zenodo page, fix metadata, and **Publish** again. (The DOI does not change.)

## Step 4 — Update the manuscript and CITATION.cff

Replace `PENDING` with the actual Zenodo identifier in three places:

### A. `docs/paper/manuscript/references.bib`
```bibtex
@misc{gummadi2026ascend-software,
  ...
  doi = {10.5281/zenodo.12345678},   <!-- replace 12345678 with the real number -->
  ...
}
```

### B. `docs/paper/manuscript/main.tex`
Search for both occurrences of `10.5281/zenodo.PENDING` (one in `\tfootnote{}`, one in `\section*{Data Availability Statement}`) and replace with the real DOI.

### C. `CITATION.cff` at the repo root
```yaml
identifiers:
  - type: doi
    value: "10.5281/zenodo.12345678"
    description: "Zenodo archive of the v1.0 source artefact."
```

Recompile the PDF (`pdflatex → bibtex → pdflatex → pdflatex` — or just **Recompile** in Overleaf), and re-export the Overleaf zip for the camera-ready submission.

## Step 5 — Commit and push

```powershell
cd C:\dev\ascend
git add -A
git commit -m "paper: replace Zenodo PENDING placeholder with minted DOI 10.5281/zenodo.XXXXXXXX"
git push
```

## Sanity check

After the steps above:

- The PDF's reference list shows `[1] V. P. K. Gummadi, "ASCEND: A comprehensive DevSecOps framework..., 2026, ..., DOI 10.5281/zenodo.<minted-id>."`
- The Data Availability Statement reads `DOI 10.5281/zenodo.<minted-id>` rather than `PENDING`.
- The title-page footnote on page 1 reads the same.
- `CITATION.cff` parses as YAML 1.2 / CFF 1.2.0 with the new DOI.

You're ready to upload the camera-ready PDF and source bundle to the IEEE Author Portal.

## FAQ

**Q. Can I mint the DOI before getting the manuscript accepted?**
Yes, and it is recommended. Reviewers can audit the exact version of the code described in your submission. The DOI is permanent regardless of acceptance outcome.

**Q. Can I update the code after minting?**
Yes. Each new GitHub release produces a new Zenodo deposit with a new DOI. The "concept DOI" (e.g., `10.5281/zenodo.12345678` versus `10.5281/zenodo.12345679` for v1.1) always resolves to the latest version, while versioned DOIs preserve historical states. Cite the v1.0 versioned DOI in the manuscript.

**Q. Does Zenodo charge?**
No. Zenodo is operated by CERN and the OpenAIRE infrastructure, supported by the European Commission. Free for individual deposits up to 50~GB.

**Q. What if `venkatapgummadi/ascend` is private?**
Make it public for at least the duration of GitHub release creation. Zenodo cannot deposit from private repositories.
