output "media_bucket" {
  value = aws_s3_bucket.media.id
}

output "datasets_bucket" {
  value = aws_s3_bucket.datasets.id
}

output "models_bucket" {
  value = aws_s3_bucket.models.id
}

output "ecr_repositories" {
  value = { for k, v in aws_ecr_repository.this : k => v.repository_url }
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "Configura este ARN como secret AWS_DEPLOY_ROLE_ARN en GitHub"
}

output "app_access_key_id" {
  value     = aws_iam_access_key.app.id
  sensitive = true
}

output "app_secret_access_key" {
  value     = aws_iam_access_key.app.secret
  sensitive = true
}
