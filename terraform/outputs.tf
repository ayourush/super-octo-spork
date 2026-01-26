output "instance_ips" {
  value = aws_instance.web_servers[*].public_ip
}

output "github_role_arn" {
  value = aws_iam_role.github_role.arn
}

output "rds_endpoint" {
  value = aws_db_instance.bot_db.endpoint
}

output "security_group_id" {
  value = aws_security_group.allow_ssh.id
}

output "subnet_ids" {
  value = data.aws_subnets.default.ids
}