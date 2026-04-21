# --------------------------------------------------------------------
# Security groups — CKV_AWS_23 compliant (no default open ingress/egress)
# --------------------------------------------------------------------

# Default security group locked down — CKV_AWS_23
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id
  # No ingress, no egress rules — default SG is effectively disabled.

  tags = { Name = "${var.app_name}-${var.environment}-default-locked" }
}

# Application security group — explicit ingress/egress only
resource "aws_security_group" "app" {
  name_prefix = "${var.app_name}-${var.environment}-app-"
  description = "Application tier — explicit ingress from LB, egress to DB and S3"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "${var.app_name}-${var.environment}-app" }

  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "app_from_lb" {
  security_group_id            = aws_security_group.app.id
  referenced_security_group_id = aws_security_group.lb.id
  from_port                    = 3000
  to_port                      = 3000
  ip_protocol                  = "tcp"
  description                  = "Allow inbound HTTP from load balancer"
}

resource "aws_vpc_security_group_egress_rule" "app_to_s3" {
  security_group_id = aws_security_group.app.id
  cidr_ipv4         = "0.0.0.0/0"  # S3 VPC endpoint preferred; this for example
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  description       = "HTTPS to S3 and dependent services"
}

# Load balancer security group
resource "aws_security_group" "lb" {
  name_prefix = "${var.app_name}-${var.environment}-lb-"
  description = "Load balancer — public ingress on 443 only"
  vpc_id      = aws_vpc.main.id

  tags = { Name = "${var.app_name}-${var.environment}-lb" }

  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "lb_https" {
  security_group_id = aws_security_group.lb.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  description       = "Public HTTPS"
}

resource "aws_vpc_security_group_egress_rule" "lb_to_app" {
  security_group_id            = aws_security_group.lb.id
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = 3000
  to_port                      = 3000
  ip_protocol                  = "tcp"
  description                  = "Forward to app tier"
}
