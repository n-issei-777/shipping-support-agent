# Terraform variable definitions

variable "project_id" {
  type        = string
  description = "Google Cloud project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Deployment target Google Cloud region"
}
