# ASCEND Examples

Reference applications demonstrating ASCEND integrated with real projects. Each example is self-contained and includes its own pipeline configuration, Dockerfile, tests, and setup guide.

## Examples overview

| Example | Language | Pipeline | What it demonstrates |
|---------|----------|----------|----------------------|
| [sample-python-app](./sample-python-app/) | Python / Flask | GitHub Actions | Web API with SAST + SCA + DAST |
| [sample-node-app](./sample-node-app/) | Node.js / Express | GitLab CI/CD | REST API with native GitLab security |
| [terraform-baseline](./terraform-baseline/) | Terraform (AWS) | (any platform) | IaC scanning with Checkov |
| [conflict-fixtures](./conflict-fixtures/) | N/A | N/A | JSON fixtures for testing AI sync |

## How to use the examples

### As a reference

Read through the example most similar to your stack. Adapt its pipeline and configuration into your repo.

### As a sandbox

Clone the example to a separate repository, push to GitHub / GitLab, and run the pipeline end-to-end. This lets you see what findings look like, what the pipeline output contains, and how quality gates fire — all without touching your real codebase.

### As an adoption trainer

Walk new team members through one of the examples to teach ASCEND concepts before exposing them to the organization's complete pipeline.

## Adding your own example

Contributions welcome. A good example should:

- Be small enough to understand in 30 minutes.
- Include realistic (non-trivial) security-relevant patterns.
- Demonstrate both passing and failing scenarios.
- Include a README explaining what each scan catches and why.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the PR workflow.
