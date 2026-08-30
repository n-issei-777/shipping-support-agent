# Terraform output definitions

output "service_account_email" {
  value       = google_service_account.agent_sa.email
  description = "Service account email address for the agent"
}

output "secret_id" {
  value       = google_secret_manager_secret.app_config_secret.secret_id
  description = "Secret Manager secret ID"
}

output "artifact_bucket_name" {
  value       = google_storage_bucket.agent_artifacts.name
  description = "Cloud Storage bucket name for artifacts"
}
