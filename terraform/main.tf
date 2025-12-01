terraform {

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }

  required_version = ">= 1.2"
}


provider "aws" {
  region = "eu-north-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}


resource "aws_instance" "k3s-master" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "m7i-flex.large"
  subnet_id              = aws_subnet.Main.id
  vpc_security_group_ids = [aws_security_group.open_to_the_world.id]
  private_ip             = var.MASTER_A_IP

  user_data = templatefile("${path.module}/scripts/set_first_master.sh",
    {
      AGENT_TOKEN = var.AGENT_TOKEN
  })

  tags = {
    Name = "k3s-master"
  }

}

resource "aws_instance" "k3s-agent" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "m7i-flex.large"
  subnet_id              = aws_subnet.Main.id
  vpc_security_group_ids = [aws_security_group.open_to_the_world.id]

  user_data = templatefile("${path.module}/scripts/set_agents.sh",
    {
      AGENT_TOKEN = var.AGENT_TOKEN
      MASTER_A_IP = var.MASTER_A_IP
  })

  tags = {
    Name = "k3s-agent"
  }
  depends_on = [aws_instance.k3s-master]
}



