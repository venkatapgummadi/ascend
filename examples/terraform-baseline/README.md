# Terraform IaC Baseline Example

A reference Terraform configuration demonstrating Checkov-compliant Infrastructure-as-Code patterns. Use this as a template for new infrastructure modules or for comparing against your existing Terraform.

## What this example demonstrates

- AWS VPC with flow logs, private subnets, and NAT gateway.
- Encrypted S3 bucket with blocked public access, versioning, and lifecycle policies.
- KMS keys with rotation enabled for encryption.
- IAM roles with least privilege.
- Security group with explicit egress rules (no default allow-all).

## Structure

```
terraform-baseline/
├── README.md
├── main.tf                   # VPC + subnets + flow logs
├── s3.tf                     # Encrypted S3 with public access blocked
├── kms.tf                    # Customer-managed KMS keys
├── iam.tf                    # Roles with least privilege
├── security_groups.tf        # Tight security groups
├── variables.tf
├── outputs.tf
├── versions.tf
└── .checkov.yml              # Checkov configuration
```

## How to use

### As a module source

Reference this as a Terraform module:

```terraform
module "baseline_vpc" {
  source      = "./terraform-baseline"
  environment = "dev"
  app_name    = "my-service"
}
```

### As a scanning target

Run Checkov against this directory:

```bash
cd examples/terraform-baseline
checkov -d . --framework terraform
```

You should see zero CRITICAL / HIGH findings on a clean pass. If Checkov flags a finding, either:

1. The finding is new (Checkov added a rule) — update the code to comply.
2. The finding is a false positive — document with inline suppression and justification.

## What this example intentionally does NOT do

- **Deploy anything.** This is a reference configuration; no `terraform apply` is expected.
- **Include secrets.** All credentials come from environment variables, IAM roles, or SSM parameters — never hardcoded.
- **Cover every AWS service.** This is a baseline; extend it for your use case.

## Common extensions

- Add CloudTrail for API audit logging.
- Add AWS Config rules for continuous compliance.
- Add GuardDuty for threat detection.
- Add WAF v2 for application layer protection.

Each addition should come with Checkov-compliance validation in the same PR.

## Testing changes

```bash
# Format
terraform fmt -check -recursive

# Validate syntax
terraform init -backend=false
terraform validate

# Security scan
checkov -d .

# Policy check (optional, if using OPA)
# conftest test main.tf
```

Wire these into your ASCEND Layer 2 IaC scan job.
