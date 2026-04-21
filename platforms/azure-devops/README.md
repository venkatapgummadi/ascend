# ASCEND — Azure DevOps

Full reference configuration for the ASCEND framework on Azure DevOps Pipelines. This configuration is designed for enterprise scenarios requiring RBAC integration, audit trails, and Microsoft ecosystem compatibility.

## Files

- [`azure-pipelines.yml`](./azure-pipelines.yml) — Complete four-layer pipeline.

## Required extensions

Install from the Azure DevOps Marketplace at `Organization Settings → Extensions`:

- **SonarQube** (SonarSource)
- **Snyk Security Scan** (Snyk)
- **Trivy** (optional — included via Docker in the pipeline)

## Required service connections

Configure at `Project Settings → Service connections`:

| Name | Type | Purpose |
|------|------|---------|
| `SonarQube-Enterprise` | SonarQube | SAST scanning |
| `Snyk` | Generic / Snyk | SCA scanning |
| `$(dockerRegistryServiceConnection)` | Docker Registry | Container image publishing |
| `$(azureSubscriptionEndpoint)` | Azure Resource Manager | App Service deployment |

## Required pipeline variables

Add at `Pipelines → <Your Pipeline> → Variables`:

| Variable | Scope | Purpose |
|----------|-------|---------|
| `webAppName` | Pipeline | Target Azure App Service name |
| `resourceGroupName` | Pipeline | Azure resource group |
| `FOSSA_API_KEY` | Secret | FOSSA license compliance (optional) |
| `ASCEND_SYNC_WEBHOOK` | Secret | Layer 4 webhook URL |

## Required environments

Create at `Pipelines → Environments`:

- **staging** — no approval gates
- **production** — require approval from Security and Release teams (at least 2 approvers)

## Setup

### 1. Copy the pipeline

```bash
cp azure-pipelines.yml /path/to/your/repo/azure-pipelines.yml
```

### 2. Create the pipeline

In Azure DevOps: `Pipelines → New pipeline → Your repo → Existing Azure Pipelines YAML file`. Select `azure-pipelines.yml`.

### 3. Configure branch policies

At `Repos → Branches → main → Branch policies`, add:

- Require minimum number of reviewers: 1
- Check for linked work items
- Require build validation: select your ASCEND pipeline
- Require merge strategy: squash merge

This enforces pipeline pass before merge to `main`.

### 4. Configure environment approvals

At `Pipelines → Environments → production → Approvals and checks`, add:

- Approvals: Security Engineering group, Release Manager
- Business hours check: Mon–Fri 9am–5pm (prevent off-hours deployments)

## Audit trail

Azure DevOps automatically captures the audit trail required for SOC 2 Type II compliance:

- Pipeline runs (who, when, what)
- Approval decisions
- Deployment records
- Scan results persistence

Export via `Organization Settings → Auditing → Download logs`.

## Security scanning results in PR

Scan results appear in pull request comments via the SonarQube and Snyk Azure DevOps extensions. Configure at:

- `Project Settings → SonarQube → Pull request annotations: Enabled`
- `Project Settings → Snyk → Comment on pull requests: Enabled`
