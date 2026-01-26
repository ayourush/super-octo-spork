# Subnets for RDS
resource "aws_db_subnet_group" "db_subs" {
  name       = "bot_db_subnet_group"
  subnet_ids = data.aws_subnets.default.ids

  tags = { Name = "Bot DB Subnets" }
}

# SG for DB
resource "aws_security_group" "rds_sg" {
  name        = "bot_rds_sg"
  vpc_id      = data.aws_vpc.default.id # VPC var must match with main.tf

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.allow_ssh.id] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Database itself (Free Tier)
resource "aws_db_instance" "bot_db" {
  identifier           = "bot-db"
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.t4g.micro" # Free Tier for eu-north-1
  db_name              = "bot_stats"
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.db_subs.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible  = false
  skip_final_snapshot  = true
}