# ASCEND — paper

## Current manuscript (active)

**Title:** ASCEND: A Verification-Gated DevSecOps Framework with AI-Assisted
Synchronization

**Status:** preprint / under submission to a peer-reviewed venue. Not yet accepted.

This version scopes all empirical claims to the **public benchmark** in
[`../../benchmark/`](../../benchmark/): detection coverage on the labeled OWASP
Benchmark, conflict-resolution metrics on the public `examples/conflict-fixtures/`
(auto-resolve rate plus a **conditional** accept-rate), and per-layer scanning
overhead on the sample apps. Every number is regenerable with `make repro`.

The source for this version is maintained outside the repo until acceptance; on
acceptance, the camera-ready and DOI will be added here and to `CITATION.cff`.

## Superseded manuscript (withdrawn — kept for history only)

An earlier manuscript titled *"ASCEND: A Comprehensive DevSecOps Framework for
Automated Code Scanning, Multi-Track Deployment, and AI-Powered Post-Deployment
Synchronization in Enterprise CI/CD"* reported a 26-week pre/post study across
twelve repositories from three organizations (e.g., 83.0% critical-vuln reduction,
43.5% MTTD improvement, 94.2% conflict-resolution accuracy at p<0.001, d>2.0).

**Those results are withdrawn.** The study relied on private, non-releasable
per-repository telemetry and could not be independently reproduced; peer review
correctly identified it as underpowered, uncontrolled, and conflicted. Do not cite
those figures. The files `EVALUATION.md` and `REVIEWER_CHECKLIST.md` in this folder
pertain to the withdrawn manuscript and are retained only as historical record.

If you are evaluating ASCEND, use the current manuscript and the public benchmark.
