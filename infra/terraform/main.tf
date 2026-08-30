# Google Cloud Terraform infrastructure configuration

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Service Account
resource "google_service_account" "agent_sa" {
  account_id   = "customer-support-agent-sa"
  display_name = "Customer Support Agent Service Account"
}

# 2. Vertex AI User IAM role assignment
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# 3. Secret Manager Secret resource
resource "google_secret_manager_secret" "app_config_secret" {
  secret_id = "customer-support-agent-config"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "secret_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.app_config_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_sa.email}"
}

# 4. Cloud Storage bucket for agent artifacts and session storage
resource "google_storage_bucket" "agent_artifacts" {
  name          = "${var.project_id}-customer-support-artifacts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}
