variable "region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "project" {
  type    = string
  default = "cacaoscan"
}

variable "domain_name" {
  type        = string
  description = "Dominio raiz en Route53 (ej. cacaoscan.app)"
}

variable "api_subdomain" {
  type    = string
  default = "api"
}

variable "app_subdomain" {
  type    = string
  default = "app"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_multi_az" {
  type    = bool
  default = false
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "backend_cpu" {
  type    = number
  default = 512
}

variable "backend_memory" {
  type    = number
  default = 1024
}

variable "celery_cpu" {
  type    = number
  default = 512
}

variable "celery_memory" {
  type    = number
  default = 1024
}

variable "backend_desired_count" {
  type    = number
  default = 1
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "Tag de imagen a desplegar. Override desde CI con github.sha."
}

variable "github_owner" {
  type        = string
  description = "Owner del repo en GitHub (para OIDC role)"
}

variable "github_repo" {
  type    = string
  default = "cacaoscan"
}
