# Glossary

Definitions of terms used in ASCEND documentation.

## A

**AST (Abstract Syntax Tree).** A tree representation of the syntactic structure of source code. ASCEND uses AST-level comparison (rather than text-level diff) for drift detection to ignore formatting differences.

**ASCEND.** Automated Scanning, Compliance ENforcement, and Deployment. The four-layer DevSecOps framework described in this repository.

## B

**Blue-Green Deployment.** A deployment strategy maintaining two identical production environments (Blue and Green) with traffic routed to one at a time. Enables instant rollback by reverting traffic routing.

**Build Gate.** A check in a CI/CD pipeline that must pass before the build can advance. ASCEND defines three explicit build gates (Quality Gates 1, 2, and 3).

## C

**Canary Deployment.** A progressive rollout strategy that exposes a new version to a small percentage of production traffic before full rollout. Allows detection of regressions with limited blast radius.

**Checkov.** Open-source IaC static analysis tool from Bridgecrew / Prisma Cloud. Validates Terraform, CloudFormation, Kubernetes, and Dockerfile against security policy benchmarks.

**CI/CD.** Continuous Integration / Continuous Deployment. The practice of automatically building, testing, and deploying code changes.

**Circuit Breaker.** A fault-tolerance pattern that stops sending requests to a failing service. Used in ASCEND's AI synchronization layer to avoid hammering a broken LLM provider.

**CodeQL.** GitHub's semantic code analysis engine. Used in ASCEND for deep semantic security queries on GitHub-hosted repositories.

**Conflict Resolution.** In the ASCEND context, automated or AI-assisted resolution of merge conflicts between deployment branches.

**CVE (Common Vulnerabilities and Exposures).** A standardized identifier for publicly known security vulnerabilities.

## D

**DAG (Directed Acyclic Graph).** In ASCEND's AI synchronization layer, execution plans for resolution workflows are represented as DAGs.

**DAST (Dynamic Application Security Testing).** Testing the running application from the outside, as an attacker would. ASCEND uses OWASP ZAP for DAST at Layer 3.

**DevSecOps.** The integration of security practices into DevOps. ASCEND is a DevSecOps framework.

**Drift.** Divergence between code states in different branches or environments over time. ASCEND's Layer 4 detects and mitigates drift.

## E

**Embedding (code embedding).** A dense numerical vector representing a piece of code's semantic content. Used in drift detection to detect similarity independent of surface syntax.

## F

**Fail-fast.** A design principle where errors are detected and reported as early as possible. ASCEND's Layer 1 follows this principle by rejecting non-compliant code before expensive build operations.

**False Positive (FP).** A finding flagged by a scanner that isn't actually a real issue. ASCEND's multi-tool cross-validation reduces FPR.

**FOSSA.** Commercial license compliance and SCA platform. Used in ASCEND's Layer 2 for license checking.

## G

**Gitleaks.** Open-source secret detection tool. Alternative to TruffleHog.

**GQL / GHAS.** GitHub Advanced Security. GitHub's commercial add-on providing CodeQL scanning, secret scanning, and dependency review.

## H

**Hotfix.** An expedited patch, typically for a critical security vulnerability, deployed outside the normal release cadence. ASCEND defines a hotfix track with accelerated but still-gated deployment.

## I

**IaC (Infrastructure as Code).** Managing cloud infrastructure via versioned configuration files (Terraform, CloudFormation, Kubernetes manifests). ASCEND Layer 2 scans IaC for misconfigurations.

## J

**Jenkinsfile.** The declarative pipeline definition file for Jenkins. ASCEND provides a reference Jenkinsfile.

## K

**KICS (Keeping Infrastructure as Code Secure).** Open-source IaC scanner from Checkmarx. Alternative to Checkov.

## L

**Layer (ASCEND).** One of four pipeline stages: Source Analysis (L1), Build & Integration (L2), Deployment Orchestration (L3), AI Synchronization (L4).

**LLM (Large Language Model).** Transformer-based ML models used in ASCEND Layer 4 for merge conflict resolution.

## M

**MDT (Mean Detection Time).** Time from code commit to vulnerability detection. A key ASCEND metric.

**MRT (Mean Remediation Time).** Time from detection to fix deployment. A key ASCEND metric.

**Multi-track deployment.** Maintaining parallel code branches for different deployment targets (dev / staging / prod / hotfix). ASCEND explicitly supports this.

**MuleSoft.** An enterprise integration platform. Mentioned in the author's background but not part of the ASCEND framework itself.

## O

**OWASP (Open Web Application Security Project).** Non-profit producing security standards and tools. ASCEND uses OWASP Top 10 rulesets and OWASP ZAP for DAST.

## P

**PR (Pull Request).** A proposed code change awaiting review and merge. ASCEND's AI sync module creates PRs for AI-generated resolutions.

**PR Orchestrator.** Component of ASCEND Layer 4 that opens pull requests with AI-generated resolutions.

**Property-based testing.** Testing where properties that must hold are specified, and a framework generates many test inputs. ASCEND's Verifier uses property-based ideas to validate resolutions.

## Q

**Quality Gate (QG).** A named checkpoint in the ASCEND pipeline that must pass before code advances. ASCEND defines QG1, QG2, QG3 at the boundaries of Layers 1, 2, and 3.

## R

**RASP (Runtime Application Self-Protection).** Security technology that runs within the application at runtime to detect and prevent attacks. Complementary to ASCEND's build-time scanning.

**Rolling Deployment.** A deployment strategy that gradually replaces instances of the old version with the new version. Zero-downtime for stateless applications with health checks.

## S

**SARIF (Static Analysis Results Interchange Format).** Standardized format for scanner output. ASCEND pipeline steps produce SARIF for GitHub Code Scanning integration.

**SAST (Static Application Security Testing).** Analyzing source code without executing it. ASCEND Layer 1 runs SAST.

**SBOM (Software Bill of Materials).** Machine-readable inventory of software components. On the ASCEND roadmap.

**SCA (Software Composition Analysis).** Analyzing dependencies for known vulnerabilities. ASCEND uses Snyk for SCA.

**Semgrep.** Open-source semantic code scanner. Faster than SonarQube and CodeQL with low false positive rate.

**SLSA (Supply Chain Levels for Software Artifacts).** A framework for supply chain integrity. ASCEND roadmap includes SLSA L2 / L3 attestations.

**SOC 2.** Service Organization Controls audit framework for service organizations. ASCEND artifacts support SOC 2 Type II audits.

**SonarQube.** Comprehensive multi-language SAST and code quality platform. Used in ASCEND Layer 1.

**SSO (Single Sign-On).** Authentication mechanism where credentials flow through a single identity provider. Common in enterprise CI/CD deployments.

## T

**TCSVC.** IEEE Computer Society Technical Committee on Services Computing.

**TCCLD.** IEEE Computer Society Technical Committee on Cloud Computing.

**TPC (Technical Program Committee).** The group of researchers and practitioners reviewing submissions to an academic conference.

**Trivy.** Open-source scanner for container images, filesystems, git repositories, IaC, and SBOMs.

**TruffleHog.** Open-source secret scanner with verified-secret detection (queries the issuing service to confirm credentials are valid).

## V

**Verifier (ASCEND).** Component of Layer 4 that validates candidate resolutions for parseability, signature preservation, security pattern preservation, and property-based tests.

## Z

**ZAP (OWASP Zed Attack Proxy).** Open-source DAST tool used in ASCEND Layer 3.
