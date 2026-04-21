# --------------------------------------------------------------------
# Application execution role with least privilege
# --------------------------------------------------------------------

resource "aws_iam_role" "app_exec" {
  name_prefix = "${var.app_name}-${var.environment}-app-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Scoped S3 access — specific bucket, specific actions only
resource "aws_iam_role_policy" "app_s3_access" {
  name_prefix = "${var.app_name}-s3-"
  role        = aws_iam_role.app_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3ReadWrite"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ]
        Resource = ["${aws_s3_bucket.data.arn}/*"]
      },
      {
        Sid    = "S3BucketList"
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.data.arn]
      },
      {
        Sid    = "KMSUse"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
        ]
        Resource = [aws_kms_key.s3.arn]
      },
    ]
  })
}
