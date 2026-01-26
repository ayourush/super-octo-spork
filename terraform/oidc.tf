# 1. GitHub as trusted provider
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  # Thumbprint for GitHub Actions
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# 2. Role for GitHub Actions
resource "aws_iam_role" "github_role" {
  name = "github-actions-oidc-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub": "repo:ayourush/super-octo-spork:*"
          }
        }
    }]
  })
}

# 3. Current role permission for tests is AdminAccess, further will be custom limited role (EC2, RDS, SecurityGroups)
resource "aws_iam_role_policy_attachment" "github_admin" {
  role       = aws_iam_role.github_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}