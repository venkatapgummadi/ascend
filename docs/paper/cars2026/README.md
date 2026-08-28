# ASCEND — IEEE CARS 2026 conference paper

`ASCEND-CARS2026-camera-ready.pdf` is the camera-ready version of:

> V. P. K. Gummadi, "ASCEND: A Verification-Gated DevSecOps Framework with
> AI-Assisted Synchronization," IEEE Cyber Awareness and Research Symposium
> (CARS), 2026.

## Numbers in the paper map to this repository

Every typeset result is regenerated from `benchmark/`:

| Paper table | Source |
|---|---|
| Detection coverage on OWASP BenchmarkJava (`b51dbd8`) | `benchmark/results/coverage.json` |
| Conflict-type classification baseline (5/7) | `benchmark/results/sync.json` |
| Per-layer L1/L2 CI overhead | `benchmark/results/overhead.json` |

## Scope of claims

The paper reports detection coverage, a deterministic conflict-type
classification baseline, and scanning overhead. It does **not** report an
end-to-end auto-resolution accept-rate or verification-gate false-accept /
false-reject rates: those require a public conflict corpus carrying ground-truth
merged resolutions, which is not yet released with this artifact. See
`benchmark/results/sync.json` for the current status.

The earlier manuscript under `docs/paper/manuscript/` targets a different venue
and format and is retained for history; where the two disagree, this
camera-ready is authoritative.
