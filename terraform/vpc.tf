resource "aws_vpc" "locallibary" {
  cidr_block = "10.0.0.0/16"

  tags = {

    Name = "locallibary"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.locallibary.id

  tags = {
    Name = "main"
  }

}

resource "aws_route_table" "main" {

  vpc_id = aws_vpc.locallibary.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
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
  vpc_id                  = aws_vpc.locallibary.id
  cidr_block              = "10.0.0.0/24"
  map_public_ip_on_launch = true


  tags = {
    Name = "Main"
  }
}

resource "aws_route_table_association" "association_main" {
  subnet_id      = aws_subnet.Main.id
  route_table_id = aws_route_table.main.id
}