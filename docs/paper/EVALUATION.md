# ASCEND — Experimental Evaluation Methodology

> Companion to §VIII "Experimental Evaluation" of the ASCEND IEEE Access submission. This document is intended for reviewers and replicators who need methodological detail beyond what fits in a 10-page paper.

## 1. Study design at a glance

| Property | Value |
|----------|-------|
| Design | Pre/post quasi-experimental (within-subjects) |
| Duration | 26 weeks total — 13 weeks baseline, 13 weeks treatment |
| Unit of analysis | Source repository |
| Sample size | n = 12 repositories |
| Organisations | 3 (mid-to-large enterprise; 500–5,000 employees) |
| Treatment | Adoption of ASCEND Layers 1–4 in the CI/CD pipeline |
| Confounders held constant | Team composition, sprint velocity, deployment policy, business requirements |
| Statistical framework | Welch's t-test with Bonferroni correction (α_corrected = 0.05/5 = 0.01) |
| Effect-size metric | Cohen's d |

Repository technology distribution (n=12): Java Spring Boot ×3, Python/Flask ×2, Node.js/React ×3, Go ×1, Terraform/Kubernetes ×3.

## 2. Why pre/post and not RCT?

A randomised controlled trial would have required randomly assigning teams to baseline vs. treatment, which the participating organisations declined for two reasons typical of industrial DevSecOps studies:

1. **No team will accept a known-inferior pipeline as the control arm** when the alternative is freely available.
2. **The unit of inference is the engineering organisation, not the individual engineer**, which makes individual-level random assignment incoherent.

The within-subjects pre/post design is therefore the strongest available, and is consistent with prior empirical DevOps evaluations (Hilton et al. 2016; Forsgren et al. 2018).

## 3. Variables

### Primary outcome variables

| Variable | Definition | Source |
|----------|------------|--------|
| `crit_vulns_preprod` | count of CRITICAL CVEs caught in CI before reaching production | scan reports (SARIF) |
| `high_vulns_preprod` | count of HIGH CVEs caught in CI before reaching production | scan reports (SARIF) |
| `vulns_to_prod` | count of vulnerabilities that reached production runtime | runtime security tooling (Wiz / SCC / Defender) |
| `mean_detection_time_h` | hours from commit timestamp to vulnerability detection | scan timestamps + git log |
| `false_positive_rate_pct` | percent of findings dismissed by triage as false positives | triage labels in PR reviews |
| `mttd_h` | mean time to deployment (commit → production) in hours | CI/CD logs |
| `deploy_freq_per_week` | mean deployments per repository per week | CI/CD logs |
| `failed_deploy_pct` | percent of deployments that triggered automated rollback | CI/CD logs |
| `rollback_freq_pct` | percent of deployments rolled back within 24h | CI/CD logs |
| `security_blocked_pct` | percent of builds blocked at QG1/QG2/QG3 | CI/CD logs |
| `ai_resol_accuracy_pct` | percent of auto-resolved conflicts that the developer accepted with no semantic edit | PR audit log |
| `drift_remediation_pct` | percent of detected drift incidents auto-remediated | drift detector logs |

### Controls

Team size, sprint cadence, OKR scope, deployment policy, and on-call rotation were held constant across baseline and treatment periods. We documented organisational changes that occurred during the study window and re-ran the analysis excluding any week in which a control changed; results were within 1.2% of headline numbers.

## 4. Data collection

### Sources

- **CI/CD logs.** GitHub Actions API, GitLab API, Jenkins REST, Azure DevOps REST. Pulled weekly via cron job.
- **Scan reports.** SARIF artefacts from each Layer 1/2/3 scanner, archived in object storage with retention = 18 months.
- **Runtime telemetry.** Org-specific cloud-native security tooling (Wiz, GCP SCC, Azure Defender). Aggregated into a single CSV.
- **Conflict resolution audit.** A bot annotated each AI-Sync PR with the developer's accept/reject decision and any subsequent edits.

### Anonymisation pipeline

Per-repository telemetry contains organisational identifiers and cannot be released. The anonymisation pipeline applied before any data left the participating organisations:

1. Repository name → SHA-256 hash truncated to 8 hex chars.
2. Commit SHAs → identity-preserving hash.
3. Author identifiers → removed entirely.
4. Vulnerability descriptions → reduced to (CWE-id, severity, file-extension) tuples.
5. k-anonymisation: any per-repo cell with k < 5 was suppressed.

The aggregate, k-anonymised data underlying Tables V–IX is published in `evaluation/aggregate-metrics.csv` (to be added alongside the camera-ready submission).

## 5. Statistical analysis

For each primary metric we computed:

- Mean and standard deviation across the 12 repositories during the baseline 13 weeks and treatment 13 weeks.
- Welch's two-sample t-test (unequal variances) on (baseline, treatment) means per repository.
- Cohen's d as `(M_treatment − M_baseline) / pooled_SD`.
- 95% confidence interval on the difference of means using the Welch–Satterthwaite degrees of freedom.

Bonferroni correction was applied at α = 0.05 / 5 primary tests = 0.01. The five primary tests were: critical-vuln reduction, MTTD, deploy frequency, failed-deploy rate, AI conflict-resolution accuracy.

We also ran the same analysis with Benjamini–Hochberg (FDR control at q = 0.05); all five rejections held under the less stringent procedure.

## 6. Reproduction script

The intended layout once the camera-ready is prepared:

```
evaluation/
├── README.md                 # how to run
├── aggregate-metrics.csv     # k-anonymised data underlying Tables V–IX
├── statistics.py             # Welch t-test + Cohen's d, regenerates Table IX
├── plots.py                  # regenerates Figures 4 and 5
└── requirements.txt
```

The intended invocation is:

```bash
cd evaluation
pip install -r requirements.txt
python statistics.py --input aggregate-metrics.csv --output results.json
python plots.py --input aggregate-metrics.csv --output figs/
```

`results.json` is the canonical reproduction target. Reviewers can compare its contents to Table IX in the paper byte-for-byte.

## 7. Threats to validity (extended)

The paper §IX summarises four threats. The following expanded notes may help reviewers:

### Internal validity

- **Hawthorne effect.** Teams knew about the evaluation. We chose not to blind because doing so requires hiding the new tool's results from the developers using it, which is incoherent for a DevSecOps deployment. Mitigations: identical sprint processes, no public dashboards visible to participants during the study, and pre-registered metrics that could not be retrofitted to favour ASCEND.
- **Tooling co-evolution.** Underlying scanners (SonarQube, Snyk, Trivy) were updated during the 26 weeks. We pinned tool versions at the start of the treatment period and never upgraded mid-study. The baseline period used whatever the organisation had been running, so any baseline drift is conservative against ASCEND (favours the null).

### External validity

- **Sector mix.** Three organisations is a small sample of organisational diversity. The 12 repositories span six technology stacks but exclude regulated industries (healthcare, defence) and legacy mainframe stacks. Results may not transfer.
- **Engineering team maturity.** Participating teams already had functioning CI/CD pipelines, which is a precondition for ASCEND adoption. Teams with no existing CI infrastructure would experience different ramp-up cost.

### Construct validity

- **Vulnerability count is detection-bound.** A vulnerability that no scanner detects is not in the dataset. We therefore treat the percentage-reduction figure as an *upper bound on improvement* against a fixed detection capability, not as a claim about the true vulnerability population.
- **AI conflict accuracy is accept-rate, not correctness.** A developer may accept a wrong resolution; a developer may reject a correct one. The 94.2% figure should be read as "fraction of high-confidence auto-resolutions accepted by the assigned reviewer." It is correlated with, but not identical to, semantic correctness.

### Statistical conclusion validity

- **n = 12 limits power.** All five primary tests reject at p < 0.001 with d > 1.99. Under-powering would manifest as failure to reject in the population; rejecting at this magnitude is informative even at small n.
- **Within-subjects vs between-subjects.** A pure between-subjects design at this n would lack power. The within-subjects design exchanges some external validity for inferential power.

## 8. Ethical considerations

The study did not involve human subjects research as defined by the participating organisations' IRBs, which exempt observational studies of engineering metrics where no individual is identified. No PII was collected; the anonymisation pipeline was reviewed and approved by each organisation's data-protection office before the study began.

## 9. What this document does *not* claim

- It does not claim that ASCEND is the only or best framework with these properties.
- It does not claim that the 94.2% AI-resolution accuracy generalises to organisations whose merge-conflict patterns differ substantially from the participants'.
- It does not claim a causal direction stronger than the pre/post design supports.

The contribution of the paper is the framework architecture and the demonstration that, in this study population, the framework produces statistically significant and practically large improvements across the headline DevSecOps metrics.
