# infra/outputs.tf
output "app_url" {
  description = "Application URL"
  value       = var.certificate_arn != "" ? "https://${aws_lb.app.dns_name}" : "http://${aws_lb.app.dns_name}"
}

output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}