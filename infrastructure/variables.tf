variable "project_id" {
  description = "your_project_name"
  type        = string
  default = "your_project_name"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west3"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "europe-west3-a"
}

variable "vpc_network_name" {
  description = "VPC network name"
  type = string
  default = "finitec-vpc-network"
}

variable "firewall_name" {
  description = "Firewall name"
  type = string
  default = "finitec-firewall"
}

variable "web_app_vm_instance_name" {
  description = "Web Application Virtual Machine instance name"
  type = string
  default = "finitec-vm"
}

variable "database_name" {
  description = "Database instance name"
  type        = string
  default     = "my-database"
}

variable  "database_username"  {
  description = "Username to use for the database"
  type        = string
  default = "fastapi_app"
}

variable "database_port" {
  description = "Database port"
  type = string
  default = "5432"
}

variable "environment" {
  description = "Environment of infrastructure"
  type = string
  default = "production"
}