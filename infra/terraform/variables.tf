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

variable "github_owner" {
  type        = string
  description = "Owner del repo en GitHub (para OIDC role)"
}

variable "github_repo" {
  type    = string
  default = "cacaoscan"
}
