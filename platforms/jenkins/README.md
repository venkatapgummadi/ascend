# ASCEND — Jenkins

Declarative Jenkinsfile reference configuration for the ASCEND framework.

## Files

- [`Jenkinsfile`](./Jenkinsfile) — Complete four-layer pipeline.

## Prerequisites

### Required plugins

Install via `Manage Jenkins → Plugins`:

- SonarQube Scanner
- OWASP Dependency-Check
- Pipeline Utility Steps
- Credentials Binding
- AnsiColor
- HTML Publisher
- JUnit
- Warnings Next Generation
- Kubernetes CLI (if deploying to Kubernetes)
- Docker Pipeline
- Email Extension

### Required credentials

Configure in `Manage Jenkins → Credentials`:

| Credential ID | Type | Purpose |
|---------------|------|---------|
| `sonar-token` | Secret text | SonarQube authentication |
| `snyk-token` | Secret text | Snyk API token |
| `fossa-api-key` | Secret text | FOSSA license compliance (optional) |
| `ascend-sync-webhook` | Secret text | Layer 4 AI Sync webhook |
| `kubeconfig` | Secret file | Kubernetes deployment |
| `docker-registry` | Username/password | Container registry |

### Required tools

Available on agent nodes:

- Docker CLI
- Maven (or your build tool)
- `trivy`
- `snyk`
- `kubectl`

## Setup

### 1. Copy the Jenkinsfile

```bash
cp Jenkinsfile /path/to/your/repo/Jenkinsfile
```

### 2. Create the pipeline job

In Jenkins: `New Item → Pipeline`. Configure:

- Pipeline definition: *Pipeline script from SCM*
- SCM: Git
- Repository URL: your repo
- Script Path: `Jenkinsfile`

### 3. Configure SonarQube server

Go to `Manage Jenkins → System`. Find the SonarQube servers section and add:

- Name: `SonarQube-Enterprise` (must match the name used in the Jenkinsfile)
- Server URL: your SonarQube URL
- Server authentication token: select `sonar-token` credential

## Progressive rollout

Jenkins supports conditional pipeline logic. To start in reporting-only mode, wrap failing stages with `catchError`:

```groovy
catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
    sh 'trivy image --exit-code 1 ...'
}
```

This records failures as UNSTABLE without aborting the pipeline. Remove the `catchError` wrapper once the pipeline has been calibrated.

## Parallel scan performance

The Layer 1 and Layer 2 stages use `parallel` blocks to run scans concurrently. Ensure your Jenkins has sufficient executor capacity — recommend minimum 4 executors per agent for optimal throughput.
