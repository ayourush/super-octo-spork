data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_key_pair" "lab_key" {
  key_name   = "aws_lab_key"
  public_key = file("~/.ssh/aws_lab_key.pub")
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh_from_gcp"
  description = "Allow SSH inbound traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.gcp_vm_ip}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web_servers" {
  count         = 2
  ami           = "ami-0fa91bc90632c73c9"
  instance_type = "t3.micro"

  key_name               = aws_key_pair.lab_key.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  tags = {
    Name = "Lab-Server-${count.index + 2}"
  }
}