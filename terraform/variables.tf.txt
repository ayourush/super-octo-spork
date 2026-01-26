variable "db_username" {
  type    = string
  default = "bot_admin"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "gcp_vm_ip" {
  description = "The static IP of your management VM in GCP"
  type        = string
}