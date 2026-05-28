.PHONY: help build test up down restart logs clean deploy k8s-status k8s-logs k8s-clean seed minio-up minio-console sync-models upload-model

COMPOSE ?= docker compose --env-file .env
PYTHON ?= python3
PNPM ?= pnpm
K8S_NS ?= app-namespace

help: ## Mostrar ayuda general
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

build: ## Construir todas las imágenes usando docker compose
	$(COMPOSE) build

test: ## Ejecutar pruebas backend (pytest) y frontend (pnpm test)
	cd backend && $(PYTHON) -m pip install --upgrade pip && $(PYTHON) -m pip install --no-cache-dir -r requirements.txt && pytest --maxfail=1 --disable-warnings -q
	cd frontend && npm install -g pnpm@8 >/dev/null 2>&1 || true
	cd frontend && $(PNPM) install --frozen-lockfile && $(PNPM) test -- --run

up: ## Levantar el stack completo
	$(COMPOSE) up --build -d

down: ## Detener el stack completo
	$(COMPOSE) down

restart: ## Reiniciar el stack completo
	$(COMPOSE) down
	$(COMPOSE) up --build -d

logs: ## Ver logs combinados
	$(COMPOSE) logs -f

clean: ## Eliminar contenedores y volúmenes locales
	$(COMPOSE) down -v

deploy: ## Aplicar manifiestos Kubernetes con Kustomize
	kubectl apply -k k8s/

k8s-status: ## Mostrar estado de los pods en Kubernetes
	kubectl get pods -n $(K8S_NS)

k8s-logs: ## Logs del backend en Kubernetes
	kubectl logs -f deployment/backend-deployment -n $(K8S_NS)

k8s-clean: ## Eliminar recursos desplegados con Kustomize
	kubectl delete -k k8s/ || true

seed: ## Migraciones + catalogos + Colombia (DB recien creada)
	$(COMPOSE) exec backend python manage.py migrate
	$(COMPOSE) exec backend python manage.py init_catalogos
	$(COMPOSE) exec backend python manage.py seed_colombia

minio-up: ## Levantar solo MinIO + crear buckets
	$(COMPOSE) up -d minio minio_setup

minio-console: ## Abrir consola web de MinIO
	@echo "MinIO console: http://localhost:19001  (user: minioadmin)"

sync-models: ## Descargar modelos desde S3/MinIO a backend/ml/artifacts
	bash scripts/sync_models_from_s3.sh

upload-model: ## Subir modelo a S3/MinIO. Uso: make upload-model SRC=... DST=...
	bash scripts/upload_model_to_s3.sh $(SRC) $(DST)

