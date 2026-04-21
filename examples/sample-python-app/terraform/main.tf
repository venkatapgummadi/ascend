# Minimal AWS infrastructure for the sample Python app.
# Demonstrates a Checkov-compliant Terraform config.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "sample-python-app/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "sample-python-app"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}

# --------------------------------------------------------------------
# VPC with private + public subnets
# --------------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "sample-python-app-vpc" }
}

resource "aws_flow_log" "vpc" {
  iam_role_arn    = aws_iam_role.vpc_flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  name              = "/aws/vpc/sample-python-app"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.logs.arn
}

resource "aws_iam_role" "vpc_flow_log" {
  name_prefix = "vpc-flow-log-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "vpc-flow-logs.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# --------------------------------------------------------------------
# KMS key for log encryption
# --------------------------------------------------------------------
resource "aws_kms_key" "logs" {
  description             = "KMS key for CloudWatch log encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# --------------------------------------------------------------------
# Application S3 bucket (for artifact storage) — hardened
# --------------------------------------------------------------------
resource "aws_s3_bucket" "app_data" {
  bucket = "${var.app_name}-${var.environment}-data"
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.logs.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket                  = aws_s3_bucket.app_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
