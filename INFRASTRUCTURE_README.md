# 🚀 Guía de Infraestructura Segura - CacaoScan

Esta guía describe el nuevo flujo de trabajo para construir, probar y desplegar CacaoScan con Docker Compose y Kubernetes bajo las prácticas reforzadas de seguridad, observabilidad y DevOps.

---

## 📁 Estructura relevante

```
project-root/
├── docker-compose.yml          # Stack completo (backend, frontend, db, redis, celery)
├── backend/
│   ├── Dockerfile              # Builder + runtime + targets backend/celery
│   └── docker-entrypoint.sh    # Control de roles (web/worker/beat)
├── frontend/
│   ├── Dockerfile              # Builder pnpm + nginx unprivileged
│   └── nginx.conf              # Escucha en 8080 con healthcheck
├── k8s/
│   ├── backend-deployment.yaml # Deployment + Service backend (replicas, PVC, securityContext)
│   ├── redis.yaml              # Deployment + Service redis con requirepass
│   ├── media-pvc.yaml          # PersistentVolumeClaim RWX para media
│   ├── redis-pvc.yaml          # PVC de Redis
│   ├── networkpolicy.yaml      # Limita acceso a DB/Redis desde backend y celery
│   ├── configmap.yaml          # Configuración pública
│   ├── secrets.yaml            # Passwords y URLs sensibles (editar antes de usar)
│   ├── ingress.yaml            # HTTPS forzado y CORS restringido
│   ├── kustomization.yaml      # Orquestación Kustomize
│   └── namespace.yaml          # Namespace `app-namespace`
├── db/k8s/                     # Manifiestos actualizados de PostgreSQL (StorageClass estándar)
├── frontend/k8s/               # Despliegues de frontend con puerto 8080
├── celery/k8s/                 # Workers/beat con imagen dedicada
└── .github/workflows/docker-build.yml  # Pipeline CI/CD
```

> 📌 **.env**: crea un fichero en la raíz (`cp backend/env.example .env`) y ajusta contraseñas/hosts antes de levantar servicios o construir imágenes.

---

## 🐳 Docker Compose

1. Copia tu `.env` seguro en la raíz.
2. Ejecuta en caliente:

```bash
docker compose --env-file .env up --build
```

Servicios expuestos sólo en loopback:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`
- PostgreSQL: `127.0.0.1:5432`

Redis permanece dentro de la red privada (`requirepass` obligatorio).

### Makefile

Los comandos clave están pensados para CI/CD y operaciones locales:

```bash
make build        # Construye imágenes locales versionadas
make test         # Ejecuta test unitarios backend + frontend
make up           # docker compose up con --env-file .env
make down         # Detiene y limpia el stack local
make deploy       # kubectl apply -k k8s/
```

---

## ☸️ Kubernetes

1. **Configura secrets** editando `k8s/secrets.yaml` y aplica todo con Kustomize:

```bash
kubectl apply -k k8s/
```

2. Requisitos:
   - StorageClass `standard` (puede mapearse al proveedor cloud o CSI NFS).
   - Ingress controller nginx con certificado TLS (`app-tls`).

3. Características claves:
   - Backend replicas=3 con health/readiness probes.
   - PVC `media-pvc` RWX para ficheros compartidos.
   - Redis con password desde secreto y NetworkPolicy restrictiva.
   - Celery worker/beat con imagen dedicada, `runAsUser 1000` y liveness `celery inspect ping`.

Verifica estado:

```bash
kubectl get pods,svc,ingress,pvc -n app-namespace
```

---

## 🔐 Variables recomendadas (`.env` raíz)

```env
APP_VERSION=v1.3.0

# PostgreSQL
POSTGRES_DB=cacaoscan_db
POSTGRES_USER=cacaoscan
POSTGRES_PASSWORD=define_una_password_fuerte
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
SECRET_KEY=define_un_secret_key_aleatorio
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend,backend-service,app.cacaoscan.com
FRONTEND_URL=https://app.cacaoscan.com
CORS_ALLOWED_ORIGINS=https://app.cacaoscan.com

# Redis
REDIS_PASSWORD=protege_redis
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0

# Frontend
VITE_API_BASE_URL=http://backend:8000/api/v1
```

Replica los valores sensibles dentro de `k8s/secrets.yaml` (recuerda aplicar Base64 si usas `kubectl create secret`).

---

## 🧪 CI/CD (GitHub Actions)

El workflow `.github/workflows/docker-build.yml` realiza:

1. **Tests backend** (`pytest`) con Python 3.11.
2. **Tests frontend** (`pnpm test`).
3. **Build & push** de imágenes versionadas (`backend`, `celery`, `frontend`) hacia GHCR con etiquetas `v1.3.0` y `sha`.
4. **Escaneo Trivy** (HIGH/CRITICAL) sobre cada imagen antes de aprobar el job.

Variables `REGISTRY` y `APP_VERSION` son parametrizables. Para publicar en producción añade `GHCR_PAT` si requieres scope ampliado.

---

## ✅ Checklist operativo

- [x] Imágenes sin root (`appuser` / `nginx` unprivileged / UID 999 para Redis/Postgres).
- [x] Redis protegida con contraseña y sin puerto público.
- [x] Secrets fuera de repositorio (`.env`, `k8s/secrets.yaml`).
- [x] Healthchecks en Compose y Probes en K8s.
- [x] Volúmenes persistentes (`postgres-pvc`, `media-pvc`, `redis-pvc`).
- [x] NetworkPolicy para DB y Redis.
- [x] TLS + CORS limitado en Ingress.
- [x] Pipeline automatizado (tests + build + push + Trivy).

Con esta base puedes extender observabilidad (Prometheus/Grafana), autoscaling (HPA) o backups automatizados sin romper la arquitectura segura establecida.

