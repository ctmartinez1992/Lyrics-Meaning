output "app_task_role_arn" {
  value = aws_iam_role.app_task_role.arn
}

output "worker_task_role_arn" {
  value = aws_iam_role.worker_task_role.arn
}
