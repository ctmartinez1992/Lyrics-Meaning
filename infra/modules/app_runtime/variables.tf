variable "name_prefix" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "service_security_group_ids" {
  type = list(string)
}
