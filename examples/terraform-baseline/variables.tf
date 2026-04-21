variable "app_name" {
  description = "Application / module name used as a prefix."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,38}$", var.app_name))
    error_message = "app_name must be lowercase, start with a letter, 2-40 chars, alphanumeric and hyphens only."
  }
}

variable "environment" {
  description = "Environment (dev / staging / prod)."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "azs" {
  description = "Availability zones to use (matched to private/public CIDRs by index)."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 365
}
