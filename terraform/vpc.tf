resource "aws_vpc" "locallibary" {
  cidr_block = "10.0.0.0/16"

  tags = {

    Name = "locallibary"
  }
}


resource "aws_security_group" "open_to_the_world" {
  name        = "open-to-the-world"
  description = "Allows all inbound and outbound traffic from 0.0.0.0/0"
  vpc_id      = aws_vpc.locallibary.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Open-K3S-Agent-SG"
  }
}

resource "aws_subnet" "Main" {
  vpc_id     = aws_vpc.locallibary.id
  cidr_block = "10.0.0.0/24"

  tags = {
    Name = "Main"
  }
}
