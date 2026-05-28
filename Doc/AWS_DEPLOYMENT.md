# Despliegue en AWS — Guía paso a paso

Este documento describe cómo llevar CacaoScan de cero a producción en AWS.

## Arquitectura

```
Usuario
  ├─► app.cacaoscan.app  (CloudFront → S3 frontend Vue)
  └─► api.cacaoscan.app  (ALB HTTPS → ECS Fargate Backend Django+ASGI)
                                          ├─► RDS PostgreSQL 16
                                          ├─► ElastiCache Redis 7
                                          └─► S3 (media/datasets/models)
                          ECS Fargate Celery Worker  ──┘
                          ECS Fargate Celery Beat   ──┘
```

## Prerequisitos

- Cuenta AWS con permisos de admin
- AWS CLI configurado: `aws configure`
- Terraform >= 1.6
- Dominio en Route53 (zona hosted)
- Repo en GitHub (para OIDC)

## Etapa 1 — Bootstrap del backend de Terraform

```bash
export AWS_REGION=us-east-1

aws s3api create-bucket --bucket cacaoscan-tfstate --region $AWS_REGION
aws s3api put-bucket-versioning --bucket cacaoscan-tfstate \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket cacaoscan-tfstate \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws dynamodb create-table --table-name cacaoscan-tflock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region $AWS_REGION
```

## Etapa 2 — Aplicar infra

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars con tu dominio y github_owner

terraform init
terraform plan
terraform apply    # ~15 min (RDS + ElastiCache toman tiempo)
```

Apunta los outputs:

```bash
terraform output
```

Necesitarás:
- `github_actions_role_arn`
- `ecs_cluster_name`
- `frontend_bucket`
- `cloudfront_distribution_id`
- `api_url`

## Etapa 3 — Configurar secrets en GitHub

Repo Settings → Secrets and variables → Actions → New repository secret:

| Secret | Valor |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | output `github_actions_role_arn` |
| `AWS_REGION` | `us-east-1` |
| `ECS_CLUSTER` | output `ecs_cluster_name` |
| `FRONTEND_BUCKET` | output `frontend_bucket` |
| `CLOUDFRONT_DIST_ID` | output `cloudfront_distribution_id` |
| `API_BASE_URL` | `https://api.tudominio.app/api/v1` |

## Etapa 4 — Primera imagen en ECR

Las ECS services arrancan vacíos hasta que pushees la primera imagen.
Push manual desde local (luego CI lo hace automático):

```bash
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

ECR_REGISTRY=$(terraform -chdir=infra/terraform output -json ecr_repositories | jq -r '.backend' | cut -d/ -f1)

# Backend
docker build --target backend --build-arg INSTALL_TRAIN_DEPS=false \
  -t $ECR_REGISTRY/cacaoscan-prod-backend:v1.3.0 backend/
docker push $ECR_REGISTRY/cacaoscan-prod-backend:v1.3.0

# Celery
docker build --target celery --build-arg INSTALL_TRAIN_DEPS=false \
  -t $ECR_REGISTRY/cacaoscan-prod-celery:v1.3.0 backend/
docker push $ECR_REGISTRY/cacaoscan-prod-celery:v1.3.0
```

## Etapa 5 — Migrar base de datos

Corre las migraciones desde una tarea one-off:

```bash
aws ecs run-task \
  --cluster cacaoscan-prod-cluster \
  --task-definition cacaoscan-prod-backend \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx]}" \
  --overrides '{"containerOverrides":[{"name":"backend","command":["python","manage.py","migrate"]}]}'

# Luego seeders
aws ecs run-task ... --overrides \
  '{"containerOverrides":[{"name":"backend","command":["python","manage.py","init_catalogos"]}]}'
aws ecs run-task ... --overrides \
  '{"containerOverrides":[{"name":"backend","command":["python","manage.py","seed_colombia"]}]}'
```

## Etapa 6 — Subir modelos entrenados

Desde Colab (`notebooks/train_cacao_colab.ipynb`) o local:

```bash
aws s3 cp backend/ml/segmentation/cacao_unet.pth \
  s3://cacaoscan-prod-models/v1.0.0/segmentation/cacao_unet.pth
aws s3 cp backend/ml/artifacts/regressors/hybrid.pt \
  s3://cacaoscan-prod-models/v1.0.0/regression/hybrid.pt
```

El backend descarga los modelos en arranque (requiere wiring adicional en `docker-entrypoint.sh`,
ver TODO abajo).

## Etapa 7 — Deploy continuo

Push a `main` → GitHub Actions corre `deploy-aws.yml` → build + push ECR → ECS rolling update + frontend a CloudFront.

Para deploy manual: Actions → `deploy-aws` → Run workflow.

## TODOs pendientes (no resueltos por Terraform)

1. **Bajar modelos en arranque del contenedor**: agregar a `backend/docker-entrypoint.sh`:
   ```bash
   if [ -n "$S3_MODELS_BUCKET" ] && [ -n "$MODELS_VERSION" ]; then
     aws s3 sync "s3://$S3_MODELS_BUCKET/$MODELS_VERSION/" /app/ml/artifacts/ \
       --exclude "*" --include "*.pt" --include "*.pth"
   fi
   ```
   Y agregar `MODELS_VERSION` al `app_env` en `ecs.tf`.

2. **Cambiar Dockerfile a Daphne** o agregar daphne a requirements. El `command` de la
   task de ECS ya invoca `daphne` (ver `ecs.tf`), pero el binario debe existir en la
   imagen. Agregar `daphne==4.1.2` a `requirements.txt`.

3. **Auto-scaling de ECS**: agregar `aws_appautoscaling_target` + policy CPU >70%.

4. **Backups RDS**: ya hay 7 días por defecto; para prod considera snapshots cross-region.

5. **Monitoreo**: CloudWatch alarms para CPU, memoria, errores 5xx del ALB, RDS
   connections. SNS topic para PagerDuty/email.

6. **WAF**: AWS WAF en CloudFront y ALB para rate limiting y reglas OWASP.

## Costos mensuales estimados (us-east-1, baja carga)

| Recurso | $/mes |
|---|---|
| RDS db.t4g.micro single-AZ | ~$13 |
| ElastiCache cache.t4g.micro | ~$11 |
| Fargate 3 tareas (0.5vCPU/1GB c/u) | ~$30 |
| ALB | ~$18 |
| NAT Gateway (1) | ~$32 |
| S3 + CloudFront + ECR | ~$10 |
| Secrets Manager | ~$1 |
| **Total estimado** | **~$115/mes** |

Para reducir:
- Sin NAT (usa VPC Interface Endpoints para ECR/S3/Logs/Secrets) → -$32
- Fargate Spot → -50% del cómputo
- RDS db.t4g.micro siempre que carga lo permita

## Rollback rápido

```bash
# Volver a tag anterior
aws ecs update-service --cluster cacaoscan-prod-cluster --service backend \
  --task-definition cacaoscan-prod-backend:NUMERO_REVISION_ANTERIOR
```
