resource "random_password" "django_secret" {
  length  = 64
  special = true
}

# Secret unico que el backend lee al arrancar. Cada key se inyecta como
# variable de entorno en la task de ECS (ver ecs.tf -> secrets[]).
resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/app"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY            = random_password.django_secret.result
    DB_HOST               = aws_db_instance.main.address
    DB_PORT               = "5432"
    DB_NAME               = aws_db_instance.main.db_name
    DB_USER               = aws_db_instance.main.username
    DB_PASSWORD           = random_password.db.result
    REDIS_PASSWORD        = random_password.redis.result
    CELERY_BROKER_URL     = "rediss://:${random_password.redis.result}@${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
    CELERY_RESULT_BACKEND = "rediss://:${random_password.redis.result}@${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
  })
}
