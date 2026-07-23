resource "aws_secretsmanager_secret" "django" {
  name = "${var.name_prefix}/django"
}

resource "aws_secretsmanager_secret_version" "django" {
  secret_id = aws_secretsmanager_secret.django.id
  secret_string = jsonencode({
    DJANGO_SECRET_KEY = var.django_secret_key
    POSTGRES_PASSWORD = var.database_password
  })
}
