output "cluster_arn" {
  value = aws_ecs_cluster.this.arn
}

output "web_log_group" {
  value = aws_cloudwatch_log_group.web.name
}

output "worker_log_group" {
  value = aws_cloudwatch_log_group.worker.name
}
