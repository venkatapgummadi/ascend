# Compliance Framework Mapping

Detailed mapping of ASCEND components to major information security compliance frameworks. This document is a planning aid, not legal advice; your organization's compliance program should be designed with qualified auditors.

## How to use this document

1. Identify the frameworks that apply to your organization.
2. Map each control requirement to the relevant ASCEND layer or component.
3. Configure evidence capture so artifacts are preserved long enough for your audit cycle.
4. Review quarterly with your compliance team to catch control drift.

## PCI DSS 4.0

Applies to organizations processing, storing, or transmitting cardholder data.

| Requirement | Description | ASCEND component | Evidence artifact |
|-------------|-------------|------------------|-------------------|
| 6.3.1 | Bespoke and custom software developed by the entity is reviewed | Layer 1 SAST (CodeQL, Semgrep, SonarQube) | SARIF reports per commit |
| 6.3.2 | Inventory of bespoke/custom software, including third-party components | Layer 1 SCA (Snyk) + Layer 2 Container scan (Trivy) | Dependency manifest per build |
| 6.3.3 | Third-party software vulnerabilities are identified and managed | Layer 1 SCA + Layer 2 Container | Vulnerability report per deploy |
| 6.4.1 | Public-facing web applications are protected against attacks | Layer 3 DAST (OWASP ZAP) | ZAP baseline + full scan reports |
| 6.4.2 | Authenticated / automated vulnerability scanning | Layer 3 DAST with authenticated sessions | ZAP authenticated scan reports |
| 6.4.3 | All payment page scripts managed | Specific to payment pages — extend with CSP scanning | CSP reports |
| 6.5.1-6.5.6 | Developers trained in secure coding | Layer 1 findings + remediation guidance | Training records + findings trend |
| 11.3.1 | Internal and external vulnerability scanning | All layers | Consolidated scan history |
| 11.4.5 | Changes are reviewed prior to deployment | Quality gates | QG pass/fail record per deploy |
| 12.10.5 | Incident response includes automated alerting | ASCEND webhook integration | Alert log |

## SOC 2 Type II

Applies to service organizations handling customer data. Focus on the Trust Service Criteria (TSC) relevant to security.

### Common Criteria (CC) mappings

| Criterion | Description | ASCEND component | Evidence |
|-----------|-------------|------------------|----------|
| CC5.1 | The entity selects and develops control activities | Quality gate configuration | `quality-gates/` configs versioned in git |
| CC7.1 | Detection and monitoring of vulnerabilities | All Layer 1 / 2 / 3 scanning | Scan history with timestamps |
| CC7.2 | Monitoring of system components | Pipeline monitoring | CI/CD audit logs |
| CC7.3 | Anomalies communicated to responsible parties | Alert routing via PR comments, webhooks | Alert delivery logs |
| CC7.4 | Response to identified vulnerabilities | Remediation workflow | PR commit history showing fix → merge → deploy |
| CC8.1 | Authorization before changes are deployed | Quality gates + manual approval in Layer 3 | QG records + approval records |
| CC8.2 | Infrastructure changes are documented | IaC + Layer 2 IaC scanning | Terraform state + Checkov reports |

### Security-specific additional criteria

| Criterion | ASCEND component |
|-----------|------------------|
| Logical access controls | Pipeline secret management (vault / KMS integration) |
| System operations | Automated deployment with rollback |
| Change management | Branch protection + quality gates |
| Risk mitigation | Composite quality score + threshold enforcement |

### Evidence collection for SOC 2

SOC 2 audits typically look at a 6–12 month window. Retain:

- All scan reports (SARIF) for ≥ 12 months.
- CI/CD pipeline execution logs for ≥ 12 months.
- Quality gate pass/fail records for ≥ 12 months.
- Deployment history (who, when, what) for ≥ 12 months.
- Approval records (code review, environment approvals) for ≥ 12 months.
- Policy exception register with documented expirations.

## HIPAA Security Rule

Applies to covered entities and business associates handling electronic Protected Health Information (ePHI).

### 45 CFR § 164.308 — Administrative Safeguards

| Subsection | Requirement | ASCEND alignment |
|------------|-------------|------------------|
| (a)(1)(ii)(A) | Risk analysis | Layer 1 SAST + SCA identifies vulns that could expose ePHI |
| (a)(1)(ii)(B) | Risk management | Quality gates enforce risk thresholds before deploy |
| (a)(1)(ii)(D) | Information system activity review | CI/CD audit trails |
| (a)(8) | Evaluation | Quarterly review of scan trends |

### 45 CFR § 164.312 — Technical Safeguards

| Subsection | Requirement | ASCEND alignment |
|------------|-------------|------------------|
| (a)(1) | Access control | Pipeline secrets management; environment approvals |
| (b) | Audit controls | Full audit trail of code changes, scans, deployments |
| (c)(1) | Integrity | Scan history + code signing (SBOM + Sigstore on roadmap) |
| (e)(1) | Transmission security | IaC scan validates TLS configurations; DAST tests for TLS issues |

## NIST Cybersecurity Framework (CSF) 2.0

Mappings to the CSF functions and categories most relevant to secure software development.

### Identify (ID)

| Category | ASCEND alignment |
|----------|------------------|
| ID.AM: Asset Management | Dependency inventory via SCA |
| ID.RA-1: Asset vulnerabilities identified | Layer 1 + Layer 2 scanning |
| ID.RA-3: Internal and external threats identified | DAST threat modeling via scan rules |
| ID.SC: Supply Chain | SCA + container scanning; SBOM generation on roadmap |

### Protect (PR)

| Category | ASCEND alignment |
|----------|------------------|
| PR.AC: Identity management and access control | Secret scanning prevents credential leakage |
| PR.DS-6: Integrity checking | Code signing + quality gates |
| PR.IP-2: SDLC to manage systems | Full four-layer framework |
| PR.IP-12: Vulnerability management plan | Scan cadence + remediation workflow |

### Detect (DE)

| Category | ASCEND alignment |
|----------|------------------|
| DE.CM-1: Network monitored | Layer 3 DAST |
| DE.CM-4: Malicious code detected | Layer 2 container + SCA scanning |
| DE.CM-8: Vulnerability scans performed | All scanning layers |

### Respond (RS) and Recover (RC)

| Category | ASCEND alignment |
|----------|------------------|
| RS.AN-2: Incident impact understood | Scan reports provide blast radius |
| RS.MI-3: Newly identified vulnerabilities mitigated or documented as accepted | Remediation workflow + exception register |
| RC.RP: Recovery plan executed | Automated rollback on Layer 3 gate failure |

## ISO/IEC 27001:2022 — Annex A

Controls relevant to secure development lifecycle.

| Control | Description | ASCEND alignment |
|---------|-------------|------------------|
| A.5.30 | ICT readiness for business continuity | Blue-green deployment + automated rollback |
| A.8.8 | Management of technical vulnerabilities | SCA + Container + DAST |
| A.8.25 | Secure development life cycle | Framework |
| A.8.26 | Application security requirements | Quality gate policies |
| A.8.27 | Secure system architecture and engineering principles | Architecture docs + SAST enforcement |
| A.8.28 | Secure coding | SAST + Semgrep rules |
| A.8.29 | Security testing in development and acceptance | SAST + DAST |
| A.8.30 | Outsourced development | SCA for third-party code |
| A.8.31 | Separation of development, test and production | Multi-track deployment |
| A.8.32 | Change management | Quality gates |

## NIST SP 800-53 Rev 5 — Key controls

For organizations serving US federal customers (FedRAMP, DoD, etc.).

| Control ID | Control name | ASCEND alignment |
|------------|--------------|------------------|
| CA-7 | Continuous monitoring | Continuous scanning via CI/CD integration |
| CM-3 | Configuration change control | Quality gates + approval flow |
| RA-5 | Vulnerability monitoring and scanning | All scanning layers |
| SA-11 | Developer security testing | Layer 1 SAST + Layer 3 DAST |
| SA-15 | Development process, standards, and tools | Documented framework |
| SI-2 | Flaw remediation | Automated inline remediation via PR comments |
| SI-7 | Software, firmware, and information integrity | Code signing + SCA |

## FedRAMP moderate and high baselines

ASCEND components map to FedRAMP by inheriting from the NIST 800-53 mappings above. Additionally:

- **Continuous monitoring** (CA-7) — ASCEND's per-commit scanning and post-deploy drift detection satisfy this.
- **Supply chain risk** (SR family) — SCA covers third-party component scanning; SBOM on the roadmap.
- **Security assessment** (CA-2) — scan reports and quality gate records provide evidence.

FedRAMP-specific considerations:

- Scan reports must be retained in ATO-authorized storage.
- Third-party scanning SaaS (Snyk cloud, Semgrep cloud) must have their own FedRAMP authorization or be replaced with self-hosted equivalents.
- Evidence must be available for Continuous Monitoring Phase 3 (ongoing assessment).

## GDPR and data protection regulations

GDPR doesn't mandate specific technical controls, but Article 25 (Data Protection by Design) and Article 32 (Security of Processing) expect demonstrable secure development. ASCEND supports:

- **Demonstrable security measures** (Art. 32) — scan reports, audit trails, and policy configurations serve as evidence.
- **Data protection by design** (Art. 25) — SAST rules can enforce specific patterns (e.g., logging PII, missing consent checks).

Extend Layer 1 with GDPR-specific Semgrep rules:

```yaml
- id: ascend-pii-in-logs
  pattern-either:
    - pattern: logger.info(..., email=$E, ...)
    - pattern: logger.info(..., ssn=$S, ...)
  message: "Potential PII in logs"
  severity: WARNING
  metadata: { category: privacy, gdpr: "Article 5(1)(c)" }
```

## CIS Controls v8

Center for Internet Security's prioritized controls.

| Control | ASCEND alignment |
|---------|------------------|
| CIS 4 (Secure Configuration) | IaC scanning via Checkov |
| CIS 7 (Continuous Vulnerability Management) | All scanning layers |
| CIS 16 (Application Software Security) | Full framework |
| CIS 18 (Penetration Testing) | DAST provides baseline; complements human red-teaming |

## Audit readiness checklist

Before an audit, verify:

- [ ] Scan reports from the last 13 weeks are accessible.
- [ ] CI/CD logs preserved and exportable.
- [ ] Quality gate configuration is versioned in git.
- [ ] Approval records for production deploys are retained.
- [ ] Policy exceptions are documented with expiration dates.
- [ ] None of the expirations are in the past (or if so, they're renewed with justification).
- [ ] Scan tool versions are pinned and match the configured baseline.
- [ ] Training records for developers on secure coding (if framework requires).
- [ ] Incident response records with ASCEND alert trail.

## Disclaimer

This mapping is offered as a planning aid. Compliance determinations must be made by qualified auditors and legal counsel applicable to your jurisdiction and industry. The author makes no warranty that implementing ASCEND will satisfy any specific regulatory requirement.
