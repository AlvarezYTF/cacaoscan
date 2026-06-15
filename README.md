# CacaoScan

Plataforma full-stack para el analisis dimensional y de peso de granos de cacao mediante vision por computadora y aprendizaje automatico. Expone una API REST en Django y una SPA en Vue 3 para gestion de fincas, lotes, usuarios y reportes, integrando modelos de segmentacion (U-Net), deteccion (YOLOv8) y regresion hibrida (PyTorch + scikit-learn).

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Stack Tecnologico](#stack-tecnologico)
- [Requisitos](#requisitos)
- [Inicio Rapido con Docker](#inicio-rapido-con-docker)
- [Instalacion Manual](#instalacion-manual)
- [Pipeline de ML/IA](#pipeline-de-mlia)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Endpoints Principales](#endpoints-principales)
- [Testing y Calidad](#testing-y-calidad)
- [Despliegue](#despliegue)
- [Autores](#autores)
- [Licencia](#licencia)

---

## Arquitectura

```
+-------------+        HTTPS/WS         +-------------------+
|  Vue 3 SPA  | <---------------------> |  Django REST API  |
|  (Vite)     |       /api/v1/*         |  + Channels       |
+-------------+                         +---------+---------+
                                                  |
                            +---------------------+---------------------+
                            |                     |                     |
                       +----v-----+         +-----v-----+         +-----v-----+
                       | Postgres |         |   Redis   |         |  Celery   |
                       |    15    |         | (cache/WS)|         | worker+bt |
                       +----------+         +-----------+         +-----------+
                                                                        |
                                                                  +-----v-----+
                                                                  |  ML Stack |
                                                                  | PyTorch / |
                                                                  | YOLOv8 /  |
                                                                  | sklearn   |
                                                                  +-----------+
```

- **Backend (`backend/`)**: Django 5.2 + DRF, montado en `/api/v1/`. Apps: `api`, `auth_app`, `personas`, `fincas_app`, `images_app`, `catalogos`, `reports`, `notifications`, `audit`, `legal`, `training`, `ml`, `core`, `users`.
- **Frontend (`frontend/`)**: Vue 3 + Vite + Pinia + Vue Router + Tailwind v4.
- **Realtime**: Django Channels sobre Redis (`channels_redis`).
- **Tareas asincronas**: Celery worker + beat (activo cuando `USE_CELERY_REDIS=1`).
- **Almacenamiento**: PostgreSQL para datos relacionales; `django-storages` opcional para S3.

---

## Stack Tecnologico

| Capa              | Tecnologia                                                              |
|-------------------|-------------------------------------------------------------------------|
| Backend           | Python 3.12, Django 5.2, Django REST Framework, SimpleJWT, Channels     |
| Base de datos     | PostgreSQL 15                                                           |
| Cache / Broker    | Redis 7                                                                 |
| Tareas asincronas | Celery 5                                                                |
| ML / CV           | PyTorch 2.5, torchvision, Ultralytics YOLOv8, scikit-learn, OpenCV      |
| Frontend          | Vue 3.5, Vite 7, Pinia 3, Vue Router 4, Tailwind CSS 4                  |
| Testing           | pytest, pytest-django, pytest-xdist, Vitest, @vue/test-utils            |
| Infra             | Docker Compose, Kubernetes (Kustomize), Render                          |

---

## Requisitos

| Herramienta | Version |
|-------------|---------|
| Python      | 3.12 (exacto; 3.11 y 3.13 no son compatibles) |
| Node.js     | `^20.19.0` o `>=22.12.0` |
| pnpm        | >= 9 (recomendado sobre npm/yarn) |
| PostgreSQL  | 15+ |
| Redis       | 7+ (opcional para dev sin WS/Celery) |
| Docker      | 24+ con Docker Compose v2 |
| GPU         | Opcional, CUDA 11.8+ acelera entrenamiento |

---

## Inicio Rapido con Docker

Forma recomendada para levantar el stack completo (backend, frontend, Postgres, Redis, Celery).

```bash
git clone https://github.com/tu_usuario/cacaoscan.git
cd cacaoscan
cp env.example .env        # ajustar credenciales si aplica
make up                     # equivalente a: docker compose up -d --build
```

Servicios expuestos:

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1/
- Admin Django: http://localhost:8000/admin/

Comandos utiles:

```bash
make logs                                       # logs en vivo
make down                                       # detener
make clean                                      # detener y borrar volumenes (destruye DB)
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

---

## Instalacion Manual

### Backend

```bash
cd backend
py -3.12 -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
```

Variables de entorno en `backend/.env` (ver `env.example` para la referencia completa):

```env
APP_ENV=development
DEBUG=True
SECRET_KEY=cambia-esta-clave
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Migraciones, seeders y arranque:

```bash
python manage.py migrate
python manage.py init_catalogos
python manage.py seed_colombia
python manage.py createsuperuser
python manage.py runserver
```

API disponible en http://127.0.0.1:8000/api/v1/.

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

SPA disponible en http://127.0.0.1:5173. La URL del backend se configura con `VITE_API_BASE_URL`.

---

## Pipeline de ML/IA

### Preparacion de datos

1. Colocar imagenes en `backend/media/cacao_images/raw/` (formatos: `.bmp`, `.jpg`, `.jpeg`, `.png`, `.tiff`).
2. Copiar el CSV del dataset en `backend/media/datasets/` con la estructura:

   ```
   ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
   510,22.8,16.3,10.2,1.72,510.bmp,cacao_images\raw\510.bmp
   ```

### Ejecucion (en orden)

Los comandos asumen ejecucion dentro del contenedor backend. Para entorno local sustituye `docker compose exec backend` por activar el venv.

**1. Segmentacion U-Net**

```bash
docker compose exec backend python manage.py train_unet_background --epochs 20 --batch-size 16
```

Genera `ml/segmentation/cacao_unet.pth`. Sin GPU usar `--batch-size 4`.

**2. Calibracion de pixeles**

```bash
docker compose exec backend python manage.py calibrate_dataset_pixels --segmentation-backend auto
```

Produce crops sin fondo y `backend/media/datasets/pixel_calibration.json`.

**3. Modelo de regresion hibrido**

```bash
docker compose exec backend python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32
```

Produce `ml/artifacts/regressors/hybrid.pt`. Sin GPU usar `--batch-size 8` o menor.

GPU se detecta automaticamente. Ver opciones completas con `--help`.

---

## Estructura del Proyecto

```
cacaoscan/
├── backend/
│   ├── api/                # REST principal, websockets, realtime
│   ├── auth_app/           # JWT y login
│   ├── personas/           # Perfiles (agricultor, tecnico, admin)
│   ├── fincas_app/         # Fincas y lotes
│   ├── images_app/         # Carga y almacenamiento de imagenes
│   ├── catalogos/          # Datos de referencia
│   ├── reports/            # Excel/PDF
│   ├── notifications/      # Notificaciones
│   ├── audit/              # Auditoria
│   ├── legal/              # Terminos y privacidad
│   ├── training/           # Orquestacion de pipeline ML
│   ├── ml/                 # Segmentation, classification, regression, pipeline
│   ├── core/ users/        # Modelos compartidos
│   ├── cacaoscan/          # settings, urls, asgi, wsgi
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/ components/ stores/ router/ services/
│   │   ├── composables/ utils/ assets/ styles/
│   │   └── test/
│   ├── package.json
│   └── vite.config.js
├── k8s/                    # Manifests Kustomize
├── docker-compose.yml
├── render.yaml
├── Makefile
└── README.md
```

---

## Endpoints Principales

| Endpoint                          | Descripcion                          |
|-----------------------------------|--------------------------------------|
| `POST /api/v1/auth/login/`        | Inicio de sesion (JWT)               |
| `POST /api/v1/auth/refresh/`      | Refresh token                        |
| `GET  /api/v1/fincas/`            | Listado/gestion de fincas            |
| `GET  /api/v1/lotes/`             | Listado/gestion de lotes             |
| `POST /api/v1/images/upload/`     | Carga de imagenes para analisis      |
| `GET  /api/v1/reports/agricultores/` | Reporte Excel de agricultores    |
| `GET  /api/v1/legal/terms/`       | Terminos y condiciones               |
| `GET  /api/v1/legal/privacy/`     | Politica de privacidad               |

Documentacion interactiva (Swagger/OpenAPI) generada por `drf-yasg`.

---

## Testing y Calidad

### Backend

```bash
cd backend
pytest                       # suite completa (--reuse-db --nomigrations)
pytest -n auto               # paralelo (pytest-xdist)
pytest --cov                 # cobertura
pytest api/tests/test_x.py::TestClass::test_method
```

### Frontend

```bash
cd frontend
pnpm test                    # vitest en modo watch
pnpm test:unit               # ejecucion unica + coverage
pnpm lint
pnpm format
```

### Todo en uno

```bash
make test                    # backend + frontend
```

### Analisis estatico

```bash
./run_sonar_full.bat         # SonarQube (config en sonar-project.properties)
```

---

## Despliegue

- **Docker Compose**: `docker-compose.yml` define backend, frontend (nginx), Postgres, Redis, Celery worker y beat.
- **AWS ECS + ECR** (produccion recomendada): push a `main` dispara `.github/workflows/deploy-aws.yml` — construye imagenes, las sube a ECR y actualiza el servicio ECS. Requiere Terraform aplicado previamente (`infra/terraform/`). Ver `Doc/AWS_DEPLOYMENT.md`.
- **Render**: configurado vía `render.yaml`; variables en `RENDER_ENVIRONMENT_VARIABLES.md`.
- **Kubernetes**: manifests Kustomize en `k8s/`. Comandos:

  ```bash
  make deploy           # aplica manifests
  make k8s-status       # estado de pods/services
  make k8s-logs         # logs agregados
  ```

  Namespace por defecto `app-namespace` (override con `K8S_NS=...`).

- **Almacenamiento de imagenes**: S3 en produccion via `django-storages`. En local, `AWS_S3_ENDPOINT_URL` apunta a MinIO para paridad de comportamiento sin cuenta AWS. Ver `Doc/Guia_AWS_S3_Configuracion.md`.

### Variables de entorno clave (v1.4+)

| Variable | Default | Descripcion |
|---|---|---|
| `AWS_S3_ENDPOINT_URL` | _(vacio = S3 real)_ | URL de MinIO para desarrollo local |
| `ML_CLASSIFIER_MIN_CONFIDENCE` | `0.90` | Umbral minimo del clasificador de cacao |
| `ML_YOLO_VALIDATOR_MIN_CONFIDENCE` | `0.75` | Umbral del validador YOLO |
| `ML_YOLO_SEG_CONFIDENCE` | `0.50` | Umbral de segmentacion U-Net |
| `ML_CLASSIFIER_MIN_CACAO_PROBABILITY` | `0.85` | Probabilidad minima de clase cacao |
| `DRF_THROTTLE_ANALYSIS` | `30/min` | Rate limit del endpoint `/scan/` (ML) |
| `DRF_THROTTLE_USER` | `1000/hour` | Rate limit usuarios autenticados |
| `DRF_THROTTLE_ANON` | `60/hour` | Rate limit usuarios anonimos |

---

## Autores

Proyecto desarrollado por aprendices de **Analisis y Desarrollo de Software (ADSO)** — Ficha 2923560, SENA Regional Guaviare.

- Camilo Andres Hernandez Gonzales
- Jeferson Alexander Alvarez Rodriguez
- Deyson De Jesus Urrego Ibarra
- Cristian Camilo Camacho Morales

---

## Licencia

Distribuido bajo licencia MIT. Uso academico y no comercial.

© 2025 CacaoScan.
