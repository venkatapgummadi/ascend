# --------------------------------------------------------------------
# Customer-managed KMS keys with rotation — CKV_AWS_7 compliant
# --------------------------------------------------------------------

resource "aws_kms_key" "logs" {
  description             = "${var.app_name} log encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = data.aws_iam_policy_document.logs_kms_policy.json

  tags = { Purpose = "log-encryption" }
}

resource "aws_kms_alias" "logs" {
  name          = "alias/${var.app_name}-${var.environment}-logs"
  target_key_id = aws_kms_key.logs.key_id
}

resource "aws_kms_key" "s3" {
  description             = "${var.app_name} S3 encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = { Purpose = "s3-encryption" }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.app_name}-${var.environment}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "logs_kms_policy" {
  statement {
    sid    = "EnableRootPermissions"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowCloudWatchLogs"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }

    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*",
    ]

    resources = ["*"]
  }
}
