.PHONY: help build-backend build-frontend build-all up down logs clean

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
DB_DIR = db
REDIS_DIR = redis
CELERY_DIR = celery
K8S_DIR = k8s
NAMESPACE = app-namespace

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========================================
# Docker Compose - Construcción
# ========================================

build-backend: ## Construir imagen del backend
	cd $(BACKEND_DIR) && docker-compose build

build-frontend: ## Construir imagen del frontend
	cd $(FRONTEND_DIR) && docker-compose build

build-all: ## Construir todas las imágenes
	docker-compose build

# ========================================
# Docker Compose - Ejecución
# ========================================

up: ## Levantar todos los servicios
	docker-compose up -d --build

down: ## Detener todos los servicios
	docker-compose down

restart: ## Reiniciar todos los servicios
	docker-compose restart

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-backend: ## Ver logs del backend
	docker-compose logs -f backend

logs-frontend: ## Ver logs del frontend
	docker-compose logs -f frontend

logs-db: ## Ver logs de la base de datos
	docker-compose logs -f db

# ========================================
# Docker Compose - Servicios Individuales
# ========================================

up-backend: ## Levantar solo backend (+ DB + Redis)
	cd $(BACKEND_DIR) && docker-compose up -d --build

up-frontend: ## Levantar solo frontend
	cd $(FRONTEND_DIR) && docker-compose up -d --build

up-db: ## Levantar solo base de datos
	cd $(DB_DIR) && docker-compose up -d

up-redis: ## Levantar solo Redis
	cd $(REDIS_DIR) && docker-compose up -d

up-celery: ## Levantar Celery (Worker + Beat)
	cd $(CELERY_DIR) && docker-compose up -d --build

# ========================================
# Kubernetes - Namespace y Configuración
# ========================================

k8s-namespace: ## Crear namespace
	kubectl apply -f $(K8S_DIR)/namespace.yaml

k8s-config: ## Aplicar configmaps y secrets
	kubectl apply -f $(K8S_DIR)/configmap.yaml
	@echo "⚠️  IMPORTANTE: Revisar y editar secrets antes de aplicar"
	kubectl apply -f $(K8S_DIR)/secrets.yaml

k8s-secrets: ## Aplicar solo secrets
	kubectl apply -f $(K8S_DIR)/secrets.yaml

# ========================================
# Kubernetes - Base de Datos
# ========================================

k8s-deploy-db: ## Desplegar base de datos en K8s
	kubectl apply -f $(DB_DIR)/k8s/pv.yaml
	kubectl apply -f $(DB_DIR)/k8s/pvc.yaml
	kubectl apply -f $(DB_DIR)/k8s/deployment.yaml
	kubectl apply -f $(DB_DIR)/k8s/service.yaml

k8s-deploy-redis: ## Desplegar Redis en K8s
	kubectl apply -f $(REDIS_DIR)/k8s/deployment.yaml
	kubectl apply -f $(REDIS_DIR)/k8s/service.yaml

# ========================================
# Kubernetes - Aplicación
# ========================================

k8s-deploy-backend: ## Desplegar backend en K8s
	kubectl apply -f $(BACKEND_DIR)/k8s/deployment.yaml
	kubectl apply -f $(BACKEND_DIR)/k8s/service.yaml

k8s-deploy-frontend: ## Desplegar frontend en K8s
	kubectl apply -f $(FRONTEND_DIR)/k8s/deployment.yaml
	kubectl apply -f $(FRONTEND_DIR)/k8s/service.yaml

k8s-deploy-celery: ## Desplegar Celery en K8s
	kubectl apply -f $(CELERY_DIR)/k8s/deployment.yaml

k8s-deploy-all: ## Desplegar todos los servicios en K8s
	@echo "📦 Desplegando namespace y configuración..."
	$(MAKE) k8s-namespace
	$(MAKE) k8s-config
	@echo "📦 Desplegando base de datos..."
	$(MAKE) k8s-deploy-db
	$(MAKE) k8s-deploy-redis
	@echo "📦 Desplegando aplicación..."
	$(MAKE) k8s-deploy-backend
	$(MAKE) k8s-deploy-frontend
	$(MAKE) k8s-deploy-celery
	@echo "📦 Desplegando Ingress..."
	kubectl apply -f $(K8S_DIR)/ingress.yaml
	@echo "✅ Despliegue completo!"

# ========================================
# Kubernetes - Usando Kustomize
# ========================================

k8s-kustomize: ## Desplegar usando Kustomize
	kubectl apply -k $(K8S_DIR)/

# ========================================
# Kubernetes - Información y Logs
# ========================================

k8s-status: ## Ver estado de los pods
	kubectl get pods -n $(NAMESPACE)

k8s-services: ## Ver servicios
	kubectl get services -n $(NAMESPACE)

k8s-logs: ## Ver logs de todos los pods
	kubectl logs -f -l app=backend -n $(NAMESPACE) &
	kubectl logs -f -l app=frontend -n $(NAMESPACE)

k8s-logs-backend: ## Ver logs del backend
	kubectl logs -f deployment/backend-deployment -n $(NAMESPACE)

k8s-logs-frontend: ## Ver logs del frontend
	kubectl logs -f deployment/frontend-deployment -n $(NAMESPACE)

k8s-logs-db: ## Ver logs de la base de datos
	kubectl logs -f deployment/db-deployment -n $(NAMESPACE)

k8s-describe: ## Describir recursos en el namespace
	kubectl describe all -n $(NAMESPACE)

# ========================================
# Kubernetes - Limpieza
# ========================================

k8s-clean: ## Eliminar todos los recursos de K8s
	kubectl delete -k $(K8S_DIR)/
	kubectl delete namespace $(NAMESPACE)

k8s-clean-all: ## Limpiar todo (incluyendo PVs)
	$(MAKE) k8s-clean
	kubectl delete pv --all

# ========================================
# Utilidades
# ========================================

clean: ## Limpiar contenedores y volúmenes
	docker-compose down -v
	docker system prune -f

health-check: ## Verificar health checks
	@echo "Backend:"
	@curl -s http://localhost:8000/health || echo "❌ Backend no disponible"
	@echo "\nFrontend:"
	@curl -s http://localhost:5173/health || echo "❌ Frontend no disponible"

rebuild: ## Reconstruir todas las imágenes
	docker-compose build --no-cache
	docker-compose up -d

