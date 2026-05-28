output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "api_url" {
  value = "https://${var.api_subdomain}.${var.domain_name}"
}

output "app_url" {
  value = "https://${var.app_subdomain}.${var.domain_name}"
}

output "ecr_repositories" {
  value = { for k, v in aws_ecr_repository.this : k => v.repository_url }
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.frontend.id
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "models_bucket" {
  value = aws_s3_bucket.models.id
}

output "datasets_bucket" {
  value = aws_s3_bucket.datasets.id
}

output "media_bucket" {
  value = aws_s3_bucket.media.id
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "Configura este ARN como secret AWS_DEPLOY_ROLE_ARN en GitHub"
}

output "db_endpoint" {
  value     = aws_db_instance.main.address
  sensitive = true
}

output "redis_endpoint" {
  value     = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive = true
}
