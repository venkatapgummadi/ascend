output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs."
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs."
  value       = aws_subnet.public[*].id
}

output "data_bucket" {
  description = "S3 bucket for application data."
  value       = aws_s3_bucket.data.id
}

output "app_security_group_id" {
  description = "Application security group ID."
  value       = aws_security_group.app.id
}

output "app_execution_role_arn" {
  description = "IAM role ARN for the application."
  value       = aws_iam_role.app_exec.arn
}

output "s3_kms_key_arn" {
  description = "KMS key ARN for S3 encryption."
  value       = aws_kms_key.s3.arn
  sensitive   = true
}
