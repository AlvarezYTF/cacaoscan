resource "aws_security_group" "ecs_tasks" {
  name   = "${local.name}-ecs-sg"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "main" {
  name = "${local.name}-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name}/backend"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "celery" {
  name              = "/ecs/${local.name}/celery"
  retention_in_days = 14
}

# Variables comunes a backend y celery
locals {
  ecr_url_backend = aws_ecr_repository.this["backend"].repository_url
  ecr_url_celery  = aws_ecr_repository.this["celery"].repository_url

  app_env = [
    { name = "APP_ENV", value = "production" },
    { name = "DEBUG", value = "False" },
    { name = "ALLOWED_HOSTS", value = "${var.api_subdomain}.${var.domain_name}" },
    { name = "USE_S3", value = "True" },
    { name = "AWS_STORAGE_BUCKET_NAME", value = aws_s3_bucket.media.id },
    { name = "S3_DATASETS_BUCKET", value = aws_s3_bucket.datasets.id },
    { name = "S3_MODELS_BUCKET", value = aws_s3_bucket.models.id },
    { name = "AWS_S3_REGION_NAME", value = var.region },
    { name = "USE_REDIS", value = "True" },
    { name = "USE_CELERY_REDIS", value = "True" },
    { name = "CORS_ALLOWED_ORIGINS", value = "https://${var.app_subdomain}.${var.domain_name}" },
  ]

  # Estos se montan desde Secrets Manager (cada key del JSON -> env var)
  app_secrets = [
    for k in [
      "SECRET_KEY", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
      "REDIS_PASSWORD", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"
    ] : {
      name      = k
      valueFrom = "${aws_secretsmanager_secret.app.arn}:${k}::"
    }
  ]
}

# ----- Backend (Django + Channels ASGI) -----
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "backend"
    image     = "${local.ecr_url_backend}:${var.image_tag}"
    essential = true
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    environment = local.app_env
    secrets     = local.app_secrets
    # Channels exige ASGI: daphne en vez de gunicorn.
    command = ["daphne", "-b", "0.0.0.0", "-p", "8000", "cacaoscan.asgi:application"]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.backend.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "backend"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "curl -fsS http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 90
    }
  }])
}

resource "aws_ecs_service" "backend" {
  name            = "backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  # CI sobreescribe la image_tag; ignoramos cambios desde TF para no pisar deploys.
  lifecycle {
    ignore_changes = [task_definition]
  }

  depends_on = [aws_lb_listener.https]
}

# ----- Celery worker -----
resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "${local.name}-celery-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.celery_cpu
  memory                   = var.celery_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name        = "celery-worker"
    image       = "${local.ecr_url_celery}:${var.image_tag}"
    essential   = true
    environment = local.app_env
    secrets     = local.app_secrets
    command     = ["celery", "-A", "cacaoscan", "worker", "--loglevel=info", "--concurrency=2", "--max-tasks-per-child=1"]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.celery.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "worker"
      }
    }
  }])
}

resource "aws_ecs_service" "celery_worker" {
  name            = "celery-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  lifecycle { ignore_changes = [task_definition] }
}

# ----- Celery beat (UNA sola replica - nunca escalar) -----
resource "aws_ecs_task_definition" "celery_beat" {
  family                   = "${local.name}-celery-beat"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name        = "celery-beat"
    image       = "${local.ecr_url_celery}:${var.image_tag}"
    essential   = true
    environment = local.app_env
    secrets     = local.app_secrets
    command     = ["celery", "-A", "cacaoscan", "beat", "--loglevel=info"]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.celery.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "beat"
      }
    }
  }])
}

resource "aws_ecs_service" "celery_beat" {
  name            = "celery-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_beat.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  lifecycle { ignore_changes = [task_definition] }
}
