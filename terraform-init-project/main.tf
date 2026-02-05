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
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY

}

resource "aws_s3_bucket" "new_bucket" {
  bucket = var.BUCKET_NAME

}


# variable "secrets_map" {
#   type = map(string)
#   default = {
#     "POSTGRES_DB"    = "locallibrary"
#     "POSTGRES_USER"        = "root"
#     "POSTGRES_PASSWORD"   = "aCYpomL8k*rE4q2pRyiFsnaG"
#     "DATABASE_URL"   = "sk_test_456"
#     "DJANGO_SECRET_KEY"   = "sk_test_456"
#     "DJANGO_DEBUG"   = "sk_test_456"
#     }
# }

# resource "aws_secretsmanager_secret" "multi_secret" {
#   for_each = var.secrets_map
#   name     = "my_app/${each.key}" 
# }

# resource "aws_secretsmanager_secret_version" "multi_version" {
#   for_each      = var.secrets_map
#   secret_id     = aws_secretsmanager_secret.multi_secret[each.key].id
#   secret_string = each.value 
# }
