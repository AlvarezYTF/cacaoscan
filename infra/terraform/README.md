# Infra AWS — CacaoScan

Terraform que provisiona el stack completo en AWS.

## Recursos provisionados

- **VPC** (2 AZ): subnets públicas (ALB) + privadas (Fargate, RDS, Redis), NAT Gateway
- **ECR**: 3 repos (`cacaoscan-backend`, `cacaoscan-celery`, `cacaoscan-frontend`)
- **S3**: 3 buckets (`media`, `datasets`, `models`) con versionado
- **RDS**: PostgreSQL 16, single-AZ por defecto (cambia a multi_az=true para prod)
- **ElastiCache Redis**: t4g.micro single node
- **Secrets Manager**: contiene el `.env` de producción
- **ECS Fargate**: cluster + 3 servicios (backend, celery-worker, celery-beat)
- **ALB**: HTTPS con ACM cert (DNS validation en Route53)
- **CloudFront + S3**: frontend estático (Vue build)
- **IAM**: roles task execution + task con permisos S3/Secrets

## Prerequisitos

1. **Cuenta AWS** con credenciales configuradas (`aws configure`)
2. **Dominio en Route53** (o ajusta `acm` para validación manual)
3. **Backend remoto de Terraform** — crea un bucket + tabla DynamoDB para el state:
   ```bash
   aws s3api create-bucket --bucket cacaoscan-tfstate --region us-east-1
   aws s3api put-bucket-versioning --bucket cacaoscan-tfstate \
     --versioning-configuration Status=Enabled
   aws dynamodb create-table --table-name cacaoscan-tflock \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST --region us-east-1
   ```

## Uso

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # ajusta valores
terraform init
terraform plan
terraform apply
```

## Flujo de despliegue

1. `terraform apply` crea infra vacía.
2. GitHub Actions (`deploy-aws.yml`) construye imágenes y las pushea a ECR.
3. ECS hace deployment rolling con la nueva imagen.
4. Frontend: build local → `aws s3 sync` al bucket de CloudFront.

## Costos estimados (us-east-1, carga baja)

| Recurso | $/mes |
|---|---|
| RDS db.t4g.micro single-AZ | ~$13 |
| ElastiCache cache.t4g.micro | ~$11 |
| Fargate 3 tareas 0.5vCPU/1GB | ~$30 |
| ALB | ~$18 |
| NAT Gateway | ~$32 |
| S3 + CloudFront + ECR | ~$10 |
| **Total** | **~$115/mes** |

Para reducir: quita NAT (usa VPC endpoints), apaga Multi-AZ en RDS, usa Fargate Spot.

## Destruir todo

```bash
terraform destroy
```
**Atención**: borra RDS y buckets. Habilita `prevent_destroy` en `s3.tf` si quieres salvaguarda.
