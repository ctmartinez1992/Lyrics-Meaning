resource "aws_ecs_cluster" "this" {
  name = "${var.name_prefix}-cluster"
}

resource "aws_cloudwatch_log_group" "web" {
  name              = "/lyrics-meaning/${var.name_prefix}/web"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/lyrics-meaning/${var.name_prefix}/worker"
  retention_in_days = 14
}

resource "aws_cloudwatch_metric_alarm" "web_5xx" {
  alarm_name          = "${var.name_prefix}-web-5xx"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "5xx spike on web service"
}
