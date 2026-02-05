variable "SECRET_KEY" {
  type      = string
  sensitive = true
}


variable "ACCESS_KEY" {
  type      = string
  sensitive = true
}

variable "BUCKET_NAME" {
  type = string
  sensitive = false
  
}