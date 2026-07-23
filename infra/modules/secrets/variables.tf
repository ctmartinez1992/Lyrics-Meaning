variable "name_prefix" {
  type = string
}

variable "database_password" {
  type      = string
  sensitive = true
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}
