# 🚀 Guía de Infraestructura Docker + Kubernetes - CacaoScan

Esta guía explica cómo ejecutar y desplegar la infraestructura modular de CacaoScan usando Docker Compose y Kubernetes.

---

## 📁 Estructura del Proyecto

```
project-root/
├── backend/
│   ├── Dockerfile              # Multistage (builder + runtime)
│   ├── docker-compose.yml      # Backend + DB + Redis (desarrollo)
│   ├── .env.example            # Variables de entorno
│   ├── k8s/
│   │   ├── deployment.yaml     # Deployment K8s
│   │   └── service.yaml        # Service K8s
│   └── docker-entrypoint.sh   # Script de inicio
│
├── frontend/
│   ├── Dockerfile              # Multistage (node + nginx)
│   ├── docker-compose.yml      # Frontend (desarrollo)
│   ├── .env.example            # Variables de entorno
│   ├── k8s/
│   │   ├── deployment.yaml     # Deployment K8s
│   │   └── service.yaml        # Service K8s
│   └── nginx.conf              # Configuración Nginx
│
├── db/
│   ├── docker-compose.yml      # PostgreSQL standalone
│   ├── .env.example            # Variables de entorno
│   └── k8s/
│       ├── deployment.yaml     # Deployment K8s
│       ├── service.yaml        # Service K8s
│       ├── pv.yaml             # PersistentVolume
│       └── pvc.yaml             # PersistentVolumeClaim
│
├── redis/
│   ├── docker-compose.yml      # Redis standalone
│   ├── .env.example            # Variables de entorno
│   └── k8s/
│       ├── deployment.yaml     # Deployment K8s
│       └── service.yaml        # Service K8s
│
├── celery/
│   ├── docker-compose.yml      # Celery Worker + Beat
│   ├── .env.example            # Variables de entorno
│   └── k8s/
│       └── deployment.yaml      # Deployments K8s
│
├── k8s/
│   ├── namespace.yaml           # Namespace común
│   ├── configmap.yaml           # ConfigMaps
│   ├── secrets.yaml             # Secrets
│   ├── ingress.yaml             # Ingress (routing)
│   └── kustomization.yaml      # Kustomize
│
├── docker-compose.yml           # Compose global (todos los servicios)
└── Makefile                     # Comandos útiles

```

---

## 🐳 Docker Compose - Ejecución Local

### Opción 1: Ejecutar Servicios por Separado

#### Backend (con DB y Redis)
```bash
cd backend
cp .env.example .env  # Editar valores si es necesario
docker-compose up -d --build
```

#### Frontend
```bash
cd frontend
cp .env.example .env  # Editar valores si es necesario
docker-compose up -d --build
```

#### Base de Datos
```bash
cd db
cp .env.example .env  # Editar valores si es necesario
docker-compose up -d
```

#### Redis
```bash
cd redis
docker-compose up -d
```

#### Celery (Worker + Beat)
```bash
cd celery
cp .env.example .env  # Editar valores si es necesario
docker-compose up -d --build
```

### Opción 2: Ejecutar Todos los Servicios

```bash
# Desde la raíz del proyecto
docker-compose up -d --build
```

**Servicios disponibles:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## ☸️ Kubernetes - Despliegue

### Prerrequisitos

1. **Cluster Kubernetes configurado** (minikube, kind, o cloud provider)
2. **kubectl** instalado y configurado
3. **Ingress Controller** (nginx-ingress recomendado)

### Paso 1: Crear Namespace y Configuración Base

```bash
# Aplicar namespace
kubectl apply -f k8s/namespace.yaml

# Editar secrets antes de aplicar (IMPORTANTE)
# Cambiar contraseñas por defecto en k8s/secrets.yaml
kubectl apply -f k8s/secrets.yaml

# Aplicar configmaps
kubectl apply -f k8s/configmap.yaml
```

### Paso 2: Desplegar Servicios Base

```bash
# Base de datos (con PV/PVC)
kubectl apply -f db/k8s/pv.yaml
kubectl apply -f db/k8s/pvc.yaml
kubectl apply -f db/k8s/deployment.yaml
kubectl apply -f db/k8s/service.yaml

# Redis
kubectl apply -f redis/k8s/deployment.yaml
kubectl apply -f redis/k8s/service.yaml
```

### Paso 3: Desplegar Aplicación

```bash
# Backend
kubectl apply -f backend/k8s/deployment.yaml
kubectl apply -f backend/k8s/service.yaml

# Frontend
kubectl apply -f frontend/k8s/deployment.yaml
kubectl apply -f frontend/k8s/service.yaml

# Celery (opcional)
kubectl apply -f celery/k8s/deployment.yaml
```

### Paso 4: Configurar Ingress

```bash
# Instalar Ingress Controller (si no está instalado)
# Para minikube:
minikube addons enable ingress

# Para kind u otros, seguir documentación del Ingress Controller

# Aplicar Ingress
kubectl apply -f k8s/ingress.yaml
```

### Opción Alternativa: Usar Kustomize

```bash
# Desde la raíz del proyecto
kubectl apply -k k8s/
```

---

## 🔧 Configuración

### Variables de Entorno por Servicio

#### Backend (`.env`)
```env
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432
SECRET_KEY=tu-secret-key-muy-seguro
DEBUG=True
USE_REDIS=True
CELERY_BROKER_URL=redis://redis:6379/0
FRONTEND_URL=http://localhost:5173
```

#### Frontend (`.env`)
```env
VITE_API_BASE_URL=http://backend:8000/api/v1
```

#### Base de Datos (`.env`)
```env
POSTGRES_DB=cacaoscan_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

### Kubernetes Secrets

**⚠️ IMPORTANTE:** Cambiar valores por defecto en `k8s/secrets.yaml` antes de desplegar:

```yaml
stringData:
  DB_PASSWORD: "CHANGE_THIS_PASSWORD"
  SECRET_KEY: "CHANGE_THIS_SECRET_KEY"
  POSTGRES_PASSWORD: "CHANGE_THIS_PASSWORD"
```

Generar secrets en base64:
```bash
echo -n 'tu-password-seguro' | base64
```

---

## 📊 Health Checks

### Endpoints de Health

- **Backend:** `http://localhost:8000/health`
- **Frontend:** `http://localhost:5173/health`

### Verificar Estado en Kubernetes

```bash
# Ver estado de pods
kubectl get pods -n app-namespace

# Ver logs de backend
kubectl logs -f deployment/backend-deployment -n app-namespace

# Ver logs de frontend
kubectl logs -f deployment/frontend-deployment -n app-namespace

# Verificar servicios
kubectl get services -n app-namespace
```

---

## 🛠️ Makefile - Comandos Útiles

El Makefile incluye comandos para facilitar el despliegue:

```bash
# Docker Compose
make build-backend        # Construir solo backend
make build-frontend       # Construir solo frontend
make up                   # Levantar todos los servicios
make down                 # Detener todos los servicios
make logs                 # Ver logs de todos los servicios

# Kubernetes
make k8s-namespace        # Crear namespace
make k8s-config           # Aplicar configmaps y secrets
make k8s-deploy-all       # Desplegar todos los servicios
make k8s-deploy-db        # Desplegar solo base de datos
make k8s-deploy-backend   # Desplegar solo backend
make k8s-deploy-frontend  # Desplegar solo frontend
make k8s-logs             # Ver logs de todos los pods
```

---

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Backend no se conecta a la base de datos

**Verificar:**
- Variables de entorno `DB_HOST`, `DB_USER`, `DB_PASSWORD`
- Servicio de DB está corriendo: `docker ps` o `kubectl get pods`
- En K8s, usar nombre del servicio: `db-service` (no `db`)

#### 2. Frontend no encuentra el backend

**Verificar:**
- Variable `VITE_API_BASE_URL` en `.env` del frontend
- En desarrollo local: `http://localhost:8000/api/v1`
- En Docker Compose: `http://backend:8000/api/v1`
- En K8s: `http://backend-service:8000/api/v1`

#### 3. Volúmenes persistentes en Kubernetes

**Verificar:**
- PV y PVC creados: `kubectl get pv,pvc -n app-namespace`
- Path del host disponible en el nodo: `/data/postgres`
- StorageClass configurado: `local-storage`

---

## 📝 Notas Importantes

1. **Desarrollo vs Producción:**
   - Desarrollo: Usar `.env` locales con valores de desarrollo
   - Producción: Usar Secrets de Kubernetes con valores seguros

2. **Imágenes Docker:**
   - Construir imágenes antes de desplegar en K8s:
   ```bash
   docker build -t cacaoscan-backend:latest ./backend
   docker build -t cacaoscan-frontend:latest ./frontend
   ```

3. **Redes:**
   - Todos los servicios usan la red `cacaoscan_network` en Docker Compose
   - En K8s, los servicios se comunican mediante el namespace `app-namespace`

4. **Health Checks:**
   - Backend: `/health` (retorna `{"status": "ok"}`)
   - Frontend: `/health` (retorna `"healthy"`)

---

## 🚀 Próximos Pasos

- [ ] Configurar CI/CD (GitHub Actions o Jenkins)
- [ ] Agregar monitoreo (Prometheus/Grafana)
- [ ] Configurar autoscaling en K8s
- [ ] Agregar backup automático de PostgreSQL
- [ ] Configurar SSL/TLS en Ingress

